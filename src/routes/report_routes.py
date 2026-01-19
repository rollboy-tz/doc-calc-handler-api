"""
routes/report_routes.py
FIXED - Correct imports
"""
from flask import Blueprint, request, jsonify, send_file
from services.pdf_reports import ReportFactory, ReportMetadata  # ✅ This is correct
import tempfile
import os
import logging

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
        
        # Create metadata
        metadata = ReportMetadata(
            school_info=data.get('school_info'),
            exam_info=data.get('exam_info')
        )
        
        # Create and generate report
        report = ReportFactory.create('student_report', metadata.to_dict())
        pdf_path = report.generate(
            data['student_data'],
            data.get('class_data', {}),
            data.get('school_info')
        )
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=os.path.basename(pdf_path),
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_routes.route('/api/results/class', methods=['POST'])
def generate_class_sheet():
    """Generate class result sheet"""
    try:
        data = request.get_json()
        
        if not data or 'class_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing class_data'
            }), 400
        
        metadata = ReportMetadata(
            school_info=data.get('school_info'),
            exam_info=data.get('exam_info')
        )
        
        report = ReportFactory.create('class_sheet', metadata.to_dict())
        pdf_path = report.generate(
            data['class_data'],
            data.get('school_info')
        )
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=os.path.basename(pdf_path),
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Class sheet failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500