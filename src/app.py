"""
PURE API GATEWAY ROUTER
Only handles: Security, Routing, Request/Response
Business logic will be in handler modules
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import middleware
from middleware.security import SecurityMiddleware

# Initialize Flask app
app = Flask(__name__)

# CORS Configuration - flexible
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')
if ALLOWED_ORIGINS and ALLOWED_ORIGINS[0]:
    CORS(app, origins=ALLOWED_ORIGINS)
    logger.info(f"CORS allowed for: {ALLOWED_ORIGINS}")
else:
    CORS(app)  # Allow all for now
    logger.warning("ALLOWED_ORIGINS not set - allowing all origins")

# Initialize security middleware
security = SecurityMiddleware(app)

# ==================== GLOBAL MIDDLEWARE ====================
@app.before_request
def global_middleware():
    """Global middleware for all requests"""
    # Apply security checks
    security_result = security.check_request(request)
    if security_result.get('blocked'):
        return jsonify({
            "success": False,
            "error": security_result['error'],
            "message": security_result['message']
        }), security_result.get('code', 403)
    
    # Log request
    logger.info(f"📨 {request.method} {request.path} from {request.remote_addr}")

# ==================== ROUTES ====================
@app.route('/api/documents/request', methods=['POST'])
def document_request():
    """Handle document requests"""
    try:
        data = request.get_json() or {}
        
        # TODO: Call your document processing function here
        # result = document_handler.process_request(data)
        
        # For now, just pass through
        return jsonify({
            "success": True,
            "message": "Document request received",
            "data": data,
            "handler": "document_request",
            "note": "Processing function will be implemented in handlers/document_handler.py"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in document_request: {str(e)}")
        return jsonify({
            "success": False,
            "error": "processing_error",
            "message": str(e)
        }), 500

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Handle calculation requests"""
    try:
        data = request.get_json() or {}
        
        # TODO: Call your calculation function here
        # result = calculation_handler.process(data)
        
        return jsonify({
            "success": True,
            "message": "Calculation request received",
            "data": data,
            "handler": "calculate",
            "note": "Calculation function will be implemented in handlers/calculation_handler.py"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in calculate: {str(e)}")
        return jsonify({
            "success": False,
            "error": "calculation_error",
            "message": str(e)
        }), 500

@app.route('/api/process', methods=['POST'])
def process():
    """Generic processing endpoint"""
    try:
        data = request.get_json() or {}
        action = data.get('action', 'unknown')
        
        # TODO: Route to appropriate handler based on action
        # if action == 'generate_pdf':
        #     result = pdf_handler.generate(data)
        # elif action == 'validate_data':
        #     result = validation_handler.validate(data)
        
        return jsonify({
            "success": True,
            "message": f"Process request for action: {action}",
            "data": data,
            "handler": "process",
            "action": action
        }), 200
        
    except Exception as e:
        logger.error(f"Error in process: {str(e)}")
        return jsonify({
            "success": False,
            "error": "process_error",
            "message": str(e)
        }), 500

# ==================== UTILITY ENDPOINTS ====================
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "API Gateway Router",
        "timestamp": os.times().elapsed,
        "allowed_origins": ALLOWED_ORIGINS if ALLOWED_ORIGINS[0] else "ALL"
    }), 200

@app.route('/api/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "Document & Calculation API Gateway",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api/documents/request", "method": "POST", "desc": "Submit document requests"},
            {"path": "/api/calculate", "method": "POST", "desc": "Perform calculations"},
            {"path": "/api/process", "method": "POST", "desc": "Generic processing"},
            {"path": "/health", "method": "GET", "desc": "Health check"},
            {"path": "/api/info", "method": "GET", "desc": "API information"}
        ],
        "security": {
            "api_key_required": bool(os.getenv('API_KEY')),
            "allowed_origins": ALLOWED_ORIGINS if ALLOWED_ORIGINS[0] else "Open"
        }
    }), 200

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "not_found",
        "message": "Endpoint does not exist"
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "success": False,
        "error": "method_not_allowed",
        "message": f"Method {request.method} not allowed for this endpoint"
    }), 405

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({
        "success": False,
        "error": "internal_error",
        "message": "Internal server error occurred"
    }), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    
    logger.info("=" * 50)
    logger.info("🚀 API Gateway Router Starting...")
    logger.info(f"📡 Port: {port}")
    logger.info(f"🔒 API Key Required: {'Yes' if os.getenv('API_KEY') else 'No'}")
    logger.info(f"🌐 Allowed Origins: {ALLOWED_ORIGINS if ALLOWED_ORIGINS[0] else 'ALL'}")
    logger.info("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('DEBUG', 'False').lower() == 'true'
    )