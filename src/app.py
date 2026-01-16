"""
EduSaaS Python Calculation Engine
Simple Flask API for grade calculations and report generation
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# =============================================
# HEALTH CHECK ENDPOINT
# =============================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if Python service is running"""
    return jsonify({
        'status': 'healthy',
        'service': 'EduSaaS Python Calculation Engine',
        'python_version': sys.version.split()[0],
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'endpoints': {
            'health': 'GET /api/health',
            'calculate_grades': 'POST /api/calculate/grades',
            'generate_report': 'POST /api/generate/report',
            'test_calculation': 'GET /api/test/calculation'
        }
    })

# =============================================
# TEST CALCULATION ENDPOINT
# =============================================
@app.route('/api/test/calculation', methods=['GET'])
def test_calculation():
    """Test endpoint to verify calculations work"""
    test_marks = [85, 90, 78, 92, 88, 75, 95, 80]
    
    # Simple calculation
    average = sum(test_marks) / len(test_marks)
    
    # Grade mapping
    if average >= 80:
        grade = 'A'
        remark = 'Excellent'
    elif average >= 70:
        grade = 'B+'
        remark = 'Very Good'
    elif average >= 60:
        grade = 'B'
        remark = 'Good'
    elif average >= 50:
        grade = 'C'
        remark = 'Satisfactory'
    else:
        grade = 'D'
        remark = 'Needs Improvement'
    
    return jsonify({
        'test_data': test_marks,
        'results': {
            'average': round(average, 2),
            'grade': grade,
            'remark': remark,
            'total_students': len(test_marks),
            'highest_score': max(test_marks),
            'lowest_score': min(test_marks)
        },
        'calculated_by': 'Python Calculation Engine',
        'note': 'This is a test calculation'
    })

# =============================================
# GRADE CALCULATION ENDPOINT
# =============================================
@app.route('/api/calculate/grades', methods=['POST'])
def calculate_grades():
    """Calculate grades from marks"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        marks = data.get('marks', [])
        grading_system = data.get('grading_system', 'tanzania')
        
        if not marks:
            return jsonify({
                'status': 'error',
                'message': 'Marks array is required'
            }), 400
        
        # Convert to list if not already
        if not isinstance(marks, list):
            marks = [marks]
        
        # Basic calculations
        total_marks = sum(marks)
        average = total_marks / len(marks)
        
        # Determine grade based on system
        if grading_system == 'tanzania':
            grade, remark = get_tanzania_grade(average)
        elif grading_system == 'international':
            grade, remark = get_international_grade(average)
        else:
            grade, remark = get_tanzania_grade(average)
        
        # Statistics
        passed = sum(1 for mark in marks if mark >= 40)
        failed = len(marks) - passed
        
        return jsonify({
            'status': 'success',
            'data': {
                'summary': {
                    'total_students': len(marks),
                    'average_score': round(average, 2),
                    'total_marks': total_marks,
                    'passed': passed,
                    'failed': failed,
                    'pass_rate': round((passed / len(marks)) * 100, 2)
                },
                'grade_info': {
                    'grade': grade,
                    'remark': remark,
                    'grading_system': grading_system
                },
                'statistics': {
                    'highest': max(marks),
                    'lowest': min(marks),
                    'range': max(marks) - min(marks),
                    'median': calculate_median(marks)
                }
            },
            'calculated_by': 'Python Engine',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# =============================================
# REPORT GENERATION ENDPOINT
# =============================================
@app.route('/api/generate/report', methods=['POST'])
def generate_report():
    """Generate a simple report (PDF simulation)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        report_type = data.get('type', 'student_report')
        student_name = data.get('student_name', 'Student')
        marks = data.get('marks', {})
        
        # Simulate PDF generation
        report_id = f"REPORT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return jsonify({
            'status': 'success',
            'data': {
                'report_id': report_id,
                'report_type': report_type,
                'student_name': student_name,
                'download_url': f'/reports/{report_id}.pdf',
                'preview_url': f'/reports/{report_id}/preview',
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'pages': 2,
                'file_size': '450KB'
            },
            'note': 'PDF generation simulated. Actual PDF would be generated with ReportLab.',
            'next_steps': [
                'Download report from download_url',
                'View preview from preview_url',
                'Store report_id for future reference'
            ]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# =============================================
# HELPER FUNCTIONS
# =============================================
def get_tanzania_grade(average):
    """Tanzania grading system"""
    if average >= 80:
        return 'A', 'Excellent'
    elif average >= 70:
        return 'B+', 'Very Good'
    elif average >= 60:
        return 'B', 'Good'
    elif average >= 50:
        return 'C', 'Satisfactory'
    elif average >= 40:
        return 'D', 'Pass'
    else:
        return 'E', 'Fail'

def get_international_grade(average):
    """International grading system"""
    if average >= 90:
        return 'A+', 'Outstanding'
    elif average >= 80:
        return 'A', 'Excellent'
    elif average >= 70:
        return 'B', 'Good'
    elif average >= 60:
        return 'C', 'Satisfactory'
    elif average >= 50:
        return 'D', 'Pass'
    else:
        return 'F', 'Fail'

def calculate_median(numbers):
    """Calculate median of a list"""
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    mid = n // 2
    
    if n % 2 == 0:
        return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2
    else:
        return sorted_numbers[mid]

# =============================================
# MAIN EXECUTION
# =============================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)