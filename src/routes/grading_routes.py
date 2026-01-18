# routes/grading_routes.py
"""
GRADING PROCESSING ROUTES
"""
from flask import Blueprint, request, jsonify
from services.grading.grade_calculator import GradeCalculator
from services.grading.result_builder import ResultBuilder
import datetime

grading_routes = Blueprint('grading', __name__)


@grading_routes.route('/api/grading/process', methods=['POST'])
def process_grades():
    """Process extracted data into grades"""
    try:
        data = request.json
        
        # Validate request
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided',
                'timestamp': datetime.datetime.now().isoformat()
            }), 400
        
        if 'extracted_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing extracted_data field',
                'timestamp': datetime.datetime.now().isoformat()
            }), 400
        
        extracted_data = data['extracted_data']
        external_ids = data.get('external_ids', {})
        
        # Validate required IDs
        if not external_ids.get('exam_id'):
            return jsonify({
                'success': False,
                'error': 'exam_id is required in external_ids',
                'timestamp': datetime.datetime.now().isoformat()
            }), 400
        
        if not external_ids.get('class_id'):
            return jsonify({
                'success': False,
                'error': 'class_id is required in external_ids',
                'timestamp': datetime.datetime.now().isoformat()
            }), 400
        
        # Get grading system
        grading_system = external_ids.get('grading_rule', 'csee')
        
        # Process grades
        calculator = GradeCalculator(system=grading_system)
        results = calculator.process_class_results(
            extracted_data=extracted_data,
            external_ids=external_ids
        )
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.datetime.now().isoformat()
        }), 500


@grading_routes.route('/api/grading/systems', methods=['GET'])
def get_grading_systems():
    """Get available grading systems"""
    from services.grading.grading_rules import GRADING_SYSTEMS
    
    systems = []
    for key, system in GRADING_SYSTEMS.items():
        systems.append({
            'id': key,
            'name': system['name'],
            'grades': [g['grade'] for g in system['grades']]
        })
    
    return jsonify({
        'success': True,
        'systems': systems,
        'timestamp': datetime.datetime.now().isoformat()
    })


@grading_routes.route('/api/grading/format/database', methods=['POST'])
def format_for_database():
    """Format results for database storage"""
    try:
        data = request.json
        
        if not data or 'results' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing results data',
                'timestamp': datetime.datetime.now().isoformat()
            }), 400
        
        formatted = ResultBuilder.format_for_database(data['results'])
        
        return jsonify({
            'success': True,
            'formatted_data': formatted,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.datetime.now().isoformat()
        }), 500


@grading_routes.route('/api/grading/summary', methods=['POST'])
def get_summary():
    """Get summary report"""
    try:
        data = request.json
        
        if not data or 'results' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing results data',
                'timestamp': datetime.datetime.now().isoformat()
            }), 400
        
        summary = ResultBuilder.create_summary_report(data['results'])
        
        return jsonify({
            'success': True,
            'summary': summary,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.datetime.now().isoformat()
        }), 500


@grading_routes.route('/api/grading/test', methods=['POST'])
def test_grading():
    """Test endpoint with sample data"""
    sample_request = {
        "extracted_data": {
            "data": [
                {
                    "student_id": "STU001",
                    "admission_no": "ADM001",
                    "full_name": "JOHN MWALIMU",
                    "gender": "M",
                    "mathematics": 85,
                    "english": 78,
                    "physics": 65
                },
                {
                    "student_id": "STU002",
                    "admission_no": "ADM002",
                    "full_name": "MARY JUMANNE",
                    "gender": "F",
                    "mathematics": 72,
                    "english": 88,
                    "physics": 91
                }
            ],
            "metadata": {
                "subject_columns": ["mathematics", "english", "physics"],
                "student_count": 2
            }
        },
        "external_ids": {
            "exam_id": "EXAM_2024_TERM1_001",
            "class_id": "CLASS_FORM4_SCIENCE_001",
            "stream_id": "STREAM_SCIENCE_001",
            "grading_rule": "csee",
            "subject_ids": {
                "mathematics": "SUBJ_MATH_001",
                "english": "SUBJ_ENG_002",
                "physics": "SUBJ_PHY_003"
            }
        }
    }
    
    calculator = GradeCalculator(system="csee")
    results = calculator.process_class_results(
        extracted_data=sample_request["extracted_data"],
        external_ids=sample_request["external_ids"]
    )
    
    return jsonify(results)