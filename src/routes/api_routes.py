# routes/api_routes.py
"""
MAIN API ROUTES
"""
from flask import Blueprint, jsonify
from datetime import datetime

api_routes = Blueprint('api', __name__)

@api_routes.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint"""
    return jsonify({
        "message": "API is working",
        "timestamp": datetime.now().isoformat()
    })

# Add more routes as needed