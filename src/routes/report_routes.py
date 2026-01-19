"""
PDF REPORT GENERATION ROUTES
Uses fpdf2 library for PDF generation
"""
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import os
import traceback
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint (NO URL_PREFIX - following your pattern)
report_bp = Blueprint('report', __name__)

# Import PDF generator factory
try:
    from services.pdf_services.factory import PDFGeneratorFactory
    from services.pdf_services.base.utils import generate_filename
except ImportError as e:
    logger.error(f"Failed to import PDF services: {e}")
    # We'll handle this in the routes

# ========== STUDENT REPORT ==========

@report_bp.route('/api/reports/student', methods=['POST'])
def generate_student_report():
    """
    Generate student academic report PDF
    ---
    Expected JSON structure:
    {
        "student_data": {
            "student": {
                "name": "Student Name",
                "admission": "ADM001",
                "gender": "Male/Female",
                "class": "Form 4",
                "year": "2024"
            },
            "summary": {
                "total": 450,
                "average": 75.0,
                "grade": "B",
                "position": "15/50",
                "division": "II",
                "remark": "Good performance"
            },
            "subjects": [
                {"name": "Math", "score": 85, "grade": "A", "remarks": "Excellent"}
            ],
            "comments": {
                "class_teacher": "Teacher name",
                "principal": "Principal name",
                "remarks": "Additional comments"
            }
        },
        "class_info": {
            "class_name": "FORM 4 EAST",
            "exam_name": "TERM I EXAM",
            "term": "I",
            "year": "2024"
        },
        "school_info": {
            "name": "School Name",
            "motto": "School Motto",
            "address": "School Address"
        },
        "config": {
            "system_name": "EDU-MANAGER",
            "footer_text": "Confidential"
        }
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required data
        if not data or 'student_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing student_data in request'
            }), 400
        
        # Extract data with defaults
        student_data = data['student_data']
        class_info = data.get('class_info', {})
        school_info = data.get('school_info', {})
        user_config = data.get('config', {})
        
        # Validate required student fields
        required_student_fields = ['student', 'summary']
        for field in required_student_fields:
            if field not in student_data:
                return jsonify({
                    'success': False,
                    'error': f'Missing {field} in student_data'
                }), 400
        
        # System configuration
        system_config = {
            "system_name": "EDU-MANAGER PRO",
            "version": "2.0.0",
            "domain": "edumanager.ac.tz",
            "support_email": "support@edumanager.ac.tz",
            "support_phone": "+255 123 456 789",
            "company": "EduManager Solutions Ltd",
            "footer_text": "Confidential - For official use only",
            "generated_date": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        # Merge user config with system config
        final_config = {**system_config, **user_config}
        
        # Create generator and generate PDF
        generator = PDFGeneratorFactory.create('student_report', final_config)
        
        pdf_path = generator.generate(
            student_data=student_data,
            class_info=class_info,
            school_info=school_info
        )
        
        # Create filename
        student = student_data['student']
        admission = student.get('admission', 'unknown').replace(' ', '_')
        student_name = student.get('name', 'student').replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{admission}_{student_name}_{timestamp}.pdf"
        
        logger.info(f"Generated student report: {filename}")
        
        # Return PDF file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error generating student report: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== TEST ENDPOINT ==========

@report_bp.route('/api/reports/student/test', methods=['GET'])
def test_student_report():
    """
    Test endpoint - generates a sample student report
    Returns a PDF file with sample data
    """
    try:
        # Sample data for testing (Tanzanian context)
        sample_data = {
            "student_data": {
                "student": {
                    "name": "JOHN PETER MWITA",
                    "admission": "ADM2024001",
                    "gender": "Male",
                    "class": "Form 4 East",
                    "year": "2024",
                    "stream": "Science"
                },
                "summary": {
                    "total": 568,
                    "average": 81.14,
                    "grade": "A",
                    "position": "5/120",
                    "division": "I",
                    "remark": "EXCELLENT PERFORMANCE"
                },
                "subjects": [
                    {"name": "Mathematics", "score": 98, "grade": "A", "remarks": "Top in class"},
                    {"name": "English Language", "score": 85, "grade": "A-", "remarks": "Very good"},
                    {"name": "Kiswahili", "score": 92, "grade": "A", "remarks": "Excellent"},
                    {"name": "Physics", "score": 78, "grade": "B+", "remarks": "Good improvement"},
                    {"name": "Chemistry", "score": 82, "grade": "A-", "remarks": "Consistent"},
                    {"name": "Biology", "score": 88, "grade": "A", "remarks": "Excellent"},
                    {"name": "History", "score": 75, "grade": "B", "remarks": "Satisfactory"},
                    {"name": "Geography", "score": 70, "grade": "B-", "remarks": "Needs improvement"}
                ],
                "comments": {
                    "class_teacher": "Mwalimu S. Kipande",
                    "principal": "Dr. A. Mwamba",
                    "remarks": "Student has shown remarkable improvement. Keep up the good work."
                }
            },
            "class_info": {
                "class_name": "FORM 4 EAST",
                "exam_name": "ANNUAL EXAMINATION",
                "term": "III",
                "year": "2024",
                "exam_date": "15/11/2024"
            },
            "school_info": {
                "name": "MLIMANI SECONDARY SCHOOL",
                "motto": "Education for Excellence",
                "address": "P.O. Box 1234, Dar es Salaam, Tanzania",
                "phone": "+255 22 123 4567",
                "email": "info@mlimanischool.ac.tz"
            },
            "config": {
                "system_name": "EDU-MANAGER TEST",
                "footer_text": "TEST REPORT - Sample data for demonstration"
            }
        }
        
        # Create generator with test config
        system_config = {
            "system_name": "EDU-MANAGER PRO",
            "version": "2.0.0",
            "footer_text": "SAMPLE REPORT - For testing purposes only"
        }
        
        generator = PDFGeneratorFactory.create('student_report', system_config)
        
        # Generate PDF
        pdf_path = generator.generate(
            student_data=sample_data['student_data'],
            class_info=sample_data['class_info'],
            school_info=sample_data['school_info']
        )
        
        # Return PDF
        filename = "test_student_report.pdf"
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Test endpoint error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== REPORT TYPES ==========

@report_bp.route('/api/reports/types', methods=['GET'])
def get_report_types():
    """
    Get available report types
    Returns a list of supported PDF report types
    """
    try:
        return jsonify({
            'success': True,
            'data': {
                'report_types': [
                    {
                        'id': 'student_report',
                        'name': 'Student Academic Report',
                        'description': 'Individual student performance report with subjects breakdown',
                        'endpoint': 'POST /api/reports/student'
                    }
                    # Additional report types can be added here
                    # {
                    #     'id': 'class_report',
                    #     'name': 'Class Results Sheet',
                    #     'description': 'Class-wide results summary',
                    #     'endpoint': 'POST /api/reports/class'
                    # },
                    # {
                    #     'id': 'transcript',
                    #     'name': 'Student Transcript',
                    #     'description': 'Official academic transcript',
                    #     'endpoint': 'POST /api/reports/transcript'
                    # }
                ]
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== HEALTH CHECK ==========

@report_bp.route('/api/reports/health', methods=['GET'])
def pdf_service_health():
    """
    PDF service health check
    Tests if PDF generation service is operational
    """
    try:
        # Try to create a generator instance
        test_config = {
            "system_name": "EDU-MANAGER HEALTH CHECK",
            "version": "2.0.0"
        }
        
        generator = PDFGeneratorFactory.create('student_report', test_config)
        
        return jsonify({
            'success': True,
            'service': 'pdf-generation',
            'status': 'healthy',
            'engine': 'fpdf2',
            'timestamp': datetime.now().isoformat(),
            'message': 'PDF generation service is operational'
        })
        
    except Exception as e:
        logger.error(f"PDF health check failed: {e}")
        return jsonify({
            'success': False,
            'service': 'pdf-generation',
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ========== VALIDATION ENDPOINT ==========

@report_bp.route('/api/reports/validate', methods=['POST'])
def validate_report_data():
    """
    Validate student report data before generating PDF
    Useful for frontend validation
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'valid': False,
                'error': 'No data provided'
            }), 400
        
        errors = []
        warnings = []
        
        # Check for required sections
        if 'student_data' not in data:
            errors.append("Missing 'student_data' section")
        else:
            student_data = data['student_data']
            
            # Check student info
            if 'student' not in student_data:
                errors.append("Missing 'student' information")
            else:
                student = student_data['student']
                if not student.get('name'):
                    errors.append("Student name is required")
                if not student.get('admission'):
                    errors.append("Admission number is required")
            
            # Check summary
            if 'summary' not in student_data:
                errors.append("Missing 'summary' section")
            else:
                summary = student_data['summary']
                if summary.get('average') is None:
                    errors.append("Average score is required")
                if not summary.get('grade'):
                    errors.append("Grade is required")
        
        # Check optional sections
        if not data.get('class_info'):
            warnings.append("No class information provided")
        
        if not data.get('school_info'):
            warnings.append("No school information provided")
        
        if errors:
            return jsonify({
                'success': True,
                'valid': False,
                'errors': errors,
                'warnings': warnings,
                'message': 'Data validation failed'
            })
        
        return jsonify({
            'success': True,
            'valid': True,
            'warnings': warnings,
            'message': 'Data is valid for PDF generation'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'valid': False,
            'error': str(e)
        }), 500