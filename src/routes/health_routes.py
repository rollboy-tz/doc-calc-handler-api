# routes/health_routes.py
"""
HEALTH CHECK ROUTES
"""
from flask import Blueprint, jsonify
from datetime import datetime

health_routes = Blueprint('health', __name__)

@health_routes.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "School Management API",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    })

@health_routes.route('/api/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "Tanzania School Management System",
        "version": "2.0.0",
        "description": "Excel extraction and grade processing API",
        "endpoints": {
            "health": {
                "/health": "Health check",
                "/api/info": "API information"
            },
            "extraction": {
                "/api/extract/multi-subject": "Extract multi-subject Excel",
                "/api/extract/single-subject": "Extract single subject Excel"
            }
        }
    })