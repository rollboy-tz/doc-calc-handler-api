"""
TEMPLATE GENERATION ROUTES - UPDATED FOR PRODUCTION
"""
from flask import Blueprint, request, jsonify, send_file
import tempfile
import os
from services.generators.marksheet_generator import MarksheetGenerator
from services.generators.subject_generator import SubjectGenerator

template_routes = Blueprint('templates', __name__)

@template_routes.route('/api/templates/full', methods=['POST'])
def generate_full_template():
    """Generate full marksheet template (all subjects)"""
    try:
        data = request.json or {}
        
        # Get parameters
        class_name = data.get('class_name', 'FORM 4')
        stream = data.get('stream', '')
        subjects = data.get('subjects', [])
        students = data.get('students', [])  # ACTUAL STUDENT DATA
        
        # Generate template
        generator = MarksheetGenerator(
            class_name=class_name,
            stream=stream,
            subjects=subjects,
            students=students  # PASS ACTUAL STUDENTS
        )
        
        excel_data = generator.generate()
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_file.write(excel_data.getvalue())
        temp_file.close()
        
        # Get filename
        filename = generator.get_info()['filename']
        
        # Return file
        return send_file(
            temp_file.name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@template_routes.route('/api/templates/subject', methods=['POST'])
def generate_subject_template():
    """Generate single subject template"""
    try:
        data = request.json or {}
        
        subject_name = data.get('subject_name', 'MATHEMATICS')
        class_name = data.get('class_name', 'FORM 4')
        stream = data.get('stream', '')
        students = data.get('students', [])  # ACTUAL STUDENT DATA
        
        # Generate template
        generator = SubjectGenerator(
            subject_name=subject_name,
            class_name=class_name,
            stream=stream,
            students=students  # PASS ACTUAL STUDENTS
        )
        
        excel_data = generator.generate()
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_file.write(excel_data.getvalue())
        temp_file.close()
        
        # Get filename
        filename = generator.get_info()['filename']
        
        # Return file
        return send_file(
            temp_file.name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@template_routes.route('/api/templates/info', methods=['POST'])
def get_template_info():
    """Get template information without generating file"""
    try:
        data = request.json or {}
        template_type = data.get('type', 'full')
        
        if template_type == 'full':
            class_name = data.get('class_name', 'FORM 4')
            stream = data.get('stream', '')
            subjects = data.get('subjects', [])
            students = data.get('students', [])
            
            generator = MarksheetGenerator(
                class_name=class_name,
                stream=stream,
                subjects=subjects,
                students=students
            )
            info = generator.get_info()
            
        elif template_type == 'subject':
            subject_name = data.get('subject_name', 'MATHEMATICS')
            class_name = data.get('class_name', 'FORM 4')
            stream = data.get('stream', '')
            students = data.get('students', [])
            
            generator = SubjectGenerator(
                subject_name=subject_name,
                class_name=class_name,
                stream=stream,
                students=students
            )
            info = generator.get_info()
        
        else:
            return jsonify({
                'success': False, 
                'error': 'Invalid template type. Use "full" or "subject"'
            }), 400
        
        return jsonify({
            'success': True,
            'template_info': info
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500