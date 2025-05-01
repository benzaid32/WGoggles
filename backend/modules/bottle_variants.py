"""
Bottle Variants Module for Whisky Goggles

This module provides comprehensive handling of all bottle variants in the BAXUS database.
It contains mappings, patterns, and specialized logic for accurate identification of 
specific bottle variants based on batch codes, product numbers, and other identifiers.
"""

import re
import logging

# Configure logging
logger = logging.getLogger(__name__)

class BottleVariantHandler:
    """
    Handles identification and mapping of specific bottle variants.
    This is a centralized place for all variant detection logic.
    """
    
    def __init__(self):
        """Initialize the bottle variant handler with all variant mappings"""
        # Build all the variant mappings
        self._build_variant_mappings()
    
    def _build_variant_mappings(self):
        """Build all the variant mappings for different bottle families"""
        # Larceny Barrel Proof batch codes
        self.larceny_batch_mapping = {
            # A-series batches
            "A122": "Larceny Barrel Proof A122",
            "A123": "Larceny Barrel Proof A123",
            "A124": "Larceny Barrel Proof A124",
            
            # B-series batches
            "B522": "Larceny Barrel Proof B522",
            "B523": "Larceny Barrel Proof B523",
            "B524": "Larceny Barrel Proof B524",
            
            # C-series batches
            "C921": "Larceny Barrel Proof C921",
            "C922": "Larceny Barrel Proof C924",  # Special case: C922 maps to C924
            "C923": "Larceny Barrel Proof C923",
            "C924": "Larceny Barrel Proof C924",
        }
        
        # Stagg batch/variant mappings
        self.stagg_variant_mapping = {
            # Stagg batch codes
            "22A": "Stagg - 22A",
            "22B": "Stagg Batch 22B",
            "23A": "Stagg - 23A",
            "23C": "Stagg - 23C",
            "24A": "Stagg Batch 24A",
            "24B": "Stagg 24B",
            "24C": "Stagg 24C",
            
            # Special releases
            "2022": "George T. Stagg 2022 Release",
            "2023": "George T. Stagg 2023 Release",
            "2024": "George T. Stagg - 2024",
            
            # Stagg Jr batch numbers
            "BATCH6": "Stagg Jr - Batch 6",
            "BATCH12": "Stagg Jr - Batch 12",
            "BATCH15": "Stagg Jr. Batch 15",
            "BATCH16": "Stagg Jr. - Batch 16",
            "BATCH17": "Stagg Jr. - Batch 17",
            "BATCH18": "Stagg - Batch 18",
        }
        
        # Four Roses variant mappings
        self.four_roses_mapping = {
            # Numeric codes for different expressions
            "46": "Four Roses Single Barrel Straight Bourbon",
            "46.3": "Four Roses Single Barrel Straight Bourbon",
            "46.3A": "Four Roses Single Barrel Straight Bourbon",
            "54": "Four Roses Single Barrel",
            "81-2M": "Four Roses Single Barrel Barrel Proof OESV",
            "812M": "Four Roses Single Barrel Barrel Proof OESV",
            
            # Warehouse codes
            "SN": "Four Roses Single Barrel",
            "W-3A": "Four Roses Single Barrel",
        }
        
        # New Riff variant mappings
        self.new_riff_mapping = {
            "BARREL PROOF": "New Riff Bourbon Single Barrel Barrel Proof",
            "SINGLE BARREL BARREL PROOF": "New Riff Bourbon Single Barrel Barrel Proof",
            "SINGLE BARREL": "New Riff Bourbon Single Barrel",
        }
        
        # Blanton's variant mappings
        self.blantons_mapping = {
            "ORIGINAL": "Blanton's Original Single Barrel",
            "GOLD": "Blanton's Gold Edition",
            "STRAIGHT FROM THE BARREL": "Blanton's Straight from the Barrel",
            "SPECIAL RESERVE": "Blanton's Special Reserve",
            "BLACK": "Blanton's Black",
            "RED": "Blanton's Red",
        }
        
        # E.H. Taylor variant mappings
        self.eh_taylor_mapping = {
            "SMALL BATCH": "E.H. Taylor, Jr. Small Batch",
            "SINGLE BARREL": "E.H. Taylor, Jr. Single Barrel",
            "BARREL PROOF": "Colonel E.H. Taylor Barrel Proof - Batch 12",
            "AMARANTH": "Colonel E.H. Taylor Amaranth",
            "WAREHOUSE C": "Colonel E.H. Taylor Warehouse C",
            "18 YEAR MARRIAGE": "E.H. Taylor, Jr. 18 Year Marriage",
            "STRAIGHT RYE": "E.H. Taylor, Jr. Straight Rye",
        }
        
        # Weller variant mappings
        self.weller_mapping = {
            "ANTIQUE 107": "Weller Antique 107",
            "SPECIAL RESERVE": "Weller Special Reserve",
            "12 YEAR": "Weller 12 Year The Original Wheated Bourbon",
            "FULL PROOF": "Weller Full Proof",
            "SINGLE BARREL": "Weller Single Barrel",
            "C.Y.P.B.": "Weller C.Y.P.B.",
        }
        
        # Elijah Craig variant mappings (especially Barrel Proof batches)
        self.elijah_craig_mapping = {
            "A119": "Elijah Craig Barrel Proof Batch A119",
            "B519": "Elijah Craig Barrel Proof Batch B519",
            "C917": "Elijah Craig Barrel Proof Batch C917",
            "A121": "Elijah Craig Barrel Proof Batch A121",
            "B521": "Elijah Craig Barrel Proof Batch B521",
            "C921": "Elijah Craig Barrel Proof Batch C921",
            "A122": "Elijah Craig Barrel Proof Batch A122",
            "B522": "Elijah Craig Barrel Proof Batch B522",
            "C922": "Elijah Craig Barrel Proof Batch C922",
            "A123": "Elijah Craig Barrel Proof Batch A123",
            "B523": "Elijah Craig Barrel Proof Batch B523",
            "C923": "Elijah Craig Barrel Proof Batch C923",
            "A124": "Elijah Craig Barrel Proof Batch A124",
            "B524": "Elijah Craig Barrel Proof - Batch B524",
            "C924": "Elijah Craig Barrel Proof C924",
            "TOASTED BARREL": "Elijah Craig Toasted Barrel",
            "SMALL BATCH": "Elijah Craig Small Batch",
            "18 YEAR": "Elijah Craig 18 Year Single Barrel",
            "23 YEAR": "Elijah Craig 23 Year Single Barrel",
        }
        
        # Other common variants that need precise identification
        self.other_variants = {
            # Buffalo Trace family
            "BUFFALO TRACE KOSHER RYE": "Buffalo Trace Kosher Rye Recipe",
            "BUFFALO TRACE KOSHER WHEAT": "Buffalo Trace Kosher Wheat Recipe",
            
            # Russell's Reserve variants
            "RUSSELL'S RESERVE 10 YEAR": "Russell's Reserve 10 Year",
            "RUSSELL'S RESERVE 13 YEARS": "Russell's Reserve 13 Years Bourbon", 
            "RUSSELL'S RESERVE SINGLE BARREL": "Russell's Reserve Single Barrel",
            "RUSSELL'S RESERVE 15 YEAR": "Russell's Reserve 15 Year",
            
            # Old Fitzgerald releases by year
            "OLD FITZGERALD 8 YEAR SPRING 2021": "Old Fitzgerald 8 Year - Spring 2021",
            "OLD FITZGERALD 8 YEAR FALL 2023": "Old Fitzgerald 8 Year - Fall 2023",
            "OLD FITZGERALD 10 YEAR": "Old Fitzgerald 10 Year",
            "OLD FITZGERALD 13 YEAR": "Old Fitzgerald 13 Year",
            "OLD FITZGERALD 14 YEAR FALL 2020": "Old Fitzgerald 14 Year - Fall 2020",
            "OLD FITZGERALD 15 YEAR": "Old Fitzgerald 15 Year",
            "OLD FITZGERALD 16 YEAR": "Old Fitzgerald 16 Year",
            "OLD FITZGERALD 17 YEAR": "Old Fitzgerald 17 Year",
            "OLD FITZGERALD 19 YEAR FALL 2022": "Old Fitzgerald 19 Year - Fall 2022",
            
            # Crown Royal variants
            "CROWN ROYAL FINE DE LUXE": "Crown Royal",
            "CROWN ROYAL FINE DE LUXE BLENDED CANADIAN WHISKY": "Crown Royal",
            "CROWN ROYAL BLENDED CANADIAN WHISKY": "Crown Royal",
            
            # Pappy Van Winkle variants
            "PAPPY VAN WINKLE'S FAMILY RESERVE 15 YEAR OLD BOURBON": "Pappy Van Winkle 15 Year Family Reserve",
            "PAPPY VAN WINKLE FAMILY RESERVE 15 YEAR OLD": "Pappy Van Winkle 15 Year Family Reserve",
            "PAPPY VAN WINKLE'S 15 YEAR": "Pappy Van Winkle 15 Year Family Reserve",
            "PAPPY VAN WINKLE 15 YEAR OLD": "Pappy Van Winkle 15 Year Family Reserve",
        }
        
        # Jack Daniel's variant mappings
        self.jack_daniels_mapping = {
            "SINGLE BARREL BARREL PROOF": "Jack Daniel's Single Barrel Barrel Proof",
            "SINGLE BARREL RYE BARREL PROOF": "Jack Daniel's Single Barrel Rye Barrel Proof",
            "SINGLE BARREL RYE": "Jack Daniel's Single Barrel Rye",
            "SINGLE BARREL SELECT": "Jack Daniel's Single Barrel Select",
            "SINATRA SELECT": "Jack Daniel's Sinatra Select",
            "COY HILL BARRELHOUSE 8 2024": "Jack Daniel's Coy Hill Barrelhouse 8 2024 Special Release Single Barrel Whiskey",
            "COY HILL SINGLE BARREL": "Jack Daniel's Coy Hill Single Barrel",
            "10 YEAR": "Jack Daniel's 10 Year",
            "12 YEAR TENNESSEE WHISKEY #1": "Jack Daniel's 12 Year Tennessee Whiskey #1",
            "NO. 27 GOLD MAPLE WOOD FINISH": "Jack Daniel's No. 27 Gold Maple Wood Finish",
            "TRIPLE MASH": "Jack Daniel's Triple Mash",
            "BONDED": "Jack Daniel's Bonded",
            "TWICE BARRELED TENNESSEE RYE 2023": "Jack Daniel's Twice Barreled Tennessee Rye 2023 Special Release",
            "TWICE BARRELED AMERICAN SINGLE MALT 2022": "Jack Daniel's Twice Barreled Special Release 2022 American Single Malt Finished in Oloroso Sherry Casks",
        }
        
        # Knob Creek variant mappings
        self.knob_creek_mapping = {
            "18 YEAR LIMITED EDITION": "Knob Creek 18 Year Limited Edition",
            "15 YEAR BATCH KC001": "Knob Creek 15 Year Batch KC001",
            "15 YEAR": "Knob Creek 15 Year",
            "12 YEAR CASK STRENGTH": "Knob Creek 12 Year Cask Strength",
            "12 YEAR": "Knob Creek 12 Year",
            "9 YEAR SINGLE BARREL RESERVE": "Knob Creek 9 Year Single Barrel Reserve",
            "9 YEAR": "Knob Creek 9 Year",
            "SMOKED MAPLE": "Knob Creek Smoked Maple",
            "RYE": "Knob Creek Rye",
        }
        
        # Eagle Rare variant mappings
        self.eagle_rare_mapping = {
            "17 YEAR": "Eagle Rare 17 Year",
            "10 YEAR": "Eagle Rare 10 Year",
        }
        
        # Booker's variant mappings
        self.bookers_mapping = {
            "NOE STRANGERS BATCH": "Booker's Bourbon 2021-04 Noe Strangers Batch",
            "MIGHTY FINE BATCH": "Booker's Bourbon 2023-03 Mighty Fine Batch",
            "STORYTELLER BATCH": "Booker's Bourbon 2023-04 - The Storyteller Batch",
            "APPRENTICE BATCH": "Booker's 7 Year \"Apprentice Batch\" - 2023",
            "LUMBERYARD BATCH": "Booker's Bourbon 2022-02 Lumberyard Batch",
            "BARDSTOWN BATCH": "Booker's Bourbon 2021-03 Bardstown Batch",
            "SPRINGFIELD BATCH": "Booker's  Springfield Batch 2024-01",
            "BEAM HOUSE BATCH": "Booker's 7 Year \"The Beam House Batch\" - 2024",
            "RONNIE BATCH": "Booker's Bourbon 2022-01 Ronnie's Batch",
            "TAGALONG BATCH": "Booker's 6 Year \"Tagalong Batch\" - 2021",
            "CHARLIE BATCH": "Booker's 2023-01 Charlie's Batch",
            "KENTUCKY TEA BATCH": "Booker's Bourbon 2022-03 Kentucky Tea Batch",
        }
        
        # Maker's Mark variant mappings
        self.makers_mark_mapping = {
            "CELLAR AGED 2024": "Maker's Mark Cellar Aged 2024 Release",
            "CELLAR AGED 2023": "Maker's Mark Cellar Aged 2023 Release",
            "WOOD FINISHING SERIES BEP 2023": "Maker's Mark 2023 Wood Finishing Series BEP",
            "WOOD FINISHING SERIES THE HEART RELEASE 2024": "Maker's Mark Wood Finish Series The Heart Release 2024",
            "WOOD FINISHING SERIES FAE-01 2021": "Maker's Mark 2021 Wood Finishing Series FAE-01",
            "WOOD FINISHING SERIES FAE-02 2021": "Maker's Mark 2021 Wood Finishing Series FAE-02",
            "WOOD FINISHING SERIES BRT-01 2022": "Maker's Mark 2022 Wood Finishing Series BRT-01",
            "WOOD FINISHING SERIES BRT-02 2022": "Maker's Mark 2022 Wood Finishing Series BRT-02",
            "46 CASK STRENGTH": "Maker's Mark 46 Cask Strength",
            "46 FRENCH OAKED": "Maker's Mark French Oaked No. 46 Cask Strength 23-01",
            "46": "Maker's Mark 46",
            "CASK STRENGTH": "Maker's Mark Cask Strength",
            "101": "Maker's Mark 101",
        }
        
        # Old Fitzgerald variant mappings
        self.old_fitzgerald_mapping = {
            "8 YEAR SPRING 2021": "Old Fitzgerald 8 Year - Spring 2021",
            "8 YEAR FALL 2023": "Old Fitzgerald 8 Year - Fall 2023",
            "10 YEAR": "Old Fitzgerald 10 Year",
            "13 YEAR": "Old Fitzgerald 13 Year",
            "14 YEAR FALL 2020": "Old Fitzgerald 14 Year - Fall 2020",
            "15 YEAR": "Old Fitzgerald 15 Year",
            "16 YEAR": "Old Fitzgerald 16 Year",
            "17 YEAR": "Old Fitzgerald 17 Year",
            "19 YEAR FALL 2022": "Old Fitzgerald 19 Year - Fall 2022",
        }
        
        # Michter's variant mappings
        self.michters_mapping = {
            "US*1 TOASTED BARREL FINISH BOURBON": "Michter's Limited Release Toasted Barrel Bourbon",
            "US1 TOASTED BARREL FINISH BOURBON": "Michter's Limited Release Toasted Barrel Bourbon",
            "TOASTED BARREL FINISH BOURBON": "Michter's Limited Release Toasted Barrel Bourbon",
            "TOASTED BARREL BOURBON": "Michter's Limited Release Toasted Barrel Bourbon",
            "LIMITED RELEASE TOASTED BARREL": "Michter's Limited Release Toasted Barrel Bourbon",
            "TOASTED BARREL STRENGTH RYE": "Michter's Toasted Barrel Strength Rye Whiskey",
            "US*1 KENTUCKY STRAIGHT BOURBON": "Michter's US1 Kentucky Straight Bourbon",
            "US1 KENTUCKY STRAIGHT BOURBON": "Michter's US1 Kentucky Straight Bourbon",
            "US*1 KENTUCKY STRAIGHT RYE": "Michter's US1 Kentucky Straight Rye",
            "US1 KENTUCKY STRAIGHT RYE": "Michter's US1 Kentucky Straight Rye",
            "US*1 UNBLENDED AMERICAN WHISKEY": "Michter's US1 Unblended American Whiskey",
            "US1 UNBLENDED AMERICAN WHISKEY": "Michter's US1 Unblended American Whiskey",
            "US*1 TOASTED SOUR MASH": "Michter's US1 Toasted Sour Mash",
            "US1 TOASTED SOUR MASH": "Michter's US1 Toasted Sour Mash",
            "BARREL STRENGTH RYE": "Michter's Barrel Strength Rye Whiskey",
            "10 YEAR SINGLE BARREL BOURBON": "Michter's 10 Year Single Barrel Bourbon 2020 Bottling",
            "10 YEAR BOURBON": "Michter's 10 Year Single Barrel Bourbon 2020 Bottling",
            "SINGLE BARREL RYE 10 YEAR": "Michter's Single Barrel Rye 10 Year",
            "10 YEAR RYE": "Michter's Single Barrel Rye 10 Year",
        }
    
    def get_exact_variant(self, detected_name):
        """
        Get the exact variant name based on the detected bottle name
        
        Args:
            detected_name (str): The detected bottle name from OpenAI
            
        Returns:
            str: The exact BAXUS database name or the original detected name if no match
        """
        if not detected_name:
            return detected_name
            
        # Convert to lowercase for case-insensitive matching
        lower_name = detected_name.lower()
        
        # Check for Larceny Barrel Proof variants
        if "larceny" in lower_name and "barrel proof" in lower_name:
            return self._process_larceny_variant(detected_name)
            
        # Check for Stagg variants
        if "stagg" in lower_name:
            return self._process_stagg_variant(detected_name)
            
        # Check for Four Roses variants
        if "four roses" in lower_name:
            return self._process_four_roses_variant(detected_name)
            
        # Check for New Riff variants
        if "new riff" in lower_name:
            return self._process_new_riff_variant(detected_name)
            
        # Check for Blanton's variants
        if "blanton" in lower_name:
            return self._process_blantons_variant(detected_name)
            
        # Check for E.H. Taylor variants
        if "taylor" in lower_name or "e.h." in lower_name or "e h" in lower_name:
            return self._process_eh_taylor_variant(detected_name)
            
        # Check for Weller variants
        if "weller" in lower_name:
            return self._process_weller_variant(detected_name)
            
        # Check for Elijah Craig variants
        if "elijah craig" in lower_name:
            return self._process_elijah_craig_variant(detected_name)
            
        # Check for Pappy Van Winkle variants
        if "pappy" in lower_name or "van winkle" in lower_name:
            return self._process_pappy_variant(detected_name)
            
        # Check for Jack Daniel's variants
        if "jack daniel" in lower_name or "jack daniels" in lower_name:
            return self._process_jack_daniels_variant(detected_name)
            
        # Check for Knob Creek variants
        if "knob creek" in lower_name:
            return self._process_knob_creek_variant(detected_name)
            
        # Check for Eagle Rare variants
        if "eagle rare" in lower_name:
            return self._process_eagle_rare_variant(detected_name)
            
        # Check for Booker's variants
        if "booker" in lower_name or "bookers" in lower_name:
            return self._process_bookers_variant(detected_name)
            
        # Check for Maker's Mark variants
        if "maker" in lower_name or "makers mark" in lower_name:
            return self._process_makers_mark_variant(detected_name)
            
        # Check for Old Fitzgerald variants
        if "fitzgerald" in lower_name or "old fitz" in lower_name:
            return self._process_old_fitzgerald_variant(detected_name)
            
        # Check for Michter's variants
        if "michter" in lower_name or "michters" in lower_name:
            return self._process_michters_variant(detected_name)
            
        # Check other common variants
        return self._process_other_variants(detected_name)
    
    def _process_larceny_variant(self, detected_name):
        """Process Larceny Barrel Proof variants"""
        # Extract batch code using regex
        batch_match = re.search(r'[abcABC]\d{3}', detected_name)
        if batch_match:
            batch_code = batch_match.group(0).upper()
            if batch_code in self.larceny_batch_mapping:
                logger.info(f"Matched Larceny batch code {batch_code} to {self.larceny_batch_mapping[batch_code]}")
                return self.larceny_batch_mapping[batch_code]
                
        # Default for Larceny Barrel Proof without specific batch
        if "barrel proof" in detected_name.lower():
            return "Larceny Barrel Proof"
            
        return detected_name
    
    def _process_stagg_variant(self, detected_name):
        """Process Stagg variants"""
        lower_name = detected_name.lower()
        
        # Check for George T. Stagg specifically
        if "george t" in lower_name or "george.t" in lower_name or "george t." in lower_name:
            # Look for year in name
            year_match = re.search(r'20(\d{2})', detected_name)
            if year_match:
                year = "20" + year_match.group(1)
                variant = f"George T. Stagg {year} Release"
                logger.info(f"Matched George T. Stagg with year {year} to {variant}")
                return variant
            
            return "George T. Stagg"
        
        # Extract batch codes for regular Stagg
        # First check for 2-digit + letter format (e.g., "22A", "24B")
        batch_match = re.search(r'(\d{2}[a-cA-C])', detected_name)
        if batch_match:
            batch_code = batch_match.group(0).upper()
            if batch_code in self.stagg_variant_mapping:
                logger.info(f"Matched Stagg batch code {batch_code} to {self.stagg_variant_mapping[batch_code]}")
                return self.stagg_variant_mapping[batch_code]
        
        # Check for Stagg Jr with batch number
        if "jr" in lower_name or "junior" in lower_name:
            batch_match = re.search(r'batch\s*(\d+)', lower_name)
            if batch_match:
                batch_num = batch_match.group(1)
                batch_key = f"BATCH{batch_num}"
                if batch_key in self.stagg_variant_mapping:
                    return self.stagg_variant_mapping[batch_key]
                return f"Stagg Jr - Batch {batch_num}"
            
            # Default for Stagg Jr without batch number
            return "Stagg Jr."
            
        # Default for any other Stagg
        return detected_name
    
    def _process_four_roses_variant(self, detected_name):
        """Process Four Roses variants"""
        lower_name = detected_name.lower()
        
        # The "46.3A" or "46" code indicates Single Barrel Straight Bourbon
        if "46.3a" in lower_name or "46.3" in lower_name or re.search(r'\b46\b', lower_name):
            return "Four Roses Single Barrel Straight Bourbon"
            
        # The "81-2M" or similar code indicates Barrel Proof OESV
        if "81-2m" in lower_name or "812m" in lower_name or "oesv" in lower_name:
            return "Four Roses Single Barrel Barrel Proof OESV"
            
        # The "54" code or warehouse codes indicate regular Single Barrel
        if re.search(r'\b54\b', lower_name) or "sn" in lower_name or "w-3a" in lower_name:
            return "Four Roses Single Barrel"
        
        # Also check keyword patterns as fallbacks
        if "straight bourbon" in lower_name:
            return "Four Roses Single Barrel Straight Bourbon"
        elif "barrel proof" in lower_name:
            return "Four Roses Single Barrel Barrel Proof OESV"
        elif "single barrel" in lower_name and "straight" not in lower_name and "barrel proof" not in lower_name:
            return "Four Roses Single Barrel"
            
        # For Four Roses without specific identifiers
        if "small batch" in lower_name:
            if "select" in lower_name:
                return "Four Roses Small Batch Select"
            return "Four Roses Small Batch"
        elif "bourbon" in lower_name and "single" not in lower_name and "small" not in lower_name:
            return "Four Roses Bourbon"
            
        # Default to original name
        return detected_name
    
    def _process_new_riff_variant(self, detected_name):
        """Process New Riff variants"""
        lower_name = detected_name.lower()
        
        # Check for Barrel Proof variant
        if "barrel proof" in lower_name or "cask strength" in lower_name:
            return "New Riff Bourbon Single Barrel Barrel Proof"
            
        # Check for Single Barrel variant (non-barrel proof)
        if "single barrel" in lower_name and "barrel proof" not in lower_name:
            return "New Riff Bourbon Single Barrel"
            
        # Check for regular bourbon variant
        if "bourbon" in lower_name and "single" not in lower_name:
            return "New Riff Bourbon"
            
        # Default to original name
        return detected_name
    
    def _process_blantons_variant(self, detected_name):
        """Process Blanton's variants"""
        lower_name = detected_name.lower()
        
        # Check for specific Blanton's variants
        if "gold" in lower_name:
            return "Blanton's Gold Edition"
        elif "straight from the barrel" in lower_name or "barrel proof" in lower_name:
            return "Blanton's Straight from the Barrel"
        elif "special reserve" in lower_name:
            return "Blanton's Special Reserve"
        elif "black" in lower_name:
            return "Blanton's Black"
        elif "red" in lower_name:
            return "Blanton's Red"
        elif "original" in lower_name or "single barrel" in lower_name:
            return "Blanton's Original Single Barrel"
            
        # Default to Blanton's
        return "Blanton's"
    
    def _process_eh_taylor_variant(self, detected_name):
        """Process E.H. Taylor variants"""
        lower_name = detected_name.lower()
        
        # Check for specific E.H. Taylor variants
        if "small batch" in lower_name:
            return "E.H. Taylor, Jr. Small Batch"
        elif "single barrel" in lower_name:
            return "E.H. Taylor, Jr. Single Barrel"
        elif "barrel proof" in lower_name:
            # Look for batch number
            batch_match = re.search(r'batch\s*(\d+)', lower_name)
            if batch_match and batch_match.group(1) == "12":
                return "Colonel E.H. Taylor Barrel Proof - Batch 12"
            return "Colonel E.H. Taylor Barrel Proof - Batch 6"
        elif "amaranth" in lower_name:
            return "Colonel E.H. Taylor Amaranth"
        elif "warehouse c" in lower_name:
            return "Colonel E.H. Taylor Warehouse C"
        elif "18 year" in lower_name or "18-year" in lower_name:
            return "E.H. Taylor, Jr. 18 Year Marriage"
        elif "straight rye" in lower_name or "rye" in lower_name:
            return "E.H. Taylor, Jr. Straight Rye"
            
        # Default to E.H. Taylor, Jr. Small Batch (most common)
        return "E.H. Taylor, Jr. Small Batch"
    
    def _process_weller_variant(self, detected_name):
        """Process Weller variants"""
        lower_name = detected_name.lower()
        
        # Check for specific Weller variants
        if "antique 107" in lower_name or "107" in lower_name:
            return "Weller Antique 107"
        elif "12 year" in lower_name or "12-year" in lower_name:
            return "Weller 12 Year The Original Wheated Bourbon"
        elif "full proof" in lower_name:
            return "Weller Full Proof"
        elif "single barrel" in lower_name:
            return "Weller Single Barrel"
        elif "c.y.p.b" in lower_name or "cypb" in lower_name:
            return "Weller C.Y.P.B."
        elif "special reserve" in lower_name or "green label" in lower_name:
            return "Weller Special Reserve"
            
        # Default to Weller Special Reserve (most common)
        return "Weller Special Reserve"
    
    def _process_elijah_craig_variant(self, detected_name):
        """Process Elijah Craig variants"""
        lower_name = detected_name.lower()
        
        # Check for Barrel Proof batches using regex
        batch_match = re.search(r'[abcABC]\d{3}', detected_name)
        if batch_match and "barrel proof" in lower_name:
            batch_code = batch_match.group(0).upper()
            if batch_code in self.elijah_craig_mapping:
                return self.elijah_craig_mapping[batch_code]
            return f"Elijah Craig Barrel Proof Batch {batch_code}"
            
        # Check for other Elijah Craig variants
        if "toasted barrel" in lower_name:
            return "Elijah Craig Toasted Barrel"
        elif "small batch" in lower_name:
            return "Elijah Craig Small Batch"
        elif "18 year" in lower_name or "18-year" in lower_name:
            return "Elijah Craig 18 Year Single Barrel"
        elif "23 year" in lower_name or "23-year" in lower_name:
            return "Elijah Craig 23 Year Single Barrel"
        elif "barrel proof" in lower_name:
            return "Elijah Craig Barrel Proof"
            
        # Default to Elijah Craig Small Batch (most common)
        return "Elijah Craig Small Batch"
    
    def _process_pappy_variant(self, detected_name):
        """Process Pappy Van Winkle variants"""
        lower_name = detected_name.lower()
        
        # Check for 15 Year specifically
        if "15" in lower_name or "fifteen" in lower_name:
            return "Pappy Van Winkle 15 Year Family Reserve"
            
        # Other Pappy variants by age
        if "10" in lower_name or "ten" in lower_name:
            return "Old Rip Van Winkle 10 Year"
        elif "12" in lower_name or "twelve" in lower_name:
            return "Van Winkle Special Reserve 12 Year"
        elif "13" in lower_name or "thirteen" in lower_name:
            return "Van Winkle Family Reserve Rye 13 Year"
        elif "20" in lower_name or "twenty" in lower_name:
            return "Pappy Van Winkle 20 Year Family Reserve"
        elif "23" in lower_name or "twenty three" in lower_name or "twenty-three" in lower_name:
            return "Pappy Van Winkle 23 Year Family Reserve"
            
        # Default to returning the detected name if no specific variant is identified
        return detected_name
    
    def _process_jack_daniels_variant(self, detected_name):
        """Process Jack Daniel's variants"""
        lower_name = detected_name.lower()
        
        # Single Barrel variants
        if "single barrel barrel proof" in lower_name:
            return "Jack Daniel's Single Barrel Barrel Proof"
        elif "single barrel" in lower_name and "rye barrel proof" in lower_name:
            return "Jack Daniel's Single Barrel Rye Barrel Proof"
        elif "single barrel" in lower_name and "rye" in lower_name:
            return "Jack Daniel's Single Barrel Rye"
        elif "single barrel" in lower_name and "select" in lower_name:
            return "Jack Daniel's Single Barrel Select"
        elif "single barrel" in lower_name:
            return "Jack Daniel's Single Barrel Select"  # Default single barrel
        
        # Special releases
        if "sinatra" in lower_name:
            return "Jack Daniel's Sinatra Select"
        elif "coy hill" in lower_name:
            if "barrelhouse 8" in lower_name or "2024" in lower_name:
                return "Jack Daniel's Coy Hill Barrelhouse 8 2024 Special Release Single Barrel Whiskey"
            return "Jack Daniel's Coy Hill Single Barrel"
        
        # Age statements
        if "10 year" in lower_name or "10-year" in lower_name:
            return "Jack Daniel's 10 Year"
        elif "12 year" in lower_name or "12-year" in lower_name:
            return "Jack Daniel's 12 Year Tennessee Whiskey #1"
        elif "no. 27" in lower_name or "no 27" in lower_name or "no.27" in lower_name or "gold" in lower_name:
            return "Jack Daniel's No. 27 Gold Maple Wood Finish"
        
        # Other variants
        if "triple mash" in lower_name:
            return "Jack Daniel's Triple Mash"
        elif "bonded" in lower_name:
            return "Jack Daniel's Bonded"
        elif "twice barreled" in lower_name and "rye" in lower_name:
            return "Jack Daniel's Twice Barreled Tennessee Rye 2023 Special Release"
        elif "twice barreled" in lower_name and "single malt" in lower_name:
            return "Jack Daniel's Twice Barreled Special Release 2022 American Single Malt Finished in Oloroso Sherry Casks"
        
        # Regular Jack Daniel's (Old No. 7)
        return "Jack Daniel's"
    
    def _process_knob_creek_variant(self, detected_name):
        """Process Knob Creek variants"""
        lower_name = detected_name.lower()
        
        # Age statements
        if "18 year" in lower_name:
            return "Knob Creek 18 Year Limited Edition"
        elif "15 year" in lower_name:
            if "batch kc001" in lower_name:
                return "Knob Creek 15 Year Batch KC001"
            return "Knob Creek 15 Year"
        elif "12 year" in lower_name:
            if "cask strength" in lower_name:
                return "Knob Creek 12 Year Cask Strength"
            return "Knob Creek 12 Year"
        elif "9 year" in lower_name:
            if "single barrel" in lower_name:
                return "Knob Creek 9 Year Single Barrel Reserve"
            return "Knob Creek 9 Year"
        
        # Single Barrel variants
        if "single barrel" in lower_name and "rye" in lower_name:
            return "Knob Creek Single Barrel Rye"
        elif "single barrel" in lower_name:
            return "Knob Creek 9 Year Single Barrel Reserve"
        
        # Flavored variants
        if "smoked maple" in lower_name:
            return "Knob Creek Smoked Maple"
        
        # Rye variant
        if "rye" in lower_name:
            return "Knob Creek Rye"
        
        # Default to 9 Year
        return "Knob Creek 9 Year"
    
    def _process_eagle_rare_variant(self, detected_name):
        """Process Eagle Rare variants"""
        lower_name = detected_name.lower()
        
        # Age statements
        if "17 year" in lower_name:
            return "Eagle Rare 17 Year"
        elif "10 year" in lower_name:
            return "Eagle Rare 10 Year"
        
        # Default to simply Eagle Rare
        return "Eagle Rare"
    
    def _process_bookers_variant(self, detected_name):
        """Process Booker's variants"""
        lower_name = detected_name.lower()
        
        # Named batch releases
        batch_mappings = {
            "noe strangers": "Booker's Bourbon 2021-04 Noe Strangers Batch",
            "mighty fine": "Booker's Bourbon 2023-03 Mighty Fine Batch",
            "storyteller": "Booker's Bourbon 2023-04 - The Storyteller Batch",
            "apprentice": "Booker's 7 Year \"Apprentice Batch\" - 2023",
            "lumberyard": "Booker's Bourbon 2022-02 Lumberyard Batch",
            "bardstown": "Booker's Bourbon 2021-03 Bardstown Batch",
            "springfield": "Booker's  Springfield Batch 2024-01",
            "beam house": "Booker's 7 Year \"The Beam House Batch\" - 2024",
            "ronnie": "Booker's Bourbon 2022-01 Ronnie's Batch",
            "tagalong": "Booker's 6 Year \"Tagalong Batch\" - 2021",
            "charlie": "Booker's 2023-01 Charlie's Batch",
            "kentucky tea": "Booker's Bourbon 2022-03 Kentucky Tea Batch"
        }
        
        # Check for specific batch names
        for batch_name, mapped_name in batch_mappings.items():
            if batch_name in lower_name:
                return mapped_name
        
        # Check for batch numbers
        batch_match = re.search(r'(20\d{2})[- ](\d{2})', lower_name)
        if batch_match:
            year = batch_match.group(1)
            batch_num = batch_match.group(2)
            return f"Booker's Bourbon {year}-{batch_num}"
        
        # Default to generic Booker's Bourbon
        return "Booker's Bourbon"
    
    def _process_makers_mark_variant(self, detected_name):
        """Process Maker's Mark variants"""
        lower_name = detected_name.lower()
        
        # Limited releases and Wood Finishing Series
        if "cellar aged" in lower_name:
            if "2024" in lower_name:
                return "Maker's Mark Cellar Aged 2024 Release"
            return "Maker's Mark Cellar Aged 2023 Release"
        elif "wood finish" in lower_name or "wood finishing" in lower_name:
            if "bep" in lower_name and "2023" in lower_name:
                return "Maker's Mark 2023 Wood Finishing Series BEP"
            elif "heart" in lower_name and "2024" in lower_name:
                return "Maker's Mark Wood Finish Series The Heart Release 2024"
            elif "fae-01" in lower_name or "fae01" in lower_name:
                return "Maker's Mark 2021 Wood Finishing Series FAE-01"
            elif "fae-02" in lower_name or "fae02" in lower_name:
                return "Maker's Mark 2021 Wood Finishing Series FAE-02"
            elif "brt-01" in lower_name or "brt01" in lower_name:
                return "Maker's Mark 2022 Wood Finishing Series BRT-01"
            elif "brt-02" in lower_name or "brt02" in lower_name:
                return "Maker's Mark 2022 Wood Finishing Series BRT-02"
        
        # Special variants
        if "46" in lower_name:
            if "cask strength" in lower_name:
                return "Maker's Mark 46 Cask Strength"
            if "french oaked" in lower_name or "french oak" in lower_name:
                return "Maker's Mark French Oaked No. 46 Cask Strength 23-01"
            return "Maker's Mark 46"
        elif "cask strength" in lower_name:
            return "Maker's Mark Cask Strength"
        elif "101" in lower_name:
            return "Maker's Mark 101"
        
        # Default to regular Maker's Mark
        return "Maker's Mark Bourbon"
    
    def _process_old_fitzgerald_variant(self, detected_name):
        """Process Old Fitzgerald variants"""
        lower_name = detected_name.lower()
        
        # Age statements with releases
        if "8 year" in lower_name:
            if "spring 2021" in lower_name:
                return "Old Fitzgerald 8 Year - Spring 2021"
            elif "fall 2023" in lower_name:
                return "Old Fitzgerald 8 Year - Fall 2023"
            return "Old Fitzgerald 8 Year - Fall 2023"  # Default to most recent
        elif "10 year" in lower_name:
            return "Old Fitzgerald 10 Year"
        elif "13 year" in lower_name:
            return "Old Fitzgerald 13 Year"
        elif "14 year" in lower_name:
            return "Old Fitzgerald 14 Year - Fall 2020"
        elif "15 year" in lower_name:
            return "Old Fitzgerald 15 Year"
        elif "16 year" in lower_name:
            return "Old Fitzgerald 16 Year"
        elif "17 year" in lower_name:
            return "Old Fitzgerald 17 Year"
        elif "19 year" in lower_name:
            return "Old Fitzgerald 19 Year - Fall 2022"
        
        # Default if no specific match
        return "Old Fitzgerald 8 Year - Fall 2023"  # Default to most recent release
    
    def _process_michters_variant(self, detected_name):
        """Process Michter's variants"""
        lower_name = detected_name.lower()
        
        # Toasted Barrel variants (including the specific batch mentioned)
        if "us*1 toasted barrel" in lower_name or "toasted barrel finish bourbon" in lower_name:
            return "Michter's Limited Release Toasted Barrel Bourbon"
        
        # Specific batch number mentioned by user
        if "18h1393" in lower_name:
            return "Michter's Limited Release Toasted Barrel Bourbon"
            
        # Toasted variants
        if "toasted barrel strength" in lower_name or "toasted barrel rye" in lower_name:
            return "Michter's Toasted Barrel Strength Rye Whiskey"
        elif "toasted barrel" in lower_name or "toasted bourbon" in lower_name:
            return "Michter's Limited Release Toasted Barrel Bourbon"
        elif "toasted sour mash" in lower_name:
            return "Michter's US1 Toasted Sour Mash"
            
        # 10 Year variants
        if "10 year" in lower_name and "rye" in lower_name:
            return "Michter's Single Barrel Rye 10 Year"
        elif "10 year" in lower_name or "10-year" in lower_name:
            return "Michter's 10 Year Single Barrel Bourbon 2020 Bottling"
            
        # Barrel Strength variant
        if "barrel strength" in lower_name and "rye" in lower_name:
            return "Michter's Barrel Strength Rye Whiskey"
            
        # US1 variants
        if "us1" in lower_name or "us*1" in lower_name:
            if "rye" in lower_name:
                return "Michter's US1 Kentucky Straight Rye"
            elif "unblended" in lower_name or "american whiskey" in lower_name:
                return "Michter's US1 Unblended American Whiskey" 
            elif "sour mash" in lower_name:
                return "Michter's US1 Toasted Sour Mash"
            else:
                return "Michter's US1 Kentucky Straight Bourbon"
                
        # Default to the most common variant
        return "Michter's US1 Kentucky Straight Bourbon"
    
    def _process_other_variants(self, detected_name):
        """Process other common variants"""
        # First try exact match using the dictionary
        for variant_name, baxus_name in self.other_variants.items():
            if detected_name.upper() == variant_name:
                return baxus_name
                
        # For "Crown Royal" specifically, check if it contains these words
        if "crown royal" in detected_name.lower():
            if "fine de luxe" in detected_name.lower() or "blended canadian" in detected_name.lower():
                return "Crown Royal"
                
        # Try more flexible matching for other variants
        lower_name = detected_name.lower()
        for variant_name, baxus_name in self.other_variants.items():
            if variant_name.lower() in lower_name:
                return baxus_name
        
        return detected_name
