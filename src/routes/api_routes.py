# routes/api_routes.py
"""
MAIN API ROUTES
Version 1.0 - Core endpoints
"""
from flask import Blueprint, jsonify
from datetime import datetime

api_routes = Blueprint('api', __name__, url_prefix='/api/v1')

@api_routes.route('/', methods=['GET'])
def api_root():
    """API Root endpoint"""
    return jsonify({
        "api": "School Management System API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "documentation": "/api/v1/docs"
    })

@api_routes.route('/docs', methods=['GET'])
def api_docs():
    """API Documentation"""
    return jsonify({
        "endpoints": {
            "extraction": {
                "POST /api/v1/extract/single-subject": "Extract single subject Excel",
                "POST /api/v1/extract/multi-subject": "Extract multi-subject Excel",
                "POST /api/v1/extract/debug": "Debug Excel file"
            },
            "processing": {
                "POST /api/v1/process/single-subject": "Process single subject JSON",
                "POST /api/v1/process/multi-subject": "Process multi-subject JSON"
            },
            "templates": {
                "POST /api/v1/templates/full": "Generate full marksheet template",
                "POST /api/v1/templates/subject": "Generate subject template"
            },
            "system": {
                "GET /health": "Health check",
                "GET /api/v1/": "API information",
                "GET /api/v1/docs": "This documentation"
            }
        }
    })

@api_routes.route('/status', methods=['GET'])
def api_status():
    """API Status check"""
    return jsonify({
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "extraction": "active",
            "processing": "ready",
            "templates": "active"
        }
    })