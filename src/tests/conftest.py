"""
Test configuration for PDF tests
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope='session')
def app():
    """Create Flask app for testing"""
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    return app

@pytest.fixture(scope='session')
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture(scope='session')
def weasyprint_available():
    """Check if WeasyPrint is available"""
    try:
        import weasyprint
        return True
    except ImportError:
        return False