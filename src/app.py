# app.py
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
    
    # Import and register routes
    # from routes.api_routes import api_routes
    from routes.extractor_routes import extractor_routes
    from routes.health_routes import health_routes
    
    app.register_blueprint(api_routes)
    app.register_blueprint(extractor_routes)
    app.register_blueprint(health_routes)
    
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