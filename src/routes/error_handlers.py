# routes/error_handlers.py
"""
ERROR HANDLERS
"""
from flask import jsonify

def register_error_handlers(app):
    """Register error handlers for the app"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'endpoint_not_found',
            'message': 'The requested endpoint does not exist'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'method_not_allowed',
            'message': 'HTTP method not allowed for this endpoint'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {error}')
        return jsonify({
            'success': False,
            'error': 'internal_server_error',
            'message': 'An internal server error occurred'
        }), 500