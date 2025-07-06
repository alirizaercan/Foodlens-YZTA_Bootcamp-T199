"""
Nutrition Analysis Controller
Handles food product image analysis, OCR, and Nutri-Score calculation
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import json
import logging
from datetime import datetime, timedelta
import traceback
from pathlib import Path
import time
import cv2
import numpy as np

# Import our enhanced services
from services.ocr_service import enhanced_ocr_service
from services.nutri_score_service import enhanced_nutri_score_calculator

logger = logging.getLogger(__name__)

# Create Blueprint
nutrition_analysis_bp = Blueprint('nutrition_analysis', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    """Validate file extensions"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files(upload_folder, days_old=7):
    """Clean up files older than specified days"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days_old)
        files_removed = 0
        
        for filename in os.listdir(upload_folder):
            filepath = os.path.join(upload_folder, filename)
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                if file_time < cutoff_date:
                    try:
                        os.remove(filepath)
                        files_removed += 1
                        logger.info(f"Removed old file: {filename}")
                    except Exception as e:
                        logger.warning(f"Could not remove old file {filename}: {e}")
        
        if files_removed > 0:
            logger.info(f"Cleaned up {files_removed} old files")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def save_debug_image(image, filename, debug_folder='debug_images'):
    """Save debug images for troubleshooting"""
    try:
        # Create debug folder if it doesn't exist
        os.makedirs(debug_folder, exist_ok=True)
        
        # Save image
        debug_path = os.path.join(debug_folder, filename)
        cv2.imwrite(debug_path, image)
        logger.info(f"Saved debug image: {debug_path}")
        return debug_path
    except Exception as e:
        logger.error(f"Error saving debug image: {e}")
        return None

@nutrition_analysis_bp.route('/analyze', methods=['POST'])
def analyze_product():
    """Analyze product image for nutrition information and calculate Nutri-Score"""
    try:
        start_time = time.time()
        
        # Check if image file was uploaded
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        # Check if file is empty
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename'
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file format. Allowed formats: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Get language preference (default to Turkish)
        language = request.form.get('language', 'tr')
        
        # Create timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        secure_name = secure_filename(file.filename)
        filename = f"{timestamp}_{secure_name}"
        
        # Define upload folder
        upload_folder = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save uploaded file
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Clean up old files
        cleanup_old_files(upload_folder)
        
        # Process the image with enhanced OCR service
        logger.info(f"Processing image: {filepath}")
        ocr_result = enhanced_ocr_service.process_image(filepath, language)
        
        if not ocr_result['success']:
            return jsonify({
                'success': False,
                'error': f"OCR processing failed: {ocr_result.get('error', 'Unknown error')}"
            }), 500
        
        logger.info(f"OCR completed with confidence: {ocr_result.get('confidence', 0):.2f}")
        
        # Extract ingredients from OCR text
        ingredients = ocr_result.get('ingredients', [])
        
        # Analyze product with enhanced Nutri-Score calculator
        nutri_analysis = enhanced_nutri_score_calculator.analyze_product_from_ocr(ocr_result, ingredients)
        
        if not nutri_analysis['success']:
            return jsonify({
                'success': False,
                'error': f"Nutri-Score calculation failed: {nutri_analysis.get('error', 'Unknown error')}"
            }), 500
            
        # Prepare file URL
        file_url = f"/static/uploads/{filename}"
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare response with comprehensive information
        response = {
            'success': True,
            'file_url': file_url,
            'nutri_score': nutri_analysis['nutri_score'],
            'nutrition': nutri_analysis['nutri_score']['nutrition_data'],
            'ingredients': ingredients,
            'data_quality': nutri_analysis['data_quality'],
            'processing': {
                'time_seconds': processing_time,
                'language': language,
                'ocr_confidence': ocr_result.get('confidence', 0),
                'table_structure': ocr_result.get('table_structure', {})
            }
        }
        
        # Add warnings if data quality is low
        if nutri_analysis['data_quality']['manual_review_needed']:
            missing = nutri_analysis['data_quality']['missing_nutrients']
            response['warnings'] = [
                f"Data quality is low ({nutri_analysis['data_quality']['confidence']:.1f}%), manual review recommended.",
                f"Missing nutrients: {', '.join(missing)}" if missing else None
            ]
            response['warnings'] = [w for w in response['warnings'] if w]
        
        logger.info(f"Analysis completed in {processing_time:.2f}s with Nutri-Score: {nutri_analysis['nutri_score']['grade']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error analyzing product: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f"Error analyzing product: {str(e)}"
        }), 500

@nutrition_analysis_bp.route('/debug-ocr', methods=['POST'])
def debug_ocr():
    """Debug endpoint for OCR processing only"""
    try:
        # Check if image file was uploaded
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file format. Allowed formats: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Get language preference (default to Turkish)
        language = request.form.get('language', 'tr')
        
        # Create timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        secure_name = secure_filename(file.filename)
        filename = f"{timestamp}_{secure_name}"
        
        # Define upload folder
        upload_folder = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save uploaded file
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Process the image with enhanced OCR service
        ocr_result = enhanced_ocr_service.process_image(filepath, language)
        
        # Prepare file URL
        file_url = f"/static/uploads/{filename}"
        
        # Return detailed OCR results for debugging
        response = {
            'success': True,
            'file_url': file_url,
            'ocr_text': ocr_result.get('text', ''),
            'ingredients': ocr_result.get('ingredients', []),
            'nutrition_values': ocr_result.get('nutrition_values', {}),
            'confidence': ocr_result.get('confidence', 0),
            'table_structure': ocr_result.get('table_structure', {})
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in debug-ocr: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f"Error in debug-ocr: {str(e)}"
        }), 500
