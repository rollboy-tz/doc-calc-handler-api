"""
routes/report_routes.py - SIMPLE WORKING VERSION
"""
from flask import Blueprint, request, jsonify, send_file
import tempfile
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

report_routes = Blueprint('report_routes', __name__)

@report_routes.route('/api/reports/student', methods=['POST'])
def generate_student_report():
    """Generate individual student report"""
    try:
        data = request.get_json()
        
        if not data or 'student_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing student_data'
            }), 400
        
        # Import inside function to avoid circular imports
        from services.pdf_reports import ReportFactory
        
        # Create system config
        system_config = {
            "system_name": "EDU-MANAGER PRO",
            "version": "2.0",
            "copyright": f"© {datetime.now().year} EduManager Pro",
            "author": "EDU-MANAGER REPORT SYSTEM",
            "generator": "Python ReportLab"
        }
        
        # Create and generate report
        report = ReportFactory.create('student_report', system_config)
        
        pdf_path = report.generate(
            data['student_data'],
            data.get('class_data', {}),
            data.get('school_info')
        )
        
        # Create filename
        student_name = data['student_data']['student']['name'].replace(' ', '_')
        filename = f"report_{student_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_routes.route('/api/reports/class', methods=['POST'])
def generate_class_sheet():
    """Generate class result sheet"""
    try:
        data = request.get_json()
        
        if not data or 'class_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing class_data'
            }), 400
        
        # Import inside function
        from services.pdf_reports import ReportFactory
        
        system_config = {
            "system_name": "EDU-MANAGER PRO",
            "version": "2.0",
            "copyright": f"© {datetime.now().year} EduManager Pro",
            "author": "EDU-MANAGER REPORT SYSTEM",
            "generator": "Python ReportLab"
        }
        
        report = ReportFactory.create('class_sheet', system_config)
        pdf_path = report.generate(
            data['class_data'],
            data.get('school_info')
        )
        
        # Create filename
        class_id = data['class_data']['metadata']['class_id']
        filename = f"class_sheet_{class_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Class sheet failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_routes.route('/api/reports/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'pdf-report-generator',
        'timestamp': datetime.now().isoformat()
    })