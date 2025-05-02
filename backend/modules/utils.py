"""
Utility functions for Whisky Goggles.
"""
import logging
import base64
from PIL import Image
import io

logger = logging.getLogger(__name__)

def encode_image(image):
    """Encode PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def decode_image(image_data):
    """Decode image from various formats to PIL Image."""
    try:
        # If it's already a PIL Image
        if isinstance(image_data, Image.Image):
            return image_data
        
        # If it's a base64 string
        if isinstance(image_data, str):
            # Check if it's a data URL
            if image_data.startswith('data:image'):
                # Extract the base64 part
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            return Image.open(io.BytesIO(image_bytes))
            
        # If it's raw bytes
        if isinstance(image_data, bytes):
            return Image.open(io.BytesIO(image_data))
            
        # If it's a file-like object
        if hasattr(image_data, 'read'):
            return Image.open(image_data)
            
        raise ValueError("Unsupported image format")
        
    except Exception as e:
        logger.error(f"Error decoding image: {str(e)}")
        return None

def format_json_response(success, message=None, data=None, error=None):
    """Format a consistent JSON response."""
    response = {
        "success": success
    }
    
    if message:
        response["message"] = message
    
    if data:
        response["data"] = data
    
    if error:
        response["error"] = error
    
    return response
