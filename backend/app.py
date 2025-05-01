"""
Flask API for Whisky Goggles.
Uses OpenAI's GPT-4o vision model to identify whisky bottles.
"""

import os
import sys
import json
import base64
import logging
import traceback
import openai
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from modules import config
from modules.whisky_service import WhiskyService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"], "methods": ["GET", "POST", "OPTIONS"]}})

# Initialize Whisky Recognition Service
whisky_service = WhiskyService()

# OpenAI API key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    # Try loading from direct key file
    try:
        with open('direct_key.env', 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY'):
                    OPENAI_API_KEY = line.split('=', 1)[1].strip()
    except Exception as e:
        app.logger.error(f"Failed to load API key: {e}")

# Routes

@app.route("/")
def home():
    """Home endpoint."""
    return jsonify({
        "name": "Whisky Goggles API",
        "description": "REST API for Whisky Goggles using OpenAI's GPT-4o vision model",
        "version": "1.0.0",
        "status": "running",
        "openai_api": "configured" if OPENAI_API_KEY else "not configured"
    })

@app.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "openai_api": bool(OPENAI_API_KEY)
    })

@app.route('/database_info', methods=['GET'])
def database_info():
    """
    Get information about the BAXUS whisky database
    
    Returns:
        json: Database statistics
    """
    try:
        # Get bottle data using WhiskyService
        annotation_count = len(whisky_service._annotation_bottles)
        baxus_db_count = len(whisky_service._baxus_bottles)
        
        # Get bottle images count
        bottle_images_count = 0
        bottle_images_dir = os.path.join(os.path.dirname(__file__), 'data', 'bottle_images')
        if os.path.exists(bottle_images_dir):
            bottle_images_count = len([f for f in os.listdir(bottle_images_dir) if f.endswith('.jpg')])
        
        # Get bottle annotations count
        bottle_annotations_count = 0
        bottle_annotations_dir = os.path.join(os.path.dirname(__file__), 'data', 'bottle_annotations')
        if os.path.exists(bottle_annotations_dir):
            bottle_annotations_count = len([f for f in os.listdir(bottle_annotations_dir) if f.endswith('.json')])
        
        # Return database information
        return jsonify({
            "status": "success",
            "database": {
                "annotations": annotation_count,
                "bottle_images": bottle_images_count,
                "bottle_annotations": bottle_annotations_count,
                "whisky_database_entries": baxus_db_count
            }
        })
    except Exception as e:
        app.logger.error(f"Error getting database info: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route('/test_recognize', methods=['POST'])
def test_recognize():
    """
    Simple test endpoint to debug image upload without OpenAI integration.
    """
    try:
        logger.info("==== TEST RECOGNIZE ENDPOINT CALLED ====")
        logger.info(f"Content type: {request.content_type}")
        logger.info(f"Form keys: {list(request.form.keys()) if request.form else 'None'}")
        logger.info(f"Files keys: {list(request.files.keys()) if request.files else 'None'}")
        
        # Prepare a sample response
        response = {
            "bottle_detected": True,
            "results": [
                {
                    "label": "Test Whisky",
                    "matches": [
                        {
                            "name": "Test Blanton's Single Barrel",
                            "confidence": 0.95,
                            "price": 299.99
                        }
                    ]
                }
            ]
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Test recognize error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Test error: {str(e)}"}), 500

@app.route('/recognize', methods=['POST'])
def recognize_image():
    """
    Recognize a whisky bottle from an uploaded image
    
    Returns:
        json: Recognition results
    """
    app.logger.info("Recognition request received")
    
    # Validate request
    if 'image' not in request.files:
        app.logger.warning("No image in request")
        return jsonify({
            "error": "No image provided. Please upload an image file."
        }), 400
    
    try:
        # Get the image file
        image_file = request.files['image']
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Get API key with proper error handling
        api_key = OPENAI_API_KEY
        if not api_key:
            app.logger.error("No OpenAI API key available")
            return jsonify({"error": "OpenAI API key not configured"}), 500
        
        app.logger.info(f"Using API key: {api_key[:5]}...")
        
        # Use our unified Whisky Service for recognition
        bottle_info = whisky_service.recognize_bottle(image_data, api_key)
        
        if not bottle_info:
            app.logger.warning("No bottle detected by Whisky Service")
            return jsonify({
                "bottle_detected": False,
                "results": [],
                "error": "No whisky bottle detected in image"
            }), 200
        
        app.logger.info(f"Detected bottle: {bottle_info['name']}")
        
        # Format response with all available data
        formatted_bottle = {
            "name": re.sub(r'\.(jpg|jpeg|png|gif|webp)$', '', bottle_info["name"], flags=re.IGNORECASE),
            "confidence": bottle_info.get("confidence", 0.95)
        }
        
        # Add all pricing and bottle data
        for key in ["fair_market_price", "msrp", "shelf_price", "proof", 
                    "abv", "size", "popularity_rank", "community_rating"]:
            if key in bottle_info and bottle_info[key]:
                formatted_bottle[key] = bottle_info[key]
        
        # Return structured response
        return jsonify({
            "bottle_detected": True,
            "results": [
                {
                    "image": "base64_image_data_would_go_here",
                    "matches": [formatted_bottle]
                }
            ]
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error in recognition: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Recognition error: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Check if the database exists
    if not os.path.exists(config.WHISKY_DATABASE_PATH):
        logger.error(f"Database not found at {config.WHISKY_DATABASE_PATH}")
    else:
        logger.info(f"Found BAXUS database at {config.WHISKY_DATABASE_PATH} with {len(whisky_service.get_roboflow_metadata())} entries")
    
    # Start the server
    port = int(os.environ.get("PORT", 5000))
    logger.info("==================================================")
    logger.info(f"Starting Whisky Goggles API server on port {port}")
    logger.info(f"  - Home: https://localhost:{port}/")
    logger.info(f"  - Health Check: https://localhost:{port}/health")
    logger.info(f"  - Database Info: https://localhost:{port}/database_info")
    logger.info(f"  - Recognition: https://localhost:{port}/recognize")
    logger.info(f"  - Test Recognize: https://localhost:{port}/test_recognize")
    logger.info("==================================================")
    
    # Start the Flask server with SSL
    app.run(host='0.0.0.0', port=port, debug=True, ssl_context=('/home/ec2-user/bwgy/ssl/flask-selfsigned.crt', '/home/ec2-user/bwgy/ssl/flask-selfsigned.key'))
