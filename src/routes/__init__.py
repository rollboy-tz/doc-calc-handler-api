# routes/__init__.py
"""
Routes Package - Export all route blueprints
"""
from .api_routes import api_routes
from .extractor_routes import extractor_routes
from .health_routes import health_routes

__all__ = ['api_routes', 'extractor_routes', 'health_routes']