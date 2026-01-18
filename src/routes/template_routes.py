# routes/template_routes.py
"""
TEMPLATE GENERATION ROUTES
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
        student_count = int(data.get('student_count', 10))
        
        # Generate template
        generator = MarksheetGenerator(
            class_name=class_name,
            stream=stream,
            subjects=subjects
        )
        
        excel_data = generator.generate(student_count)
        
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
        student_count = int(data.get('student_count', 10))
        
        # Generate template
        generator = SubjectGenerator(
            subject_name=subject_name,
            class_name=class_name,
            stream=stream
        )
        
        excel_data = generator.generate(student_count)
        
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
            
            generator = MarksheetGenerator(
                class_name=class_name,
                stream=stream,
                subjects=subjects
            )
            info = generator.get_info()
            
        elif template_type == 'subject':
            subject_name = data.get('subject_name', 'MATHEMATICS')
            class_name = data.get('class_name', 'FORM 4')
            stream = data.get('stream', '')
            
            generator = SubjectGenerator(
                subject_name=subject_name,
                class_name=class_name,
                stream=stream
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