"""
PDF ROUTES - FIXED IMPORTS
"""
from flask import Blueprint, request, send_file
from datetime import datetime
import tempfile
import sys
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to src
parent_dir = os.path.dirname(current_dir)

# Add src to Python path if not already there
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now import from services
try:
    from services.pdf.student_report import StudentReportGenerator
    from services.pdf.class_report import ClassReportGenerator
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"Current path: {sys.path}")
    raise

pdf_routes = Blueprint('pdf', __name__)

# Rest of your code remains the same...
student_gen = StudentReportGenerator()
class_gen = ClassReportGenerator()

@pdf_routes.route('/api/pdf/student', methods=['POST'])
def generate_student_pdf():
    # ... rest of function
    pass

@pdf_routes.route('/api/pdf/class', methods=['POST'])
def generate_class_pdf():
    # ... rest of function
    pass

@pdf_routes.route('/api/pdf/status', methods=['GET'])
def status():
    # ... rest of function
    pass