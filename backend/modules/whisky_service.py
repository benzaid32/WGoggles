"""
Whisky Goggles - Unified Whisky Recognition Service
This consolidated module handles all whisky recognition, matching, and pricing functions
"""
import os
import logging
import json
import re
import base64
import sqlite3
import traceback
from datetime import datetime
from openai import OpenAI
from modules import config
from modules.bottle_variants import BottleVariantHandler
from fuzzywuzzy import fuzz

# Configure logging
logger = logging.getLogger(__name__)

class WhiskyService:
    """Unified service for whisky recognition and pricing"""
    
    def __init__(self):
        """Initialize the whisky service with required paths and data"""
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(self.root_dir, 'data', 'db', 'baxus.db')
        self.annotations_dir = os.path.join(self.root_dir, 'data', 'bottle_annotations')
        
        # Create the bottle annotations directory if it doesn't exist
        if not os.path.exists(self.annotations_dir):
            try:
                os.makedirs(self.annotations_dir)
                logger.info(f"Created directory: {self.annotations_dir}")
            except Exception as e:
                logger.error(f"Error creating directory {self.annotations_dir}: {e}")
        
        # Cache for bottle data
        self._baxus_bottles = []
        self._annotation_bottles = []
        self._name_mapping = {}
        self._bottle_cache = {}
        self._batch_code_mapping = {}  # Map batch codes to exact bottle names
        self._brand_variants = {}      # Map brands to their variant names
        
        # Initialize the bottle variant handler
        self.variant_handler = BottleVariantHandler()
        
        # Load data on initialization
        self._load_bottle_data()
        
        # Build variant mapping from annotations
        self._build_variant_mapping()
    
    def recognize_bottle(self, image_data, api_key):
        """
        Unified bottle recognition method
        
        Args:
            image_data (str): Base64-encoded image data
            api_key (str): OpenAI API key
            
        Returns:
            dict: Detected bottle information with pricing
        """
        try:
            # Step 1: Detect bottle using vision API
            detected_bottle = self._detect_bottle_from_image(image_data, api_key)
            if not detected_bottle:
                return None
                
            # Step 2: Match to exact BAXUS database name
            baxus_name = self._match_to_baxus(detected_bottle)
            if not baxus_name:
                # Use the detected name if no match found
                baxus_name = detected_bottle
                
            # Step 3: Get pricing data
            pricing_data = self.get_bottle_pricing(baxus_name)
            
            # Step 4: Build complete result
            result = {
                "name": self._clean_bottle_name(baxus_name),  # Exact BAXUS name, clean any file extensions
                "detected_name": self._clean_bottle_name(detected_bottle),  # Original detected name
                "confidence": 0.95,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add pricing data if available
            if pricing_data:
                result.update({
                    "fair_market_price": self._format_price(pricing_data.get('fair_price')),
                    "msrp": self._format_price(pricing_data.get('avg_msrp')),
                    "shelf_price": self._format_price(pricing_data.get('shelf_price')),
                    "proof": pricing_data.get('proof'),
                    "abv": f"{pricing_data.get('abv')}%" if pricing_data.get('abv') else None,
                    "size": f"{pricing_data.get('size')}ml" if pricing_data.get('size') else None,
                    "popularity_rank": pricing_data.get('ranking'),
                    "community_rating": pricing_data.get('total_score')
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in bottle recognition: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def _detect_bottle_from_image(self, image_data, api_key):
        """
        Detect whisky bottle in image using OpenAI Vision API
        
        Args:
            image_data (str): Base64-encoded image data
            api_key (str): OpenAI API key
            
        Returns:
            str: Detected bottle name or None
        """
        try:
            # Initialize the OpenAI client with the API key
            client = OpenAI(api_key=api_key)
            
            # System and user prompts for optimal bottle detection
            system_prompt = ("You are a whisky identification expert. Identify whisky bottles with extreme precision. "
                            "Only identify bottles that are genuinely in the image. Accuracy is critical.")
            
            user_prompt = (
                "Identify the whisky bottle visible in this image. "
                "Provide the complete and exact brand and product name. "
                "Only identify whisky - no other spirits or products. "
                "Be as specific as possible and include any visible batch numbers, years, or special editions. "
                "For example: 'Larceny Barrel Proof Batch B522', 'George T. Stagg 2022 Release', or 'Stagg - 22A'. "
                "Only respond with the bottle name, nothing else. Do not include file extensions or image names."
            )
            
            # Make the API request with the new client
            logger.info("Making OpenAI Vision API request...")
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]}
                ],
                max_tokens=300
            )
            
            # Process the response (structure has changed in the new API)
            if response and hasattr(response, 'choices') and response.choices and hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                content = response.choices[0].message.content.strip()
                
                # Clean up the bottle name - remove file extensions
                content = self._clean_bottle_name(content)
                
                logger.info(f"OpenAI detected: {content}")
                return content
            else:
                logger.error(f"Unexpected response format from OpenAI: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error in bottle detection: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def _clean_bottle_name(self, bottle_name):
        """
        Clean up the detected bottle name by removing file extensions and other unwanted elements
        
        Args:
            bottle_name (str): The detected bottle name
            
        Returns:
            str: Cleaned bottle name
        """
        if not bottle_name:
            return bottle_name
            
        # Remove common file extensions
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        cleaned_name = bottle_name
        
        for ext in extensions:
            if cleaned_name.lower().endswith(ext.lower()):
                cleaned_name = cleaned_name[:-len(ext)]
                logger.info(f"Removed file extension {ext} from bottle name")
        
        # Remove "image" or "filename" text if present
        prefixes_to_remove = ["image of ", "image: ", "filename: ", "file: "]
        for prefix in prefixes_to_remove:
            if cleaned_name.lower().startswith(prefix.lower()):
                cleaned_name = cleaned_name[len(prefix):]
                logger.info(f"Removed prefix '{prefix}' from bottle name")
        
        # Apply specialized bottle variant handling using the variant handler
        cleaned_name = self.variant_handler.get_exact_variant(cleaned_name)
        
        return cleaned_name.strip()
    
    def _build_variant_mapping(self):
        """
        Build a comprehensive mapping of bottle variants from annotations
        This creates mappings for batch codes and brand variants
        """
        if not self._annotation_bottles:
            logger.warning("No annotation bottles available to build variant mapping")
            return
            
        logger.info("Building comprehensive bottle variant mapping...")
        
        # Extract all batch codes from annotations
        batch_pattern = re.compile(r'[abc][0-9]{3}', re.IGNORECASE)
        
        # Special case for collision handling
        batch_code_collisions = {}
        
        for bottle_name in self._annotation_bottles:
            # Look for batch codes
            match = batch_pattern.search(bottle_name.lower())
            if match:
                batch_code = match.group(0).upper()
                
                # Handle batch code collisions by brand
                if batch_code in self._batch_code_mapping:
                    # We have a collision
                    if batch_code not in batch_code_collisions:
                        batch_code_collisions[batch_code] = [self._batch_code_mapping[batch_code]]
                    batch_code_collisions[batch_code].append(bottle_name)
                    
                    # Remove from regular mapping until we resolve the collision
                    logger.warning(f"Batch code collision for {batch_code}: {self._batch_code_mapping[batch_code]} vs {bottle_name}")
                else:
                    self._batch_code_mapping[batch_code] = bottle_name
                    logger.debug(f"Added batch code mapping: {batch_code} -> {bottle_name}")
            
            # Build brand variant mapping
            parts = bottle_name.split()
            if len(parts) >= 2:
                # Use first two words as brand key (e.g., "Elijah Craig", "Larceny Barrel")
                brand_key = " ".join(parts[:2]).lower()
                if brand_key not in self._brand_variants:
                    self._brand_variants[brand_key] = []
                self._brand_variants[brand_key].append(bottle_name)
        
        # Resolve batch code collisions by creating brand-specific mappings
        for batch_code, bottles in batch_code_collisions.items():
            # Create brand-specific batch code mappings
            for bottle in bottles:
                # Extract brand
                parts = bottle.split()
                if len(parts) >= 2:
                    brand = parts[0].lower()  # First word as brand
                    
                    # Create a brand-specific batch code key
                    brand_batch_key = f"{brand}_{batch_code}".upper()
                    self._batch_code_mapping[brand_batch_key] = bottle
                    logger.info(f"Created brand-specific batch mapping: {brand_batch_key} -> {bottle}")
        
        logger.info(f"Built variant mapping with {len(self._batch_code_mapping)} batch codes and {len(self._brand_variants)} brand variants")
        
        # Log some sample batch code mappings for verification
        sample_batch_codes = list(self._batch_code_mapping.keys())[:10]
        for code in sample_batch_codes:
            logger.debug(f"Sample batch mapping: {code} -> {self._batch_code_mapping[code]}")
    
    def _match_to_baxus(self, detected_bottle_name):
        """
        Match the detected bottle name to the BAXUS database using fuzzy matching
        
        Args:
            detected_bottle_name (str): The detected bottle name
            
        Returns:
            str: The matched BAXUS bottle name or the original detected name if no match is found
        """
        if not detected_bottle_name:
            return detected_bottle_name
            
        # Clean the name first using our variant handler
        cleaned_name = self._clean_bottle_name(detected_bottle_name)
        
        # Try exact match first (most reliable)
        if cleaned_name in self._baxus_bottles:
            logger.info(f"Found exact match in BAXUS: {cleaned_name}")
            return cleaned_name
            
        # Try case-insensitive match
        for bottle in self._baxus_bottles:
            if cleaned_name.lower() == bottle.lower():
                logger.info(f"Found case-insensitive match in BAXUS: {bottle}")
                return bottle
                
        # Try fuzzy matching with multiple approaches for better accuracy
        matches = []
        
        # Method 1: Token Set Ratio (good for different word ordering)
        for bottle in self._baxus_bottles:
            ratio = fuzz.token_set_ratio(cleaned_name.lower(), bottle.lower())
            matches.append((bottle, ratio))
            
        # Method 2: Partial Ratio (good for substring matches)
        partial_matches = []
        for bottle in self._baxus_bottles:
            ratio = fuzz.partial_ratio(cleaned_name.lower(), bottle.lower())
            partial_matches.append((bottle, ratio))
            
        # Method 3: Token Sort Ratio (good for different word ordering)
        sort_matches = []
        for bottle in self._baxus_bottles:
            ratio = fuzz.token_sort_ratio(cleaned_name.lower(), bottle.lower())
            sort_matches.append((bottle, ratio))
            
        # Combine scores with weightings (token_set has proven most effective)
        final_matches = []
        for i, bottle in enumerate(self._baxus_bottles):
            token_set_score = matches[i][1] * 0.5  # 50% weight
            partial_score = partial_matches[i][1] * 0.3  # 30% weight
            sort_score = sort_matches[i][1] * 0.2  # 20% weight
            final_score = token_set_score + partial_score + sort_score
            final_matches.append((bottle, final_score))
        
        # Sort by score (highest first)
        final_matches.sort(key=lambda x: x[1], reverse=True)
        
        # Debug: Log the top 3 matches to help understand the matching
        for i, (bottle, score) in enumerate(final_matches[:3]):
            logger.info(f"Match #{i+1}: {bottle} (score: {score:.2f})")
            
        # Get the best match if the score is above the threshold
        best_match, best_score = final_matches[0]
        
        # Higher threshold (95) for more reliable matches
        if best_score >= 95:
            logger.info(f"Found high-confidence fuzzy match: {best_match} (score: {best_score:.2f})")
            return best_match
            
        # For scores between 90-95, verify it's not a false positive by checking 
        # that the second best match isn't too close
        if best_score >= 90:
            if len(final_matches) > 1:
                second_best = final_matches[1][1]
                # If the top match is significantly better than the second match
                if best_score - second_best >= 5:
                    logger.info(f"Found confident fuzzy match: {best_match} (score: {best_score:.2f})")
                    return best_match
                    
        # If we still don't have a match, try checking if the brand name is in our database
        # and use the most common variant of that brand
        brand_name = cleaned_name.split(' ')[0].lower()
        brand_matches = [bottle for bottle in self._baxus_bottles if bottle.lower().startswith(brand_name.lower())]
        
        if brand_matches:
            # Sort by commonality (shorter names tend to be more common/core expressions)
            brand_matches.sort(key=len)
            logger.info(f"Using brand match: {brand_matches[0]}")
            return brand_matches[0]
                
        # No good match found, use our variant handler for a final attempt at mapping
        # and if that fails, return the original cleaned name
        logger.info(f"No good match found in BAXUS for: {cleaned_name}")
        return cleaned_name
    
    def _string_similarity(self, a, b):
        """
        Calculate simple string similarity without external libraries
        Uses a basic Jaccard similarity approach with character bigrams
        
        Args:
            a (str): First string
            b (str): Second string
            
        Returns:
            float: Similarity score between 0 and 1
        """
        # Create character bigrams for each string
        def get_bigrams(s):
            return set(s[i:i+2] for i in range(len(s)-1))
            
        bigrams_a = get_bigrams(a)
        bigrams_b = get_bigrams(b)
        
        # Calculate Jaccard similarity
        if not bigrams_a or not bigrams_b:
            return 0
            
        intersection = len(bigrams_a.intersection(bigrams_b))
        union = len(bigrams_a.union(bigrams_b))
        
        return intersection / union if union > 0 else 0
    
    def _normalize_bottle_name(self, name):
        """
        Normalize a bottle name for better matching
        
        Args:
            name (str): Bottle name to normalize
            
        Returns:
            str: Normalized name
        """
        if not name:
            return ""
            
        # Convert to lowercase
        normalized = name.lower()
        
        # Remove common filler words
        fillers = ["whisky", "whiskey", "bourbon", "scotch", "single malt", "batch", "release"]
        for filler in fillers:
            normalized = normalized.replace(filler, "")
            
        # Normalize spaces
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def get_bottle_pricing(self, bottle_name):
        """
        Get pricing data for a bottle directly from the SQLite database
        
        Args:
            bottle_name (str): Exact BAXUS bottle name
            
        Returns:
            dict: Pricing data or None if not found
        """
        if not bottle_name:
            return None
            
        # Try cache first
        if bottle_name in self._bottle_cache:
            return self._bottle_cache[bottle_name]
            
        try:
            # Connect to database
            if not os.path.exists(self.db_path):
                logger.error(f"Database not found: {self.db_path}")
                return None
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query for exact bottle
            query = "SELECT * FROM whisky_bottles WHERE name = ? COLLATE NOCASE"
            cursor.execute(query, (bottle_name,))
            result = cursor.fetchone()
            
            if not result:
                # Try simple matching if exact match fails
                query = "SELECT name FROM whisky_bottles"
                cursor.execute(query)
                all_bottles = [row[0] for row in cursor.fetchall()]
                
                # Use our simple string similarity
                best_match = None
                highest_score = 0
                
                for b in all_bottles:
                    score = self._string_similarity(bottle_name.lower(), b.lower())
                    if score > highest_score and score > 0.75:
                        highest_score = score
                        best_match = b
                
                if best_match:
                    logger.info(f"String matched '{bottle_name}' to database entry '{best_match}'")
                    
                    # Query using the matched name
                    query = "SELECT * FROM whisky_bottles WHERE name = ? COLLATE NOCASE"
                    cursor.execute(query, (best_match,))
                    result = cursor.fetchone()
            
            if result:
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Create dict from result
                bottle_data = dict(zip(columns, result))
                
                # Format fields
                for key in bottle_data:
                    if bottle_data[key] == "NULL" or bottle_data[key] == "":
                        bottle_data[key] = None
                
                # Cache for future use
                self._bottle_cache[bottle_name] = bottle_data
                return bottle_data
            else:
                logger.warning(f"No pricing data found for bottle: {bottle_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving bottle pricing: {str(e)}")
            logger.error(traceback.format_exc())
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _format_price(self, price):
        """
        Format a price value with dollar sign
        
        Args:
            price: Price value (float, int, or string)
            
        Returns:
            str: Formatted price or None
        """
        if price is None:
            return None
            
        try:
            # Convert to float and format with dollar sign
            float_price = float(price)
            return f"${float_price:.2f}"
        except (ValueError, TypeError):
            # Return original value if conversion fails
            return price
    
    def get_roboflow_metadata(self):
        """
        Get metadata about the available annotations
        Used by the database_info endpoint
        
        Returns:
            list: Available bottle annotations
        """
        return self._annotation_bottles
    
    def _load_bottle_data(self):
        """Load all bottle data from annotations and database"""
        # Load bottles from SQLite database
        try:
            if os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM whisky_bottles")
                self._baxus_bottles = [row[0] for row in cursor.fetchall()]
                conn.close()
                logger.info(f"Loaded {len(self._baxus_bottles)} bottles from BAXUS database")
            else:
                logger.warning(f"BAXUS database not found: {self.db_path}")
                # Fallback - try to load from CSV
                csv_path = os.path.join(self.root_dir, 'data', 'baxus_whisky_database.csv')
                if os.path.exists(csv_path):
                    with open(csv_path, 'r') as f:
                        # Skip header
                        next(f)
                        self._baxus_bottles = [line.strip().split(',')[0] for line in f if line.strip()]
                    logger.info(f"Loaded {len(self._baxus_bottles)} bottles from CSV fallback")
        except Exception as e:
            logger.error(f"Error loading BAXUS bottles: {str(e)}")
            logger.error(traceback.format_exc())
            
        # Load bottles from annotations
        try:
            if os.path.exists(self.annotations_dir):
                annotation_files = [f for f in os.listdir(self.annotations_dir) if f.endswith('.json')]
                for file in annotation_files:
                    try:
                        with open(os.path.join(self.annotations_dir, file), 'r') as f:
                            data = json.load(f)
                            if 'name' in data:
                                self._annotation_bottles.append(data['name'])
                    except Exception as e:
                        logger.error(f"Error loading annotation file {file}: {str(e)}")
                logger.info(f"Loaded {len(self._annotation_bottles)} bottles from annotations")
            else:
                logger.warning(f"Bottle annotations directory not found: {self.annotations_dir}")
        except Exception as e:
            logger.error(f"Error loading bottle annotations: {str(e)}")
            logger.error(traceback.format_exc())
