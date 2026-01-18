# routes/__init__.py
"""
Routes Package - Export all route blueprints
"""
from .template_routes import template_routes
from .api_routes import api_routes
from .extractor_routes import extractor_routes
from .health_routes import health_routes

__all__ = [ 'template_routes','api_routes', 'extractor_routes', 'health_routes']