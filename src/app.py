"""
MAIN FLASK APPLICATION
Configuration and initialization only
"""
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import logging

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')
    if ALLOWED_ORIGINS and ALLOWED_ORIGINS[0]:
        CORS(app, origins=ALLOWED_ORIGINS)
        logger.info(f"CORS allowed for: {ALLOWED_ORIGINS}")
    else:
        CORS(app)
        logger.warning("ALLOWED_ORIGINS not set - allowing all origins")
    
    # Import and register routes - FIXED: Single import block
    from routes import api_routes, extractor_routes, health_routes, template_routes, test_pdf_routes
    # app.py - Add this import and registration
    from routes.grading_routes import grading_routes

# Inside create_app() function, after other blueprint registrations:


    # Register blueprints with unique prefixes to avoid conflicts
    app.register_blueprint(api_routes)
    app.register_blueprint(extractor_routes)
    app.register_blueprint(health_routes)
    app.register_blueprint(template_routes)
    app.register_blueprint(grading_routes)

    
    # Register error handlers
    from routes.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info("=" * 50)
    logger.info("🚀 School Management API Starting...")
    logger.info(f"📡 Port: {port}")
    logger.info(f"🔧 Debug: {debug}")
    logger.info("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=debug)