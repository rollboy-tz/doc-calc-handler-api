# routes/extractor_routes.py
"""
EXCEL EXTRACTION ROUTES
"""
from flask import Blueprint, request, jsonify
import tempfile
import os
from services.validators.excel_validator import ExcelValidator
from services.extractors.multi_subject_extractor import MultiSubjectExtractor
from services.extractors.single_subject_extractor import SingleSubjectExtractor

extractor_routes = Blueprint('extractors', __name__)

@extractor_routes.route('/api/extract/multi-subject', methods=['POST'])
def extract_multi_subject():
    """Extract data from multi-subject Excel file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False, 
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        # Save to temp file
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        file.save(temp_path.name)
        
        # 1. Validate
        validator = ExcelValidator()
        if not validator.validate(temp_path.name):
            os.unlink(temp_path.name)
            return jsonify({
                'success': False,
                'error': 'File validation failed',
                'details': validator.get_errors()
            }), 400
        
        # 2. Extract
        extractor = MultiSubjectExtractor(temp_path.name)
        result = extractor.extract()
        
        # 3. Clean up
        os.unlink(temp_path.name)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@extractor_routes.route('/api/extract/single-subject', methods=['POST'])
def extract_single_subject():
    """Extract data from single subject Excel file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False, 
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        subject_name = request.form.get('subject_name')
        
        # Save to temp file
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        file.save(temp_path.name)
        
        # 1. Validate
        validator = ExcelValidator()
        if not validator.validate(temp_path.name):
            os.unlink(temp_path.name)
            return jsonify({
                'success': False,
                'error': 'File validation failed',
                'details': validator.get_errors()
            }), 400
        
        # 2. Extract
        extractor = SingleSubjectExtractor(temp_path.name, subject_name)
        result = extractor.extract()
        
        # 3. Clean up
        os.unlink(temp_path.name)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@extractor_routes.route('/api/extract/debug', methods=['POST'])
def debug_extraction():
    """Debug Excel file structure"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file'}), 400
        
        file = request.files['file']
        
        # Save temp file
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        file.save(temp_path.name)
        
        # Try different reading methods
        import pandas as pd
        results = {}
        
        for header_option in [None, 0, 1, 2]:
            try:
                df = pd.read_excel(temp_path.name, header=header_option)
                results[f'header={header_option}'] = {
                    'columns': df.columns.tolist(),
                    'shape': df.shape,
                    'first_row': df.iloc[0].tolist() if len(df) > 0 else []
                }
            except Exception as e:
                results[f'header={header_option}'] = {'error': str(e)}
        
        # Clean up
        os.unlink(temp_path.name)
        
        return jsonify({
            'success': True,
            'debug_info': results,
            'filename': file.filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500