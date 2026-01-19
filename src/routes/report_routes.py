"""
routes/report_routes.py
"""
from flask import Blueprint, request, jsonify, send_file
from services.pdf_services.student_reports.generator import StudentReportGenerator
import tempfile
import os
from datetime import datetime

report_bp = Blueprint('reports', __name__)

@report_bp.route('/api/reports/student', methods=['POST'])
def generate_student_report():
    """Generate student report endpoint"""
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required data
        if not data or 'student_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing student_data in request'
            }), 400
        
        # System configuration
        system_config = {
            "system_name": "EDU-MANAGER PRO",
            "version": "3.0",
            "domain": "edumanager.ac.tz",
            "support_email": "support@edumanager.ac.tz",
            "support_phone": "+255 123 456 789",
            "company": "EduManager Solutions Ltd"
        }
        
        # Create generator and generate PDF
        generator = StudentReportGenerator(system_config)
        
        pdf_path = generator.generate(
            student_data=data['student_data'],
            class_info=data.get('class_info', {}),
            school_info=data.get('school_info', {})
        )
        
        # Prepare response
        student_name = data['student_data']['student']['name']
        filename = f"student_report_{student_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/reports/test', methods=['GET'])
def test_report():
    """Test endpoint with sample data"""
    try:
        # Sample data for testing
        sample_data = {
            "student_data": {
                "student": {
                    "name": "TEST STUDENT",
                    "admission": "ADM001",
                    "gender": "M"
                },
                "summary": {
                    "total": 450,
                    "average": 75.0,
                    "grade": "B",
                    "position": "5/50",
                    "division": "II",
                    "remark": "GOOD PERFORMANCE"
                }
            },
            "class_info": {
                "class_name": "FORM 4 TEST",
                "exam_name": "TEST EXAM",
                "term": "1"
            },
            "school_info": {
                "name": "TEST SCHOOL",
                "address": "TEST LOCATION"
            }
        }
        
        system_config = {
            "system_name": "EDU-MANAGER PRO",
            "version": "3.0",
            "domain": "edumanager.ac.tz",
            "support_email": "support@edumanager.ac.tz",
            "support_phone": "+255 123 456 789"
        }
        
        generator = StudentReportGenerator(system_config)
        pdf_path = generator.generate(
            student_data=sample_data['student_data'],
            class_info=sample_data['class_info'],
            school_info=sample_data['school_info']
        )
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name="test_report.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500