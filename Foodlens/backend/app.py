"""
FoodLens Flask Application
Main application entry point for the smart nutrition analysis platform.
"""

import os
import sys
import logging
from flask import Flask, send_from_directory, send_file, request, make_response, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.serving import WSGIRequestHandler

# Import controllers
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.nutrition_analysis_controller import nutrition_analysis_bp
from controllers.product_controller import product_bp
from controllers.analysis_controller import analysis_bp
from controllers.recommendation_controller import recommendation_bp

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__, 
                static_folder='static', 
                static_url_path='/static')
    
    # Flask configuration
    flask_env = os.getenv('FLASK_ENV', 'development')
    if flask_env == 'production':
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache
        app.config['TEMPLATES_AUTO_RELOAD'] = False
        app.config['DEBUG'] = False
    else:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # No cache for development
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.config['DEBUG'] = True
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['TOKEN_EXPIRES_IN'] = int(os.environ.get('TOKEN_EXPIRES_IN', 86400))  # 24 hours
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # CORS configuration
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": "*",
            "allow_headers": "*",
            "supports_credentials": True,
            "expose_headers": "*"
        }
    })
    
    # Add CORS headers to all responses
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
        else:
            response.headers.add('Access-Control-Allow-Origin', '*')
        
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Expose-Headers', '*')
        
        # Remove CSP header or allow HTTP
        response.headers.pop('Content-Security-Policy', None)
        
        return response
    
    # Handle preflight OPTIONS requests
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "*")
            response.headers.add('Access-Control-Allow-Methods', "*")
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(nutrition_analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(analysis_bp, url_prefix='/api/analyses')
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommendations')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'FoodLens API is running',
            'version': '1.0.0',
            'endpoints': {
                'auth': [
                    'POST /api/auth/register',
                    'POST /api/auth/login',
                    'POST /api/auth/logout',
                    'POST /api/auth/refresh',
                    'POST /api/auth/forgot-password',
                    'POST /api/auth/reset-password'
                ],
                'users': [
                    'GET /api/users/profile',
                    'PUT /api/users/profile',
                    'POST /api/users/profile/setup',
                    'GET /api/users/allergens',
                    'POST /api/users/allergens',
                    'DELETE /api/users/allergens/{id}',
                    'GET /api/users/nutrition-goals',
                    'POST /api/users/nutrition-goals',
                    'PUT /api/users/nutrition-goals/{id}'
                ],
                'analysis': [
                    'POST /api/analysis/analyze',
                    'POST /api/analysis/upload'
                ],
                'products': [
                    'GET /api/products',
                    'GET /api/products/{id}',
                    'GET /api/products/search',
                    'POST /api/products'
                ],
                'analyses': [
                    'GET /api/analyses',
                    'GET /api/analyses/{id}',
                    'DELETE /api/analyses/{id}'
                ],
                'recommendations': [
                    'GET /api/recommendations',
                    'PUT /api/recommendations/{id}/read',
                    'DELETE /api/recommendations/{id}'
                ]
            }
        })
    
    # Serve static files from uploads directory
    @app.route('/static/uploads/<path:filename>')
    def serve_uploads(filename):
        uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
        return send_from_directory(uploads_dir, filename)
    
    # Serve backend static files
    @app.route('/backend/static/<path:filename>')
    def serve_backend_static(filename):
        backend_static_dir = os.path.join(app.root_path, 'static')
        return send_from_directory(backend_static_dir, filename)
    
    # Error handlers
    @app.errorhandler(413)
    def too_large(e):
        return jsonify({
            'success': False,
            'error': 'File too large. Maximum size is 16MB.'
        }), 413
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app

# Create Flask app instance
app = create_app()

if __name__ == '__main__':
    print("Starting FoodLens API server...")
    print("Available endpoints:")
    print("  GET  /api/health")
    print("  POST /api/analysis/analyze")
    print("  Static files: /static/uploads/")
    print("  Backend static: /backend/static/")
    print("  Frontend URL: http://localhost:3000")
    print("  Backend URL: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)