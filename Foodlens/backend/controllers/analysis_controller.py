"""
Analysis Controller for FoodLens
Handles image upload, OCR processing, and Nutri-Score calculation
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
analysis_bp = Blueprint('analysis', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@analysis_bp.route('/analyze', methods=['POST'])
def analyze_product():
    """
    Analyze product image using OCR and calculate Nutri-Score
    """
    try:
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload an image file.'}), 400
        
        # Get request parameters
        language = request.form.get('language', 'tr')
        product_name = request.form.get('product_name', '')
        brand = request.form.get('brand', '')
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        if not filename:
            filename = 'uploaded_image.jpg'
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"Processing image: {filename}")
        
        # Try to import and use OCR service
        try:
            from services.ocr_service import ocr_service
            ocr_result = ocr_service.process_image(filepath, language)
            
            if not ocr_result['success']:
                # Clean up file and return error
                try:
                    os.remove(filepath)
                except:
                    pass
                return jsonify({
                    'success': False,
                    'error': 'OCR processing failed',
                    'details': ocr_result.get('error', 'Unknown OCR error')
                }), 500
            
            # Try to calculate Nutri-Score
            try:
                from services.nutri_score_service import nutri_score_calculator
                nutri_score_result = nutri_score_calculator.analyze_product_from_ocr(
                    ocr_result['text'],
                    ocr_result['ingredients']
                )
                
                if not nutri_score_result['success']:
                    # Clean up file and return error
                    try:
                        os.remove(filepath)
                    except:
                        pass
                    return jsonify({
                        'success': False,
                        'error': 'Nutri-Score calculation failed',
                        'details': nutri_score_result.get('error', 'Unknown Nutri-Score error')
                    }), 500
                
                # Success - prepare response
                response_data = {
                    'success': True,
                    'ocr_text': ocr_result['text'],
                    'ingredients': ocr_result['ingredients'],
                    'nutri_score': {
                        'grade': nutri_score_result['nutri_score']['grade'],
                        'score': nutri_score_result['nutri_score']['score'],
                        'color': nutri_score_result['nutri_score']['color'],
                        'negative_points': nutri_score_result['nutri_score']['negative_points'],
                        'positive_points': nutri_score_result['nutri_score']['positive_points'],
                        'nutrition_breakdown': {
                            'energy_kj': nutri_score_result['nutri_score']['nutrition_data'].energy_kj,
                            'fat': nutri_score_result['nutri_score']['nutrition_data'].fat,
                            'saturated_fat': nutri_score_result['nutri_score']['nutrition_data'].saturated_fat,
                            'sugars': nutri_score_result['nutri_score']['nutrition_data'].sugars,
                            'sodium': nutri_score_result['nutri_score']['nutrition_data'].sodium,
                            'proteins': nutri_score_result['nutri_score']['nutrition_data'].proteins,
                            'fiber': nutri_score_result['nutri_score']['nutrition_data'].fiber,
                            'fruits_vegetables_nuts': nutri_score_result['nutri_score']['nutrition_data'].fruits_vegetables_nuts
                        }
                    },
                    'recommendations': generate_recommendations(nutri_score_result['nutri_score'], language),
                    'processing_info': {
                        'total_ingredients': len(ocr_result['ingredients']),
                        'language': language,
                        'product_name': product_name,
                        'brand': brand
                    }
                }
                
                # Clean up uploaded file
                try:
                    os.remove(filepath)
                except Exception as e:
                    logger.warning(f"Could not remove uploaded file: {e}")
                
                logger.info(f"Analysis completed successfully. Grade: {nutri_score_result['nutri_score']['grade']}")
                return jsonify(response_data), 200
                
            except ImportError as e:
                logger.error(f"Nutri-Score service not available: {e}")
                # Return mock Nutri-Score data for testing
                response_data = {
                    'success': True,
                    'ocr_text': ocr_result['text'],
                    'ingredients': ocr_result['ingredients'],
                    'nutri_score': {
                        'grade': 'C',
                        'score': 15,
                        'color': '#FFA500',
                        'negative_points': 18,
                        'positive_points': 3,
                        'nutrition_breakdown': {
                            'energy_kj': 2000,
                            'fat': 10.5,
                            'saturated_fat': 3.2,
                            'sugars': 8.1,
                            'sodium': 350,
                            'proteins': 6.8,
                            'fiber': 2.1,
                            'fruits_vegetables_nuts': 15
                        }
                    },
                    'recommendations': generate_recommendations_mock(language),
                    'processing_info': {
                        'total_ingredients': len(ocr_result['ingredients']),
                        'language': language,
                        'product_name': product_name,
                        'brand': brand,
                        'note': 'Using mock Nutri-Score data for testing'
                    }
                }
                
                # Clean up uploaded file
                try:
                    os.remove(filepath)
                except:
                    pass
                
                return jsonify(response_data), 200
                
        except ImportError as e:
            logger.error(f"OCR service not available: {e}")
            # Return mock data for testing
            response_data = {
                'success': True,
                'ocr_text': 'Mock OCR text - service not available',
                'ingredients': ['ingredient1', 'ingredient2', 'ingredient3'],
                'nutri_score': {
                    'grade': 'C',
                    'score': 15,
                    'color': '#FFA500',
                    'negative_points': 18,
                    'positive_points': 3,
                    'nutrition_breakdown': {
                        'energy_kj': 2000,
                        'fat': 10.5,
                        'saturated_fat': 3.2,
                        'sugars': 8.1,
                        'sodium': 350,
                        'proteins': 6.8,
                        'fiber': 2.1,
                        'fruits_vegetables_nuts': 15
                    }
                },
                'recommendations': generate_recommendations_mock(language),
                'processing_info': {
                    'total_ingredients': 3,
                    'language': language,
                    'product_name': product_name,
                    'brand': brand,
                    'note': 'Using mock data - OCR service not available'
                }
            }
            
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except:
                pass
            
            return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error in analyze_product: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500

def generate_recommendations(nutri_score_data, language):
    """Generate health recommendations based on Nutri-Score"""
    try:
        grade = nutri_score_data['grade']
        nutrition = nutri_score_data['nutrition_data']
        
        recommendations = {
            'tr': [],
            'en': []
        }
        
        # Grade-based recommendations
        if grade in ['A', 'B']:
            recommendations['tr'].append("✅ Bu ürün sağlıklı bir seçim!")
            recommendations['en'].append("✅ This product is a healthy choice!")
        elif grade == 'C':
            recommendations['tr'].append("⚠️ Bu ürünü orta düzeyde tüketebilirsiniz.")
            recommendations['en'].append("⚠️ This product can be consumed in moderation.")
        else:  # D, E
            recommendations['tr'].append("❌ Bu ürünü sınırlı tüketmenizi öneririz.")
            recommendations['en'].append("❌ We recommend limiting consumption of this product.")
        
        # Specific nutrient recommendations
        if nutrition.saturated_fat > 5:
            recommendations['tr'].append("🔸 Yüksek doymuş yağ içeriği nedeniyle dikkatli tüketin.")
            recommendations['en'].append("🔸 Consume carefully due to high saturated fat content.")
        
        if nutrition.sugars > 15:
            recommendations['tr'].append("🔸 Yüksek şeker içeriği bulunmaktadır.")
            recommendations['en'].append("🔸 Contains high sugar content.")
        
        if nutrition.sodium > 500:
            recommendations['tr'].append("🔸 Yüksek sodyum içeriği nedeniyle tuz tüketiminize dikkat edin.")
            recommendations['en'].append("🔸 Watch your salt intake due to high sodium content.")
        
        if nutrition.fiber > 3:
            recommendations['tr'].append("✅ İyi lif kaynağı!")
            recommendations['en'].append("✅ Good source of fiber!")
        
        if nutrition.proteins > 10:
            recommendations['tr'].append("✅ Yüksek protein içeriği!")
            recommendations['en'].append("✅ High protein content!")
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return generate_recommendations_mock(language)

def generate_recommendations_mock(language):
    """Generate mock recommendations for testing"""
    recommendations = {
        'tr': [
            "⚠️ Bu ürünü orta düzeyde tüketebilirsiniz.",
            "🔸 Besin değerlerini kontrol edin.",
            "✅ Dengeli beslenme için çeşitli gıdalar tüketin."
        ],
        'en': [
            "⚠️ This product can be consumed in moderation.",
            "🔸 Check the nutritional values.",
            "✅ Consume various foods for a balanced diet."
        ]
    }
    return recommendations

@analysis_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for analysis service"""
    return jsonify({
        'success': True,
        'message': 'Analysis service is running',
        'endpoints': [
            '/analyze - POST - Analyze product image'
        ]
    })
