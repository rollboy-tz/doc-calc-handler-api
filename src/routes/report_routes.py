"""
PDF REPORT GENERATION ROUTES
Uses fpdf2 library for PDF generation
Supports multiple education systems: ACSEE, CSEE, PLSE
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

def transform_api_data_to_report_format(api_response, student_index=0):
    """
    Transform your API response to the format expected by the PDF generator
    
    Supports both formats you provided:
    1. Format with analytics, metadata, students
    2. Simple student data format
    """
    if not api_response.get('success'):
        raise ValueError("API response indicates failure")
    
    # Check if it's the complex format (with analytics)
    if 'students' in api_response and 'metadata' in api_response:
        students = api_response['students']
        if not students:
            raise ValueError("No student data in API response")
        
        # Check if student_index is valid
        if student_index >= len(students):
            raise ValueError(f"Student index {student_index} out of range. Total students: {len(students)}")
        
        # Use specified student for individual report
        selected_student = students[student_index]
        
        # Transform subjects from dict to list
        subjects_list = []
        if 'subjects' in selected_student:
            for subject_name, subject_data in selected_student['subjects'].items():
                if isinstance(subject_data, dict):
                    subject_item = subject_data.copy()
                    subject_item['name'] = subject_name.title().replace('_', ' ')
                    subjects_list.append(subject_item)
        
        # Build student data structure
        transformed = {
            'student': selected_student['student'],
            'summary': selected_student['summary'],
            'subjects': subjects_list
        }
        
        # Extract metadata for class info
        metadata = api_response.get('metadata', {})
        class_info = {
            'class_name': metadata.get('class_id', '').replace('_', ' '),
            'exam_name': metadata.get('exam_id', 'EXAMINATION').replace('_', ' '),
            'term': 'I',  # Default, you might want to extract this from somewhere
            'year': datetime.now().year,
            'system': metadata.get('system', ''),
            'rule': metadata.get('rule', '').lower(),
            'scale': metadata.get('scale', 100)
        }
        
        # Get school info from metadata or use defaults
        school_info = {
            'name': class_info['class_name'].split('_')[0] + ' SCHOOL' if '_' in class_info['class_name'] else 'SCHOOL',
            'address': 'Tanzania',
            'system': class_info['system']
        }
        
        return transformed, class_info, school_info
    
    # If it's already in simple format
    elif 'student_data' in api_response:
        student_data = api_response['student_data']
        class_info = api_response.get('class_info', {})
        school_info = api_response.get('school_info', {})
        
        return student_data, class_info, school_info
    
    else:
        raise ValueError("Unsupported API response format")

# ========== STUDENT REPORT (MAIN ENDPOINT) ==========

@report_bp.route('/api/reports/student', methods=['POST'])
def generate_student_report():
    """
    Generate student academic report PDF
    Supports: ACSEE, CSEE, PLSE systems
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required data
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Extract student index if provided (default to 0 = first student)
        student_index = data.get('student_index', 0)
        
        # Transform data if needed
        if 'students' in data and 'metadata' in data:
            # This is your API response format
            student_data, class_info, school_info = transform_api_data_to_report_format(data, student_index)
            
            # Get system rule from metadata
            system_rule = data['metadata'].get('rule', '').lower()
            system_name = data['metadata'].get('system', '')
            
        elif 'student_data' in data:
            # Already in correct format
            student_data = data['student_data']
            class_info = data.get('class_info', {})
            school_info = data.get('school_info', {})
            
            # Get system rule from config or class_info
            system_rule = data.get('config', {}).get('system_rule', '').lower()
            if not system_rule and 'rule' in class_info:
                system_rule = class_info['rule'].lower()
            
            system_name = class_info.get('system', '')
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid data format. Expected API response or student_data'
            }), 400
        
        # Validate required student fields
        if 'student' not in student_data:
            return jsonify({
                'success': False,
                'error': 'Missing student information'
            }), 400
        
        if 'summary' not in student_data:
            return jsonify({
                'success': False,
                'error': 'Missing performance summary'
            }), 400
        
        # Determine system type for appropriate generator
        if system_rule in ['acsee', 'advanced', 'a-level']:
            generator_type = 'acsee_student_report'
            system_display = 'ADVANCED LEVEL (ACSEE)'
        elif system_rule in ['csee', 'certificate', 'o-level']:
            generator_type = 'csee_student_report'
            system_display = 'ORDINARY LEVEL (CSEE)'
        elif system_rule in ['plse', 'primary', 'standard']:
            generator_type = 'plse_student_report'
            system_display = 'PRIMARY LEVEL (PLSE)'
        else:
            # Default to generic
            generator_type = 'student_report'
            system_display = system_name or 'ACADEMIC REPORT'
        
        # System configuration
        system_config = {
            "system_name": system_display,
            "version": "2.0.0",
            "footer_text": f"Generated on {datetime.now().strftime('%d/%m/%Y %H:%M')} - {system_display}",
            "generated_date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "system_rule": system_rule,
            "confidential": True
        }
        
        # Merge with user config if provided
        user_config = data.get('config', {})
        final_config = {**system_config, **user_config}
        
        # Create generator based on system type
        try:
            generator = PDFGeneratorFactory.create(generator_type, final_config)
        except ValueError as e:
            # Fallback to generic generator
            logger.warning(f"System-specific generator not found, using generic: {e}")
            generator = PDFGeneratorFactory.create('student_report', final_config)
        
        # Generate PDF
        pdf_path = generator.generate(
            student_data=student_data,
            class_info=class_info,
            school_info=school_info
        )
        
        # Create filename
        student = student_data['student']
        admission = student.get('admission', 'unknown').replace(' ', '_').replace('/', '_')
        student_name = student.get('name', 'student').replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{system_rule}_report_{admission}_{student_name}_{timestamp}.pdf"
        
        logger.info(f"Generated {system_display} report: {filename}")
        
        # Return PDF file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate report',
            'details': str(e)[:200]
        }), 500

# ========== TEST ENDPOINTS FOR EACH SYSTEM ==========

@report_bp.route('/api/reports/student/test/acsee', methods=['GET'])
def test_acsee_report():
    """Test endpoint for ACSEE (A-Level) report"""
    try:
        # Sample ACSEE data
        sample_data = {
            "success": True,
            "metadata": {
                "class_id": "FORM6_SCIENCE_2024",
                "exam_id": "ACSEE_MOCK_2024_001",
                "rule": "acsee",
                "scale": 100,
                "system": "ACSEE (Form 6 - A-Level)"
            },
            "students": [
                {
                    "student": {
                        "name": "SARA MWANGA",
                        "admission": "F6/002/2024",
                        "gender": "F",
                        "id": "ACSEE2024002"
                    },
                    "summary": {
                        "total": 317,
                        "average": 79,
                        "grade": "B",
                        "division": "III",
                        "points": 9,
                        "principals": 2,
                        "rank": 1,
                        "remark": "Very Good",
                        "status": "PASS",
                        "subjects_attended": 4,
                        "subjects_passed": 4,
                        "subjects_total": 11
                    },
                    "subjects": {
                        "biology": {
                            "attended": True,
                            "grade": "A",
                            "marks": 85,
                            "pass": True,
                            "points": 5,
                            "remark": "Excellent",
                            "subject_rank": 1
                        },
                        "chemistry": {
                            "attended": True,
                            "grade": "A",
                            "marks": 82,
                            "pass": True,
                            "points": 5,
                            "remark": "Excellent",
                            "subject_rank": 1
                        },
                        "physics": {
                            "attended": True,
                            "grade": "B",
                            "marks": 78,
                            "pass": True,
                            "points": 4,
                            "remark": "Very Good",
                            "subject_rank": 2
                        },
                        "general_studies": {
                            "attended": True,
                            "grade": "B",
                            "marks": 72,
                            "pass": True,
                            "points": 4,
                            "remark": "Very Good",
                            "subject_rank": 1
                        }
                    }
                }
            ]
        }
        
        # Generate ACSEE PDF
        student_data, class_info, school_info = transform_api_data_to_report_format(sample_data)
        
        config = {
            "system_name": "ACSEE TEST",
            "system_rule": "acsee",
            "footer_text": "TEST REPORT - ACSEE (A-Level) Sample"
        }
        
        generator = PDFGeneratorFactory.create('acsee_student_report', config)
        pdf_path = generator.generate(student_data, class_info, school_info)
        
        filename = "test_acsee_report.pdf"
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"ACSEE test error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/reports/student/test/csee', methods=['GET'])
def test_csee_report():
    """Test endpoint for CSEE (O-Level) report"""
    try:
        # Sample CSEE data
        sample_data = {
            "success": True,
            "metadata": {
                "class_id": "FORM4_SCIENCE_2024",
                "exam_id": "CSEE_MOCK_2024_001",
                "rule": "csee",
                "scale": 100,
                "system": "CSEE (Form 4 - O-Level)"
            },
            "students": [
                {
                    "student": {
                        "name": "MARY JUMANNE",
                        "admission": "F4/002/2024",
                        "gender": "F",
                        "id": "CSEE2024002"
                    },
                    "summary": {
                        "total": 726,
                        "average": 80,
                        "grade": "B",
                        "division": "I",
                        "points": 13,
                        "rank": 1,
                        "remark": "Very Good",
                        "status": "PASS",
                        "subjects_attended": 9,
                        "subjects_passed": 9,
                        "subjects_total": 9
                    },
                    "subjects": {
                        "mathematics": {
                            "attended": True,
                            "grade": "B",
                            "marks": 72,
                            "pass": True,
                            "points": 2,
                            "remark": "Very Good",
                            "subject_rank": 2
                        },
                        "english": {
                            "attended": True,
                            "grade": "A",
                            "marks": 88,
                            "pass": True,
                            "points": 1,
                            "remark": "Excellent",
                            "subject_rank": 1
                        },
                        "kiswahili": {
                            "attended": True,
                            "grade": "A",
                            "marks": 91,
                            "pass": True,
                            "points": 1,
                            "remark": "Excellent",
                            "subject_rank": 1
                        }
                    }
                }
            ]
        }
        
        # Generate CSEE PDF
        student_data, class_info, school_info = transform_api_data_to_report_format(sample_data)
        
        config = {
            "system_name": "CSEE TEST",
            "system_rule": "csee",
            "footer_text": "TEST REPORT - CSEE (O-Level) Sample"
        }
        
        generator = PDFGeneratorFactory.create('csee_student_report', config)
        pdf_path = generator.generate(student_data, class_info, school_info)
        
        filename = "test_csee_report.pdf"
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"CSEE test error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/reports/student/test/plse', methods=['GET'])
def test_plse_report():
    """Test endpoint for PLSE (Primary) report"""
    try:
        # Sample PLSE data
        sample_data = {
            "success": True,
            "metadata": {
                "class_id": "STD7_A_2024",
                "exam_id": "PLSE_MOCK_2024_001",
                "rule": "plse",
                "scale": 50,
                "system": "PLSE (Std 7 - Primary)"
            },
            "students": [
                {
                    "student": {
                        "name": "GRACE MBOGO",
                        "admission": "P7/002/2024",
                        "gender": "F",
                        "id": "PLSE2024002"
                    },
                    "summary": {
                        "total": 253,
                        "average": 42,
                        "grade": "A",
                        "rank": 1,
                        "remark": "Excellent",
                        "status": "PASS",
                        "subjects_attended": 6,
                        "subjects_passed": 6,
                        "subjects_total": 6
                    },
                    "subjects": {
                        "mathematics": {
                            "attended": True,
                            "grade": "A",
                            "marks": 48,
                            "pass": True,
                            "points": None,
                            "remark": "Excellent",
                            "subject_rank": 1
                        },
                        "english": {
                            "attended": True,
                            "grade": "A",
                            "marks": 41,
                            "pass": True,
                            "points": None,
                            "remark": "Excellent",
                            "subject_rank": 1
                        },
                        "kiswahili": {
                            "attended": True,
                            "grade": "B",
                            "marks": 39,
                            "pass": True,
                            "points": None,
                            "remark": "Very Good",
                            "subject_rank": 1
                        }
                    }
                }
            ]
        }
        
        # Generate PLSE PDF
        student_data, class_info, school_info = transform_api_data_to_report_format(sample_data)
        
        config = {
            "system_name": "PLSE TEST",
            "system_rule": "plse",
            "footer_text": "TEST REPORT - PLSE (Primary) Sample"
        }
        
        generator = PDFGeneratorFactory.create('plse_student_report', config)
        pdf_path = generator.generate(student_data, class_info, school_info)
        
        filename = "test_plse_report.pdf"
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"PLSE test error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== BATCH REPORTS ==========

@report_bp.route('/api/reports/students/batch', methods=['POST'])
def generate_batch_reports():
    """
    Generate PDF reports for multiple students
    Returns ZIP file containing all reports
    """
    try:
        import zipfile
        import io
        
        data = request.get_json()
        
        if not data or 'students' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing students data'
            }), 400
        
        # Get metadata for system detection
        metadata = data.get('metadata', {})
        system_rule = metadata.get('rule', '').lower()
        
        # Determine generator type
        if system_rule in ['acsee', 'advanced', 'a-level']:
            generator_type = 'acsee_student_report'
        elif system_rule in ['csee', 'certificate', 'o-level']:
            generator_type = 'csee_student_report'
        elif system_rule in ['plse', 'primary', 'standard']:
            generator_type = 'plse_student_report'
        else:
            generator_type = 'student_report'
        
        # Create config
        config = {
            "system_rule": system_rule,
            "system_name": metadata.get('system', 'BATCH REPORTS'),
            "footer_text": f"Batch generated on {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        }
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Generate report for each student
            students = data['students']
            for i, student_item in enumerate(students):
                try:
                    # Transform student data
                    student_data = {
                        'student': student_item['student'],
                        'summary': student_item['summary'],
                        'subjects': student_item.get('subjects', {})
                    }
                    
                    # Create class info
                    class_info = {
                        'class_name': metadata.get('class_id', '').replace('_', ' '),
                        'exam_name': metadata.get('exam_id', 'EXAMINATION'),
                        'system': metadata.get('system', ''),
                        'rule': system_rule
                    }
                    
                    # Create school info
                    school_info = {
                        'name': class_info['class_name'].split('_')[0] + ' SCHOOL' if '_' in class_info['class_name'] else 'SCHOOL'
                    }
                    
                    # Generate PDF
                    generator = PDFGeneratorFactory.create(generator_type, config)
                    pdf_path = generator.generate(student_data, class_info, school_info)
                    
                    # Read PDF and add to ZIP
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_content = pdf_file.read()
                    
                    # Create filename
                    student = student_item['student']
                    admission = student.get('admission', f'student_{i}').replace(' ', '_').replace('/', '_')
                    student_name = student.get('name', f'student_{i}').replace(' ', '_')
                    filename = f"{system_rule}_report_{admission}_{student_name}.pdf"
                    
                    zip_file.writestr(filename, pdf_content)
                    
                    # Clean up temp file
                    os.unlink(pdf_path)
                    
                except Exception as e:
                    logger.error(f"Error generating report for student {i}: {e}")
                    continue
        
        zip_buffer.seek(0)
        
        # Create ZIP filename
        class_name = metadata.get('class_id', 'reports').replace('_', ' ')
        zip_filename = f"batch_reports_{class_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=zip_filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        logger.error(f"Batch reports error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate batch reports',
            'details': str(e)[:200]
        }), 500

# ========== SERVICE INFO ENDPOINTS ==========

@report_bp.route('/api/reports/types', methods=['GET'])
def get_report_types():
    """Get available report types"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'supported_systems': [
                    {
                        'id': 'acsee',
                        'name': 'ACSEE (Advanced Level)',
                        'description': 'Form 5-6 A-Level reports with divisions and points',
                        'test_endpoint': 'GET /api/reports/student/test/acsee'
                    },
                    {
                        'id': 'csee',
                        'name': 'CSEE (Ordinary Level)',
                        'description': 'Form 1-4 O-Level reports with divisions and points',
                        'test_endpoint': 'GET /api/reports/student/test/csee'
                    },
                    {
                        'id': 'plse',
                        'name': 'PLSE (Primary Level)',
                        'description': 'Std 1-7 Primary reports without divisions/points',
                        'test_endpoint': 'GET /api/reports/student/test/plse'
                    }
                ],
                'endpoints': {
                    'main': 'POST /api/reports/student - Generate individual report',
                    'batch': 'POST /api/reports/students/batch - Generate batch reports (ZIP)',
                    'validate': 'POST /api/reports/validate - Validate data before generation',
                    'health': 'GET /api/reports/health - Service health check'
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@report_bp.route('/api/reports/health', methods=['GET'])
def pdf_service_health():
    """PDF service health check"""
    try:
        # Test all system generators
        systems = [
            ('acsee_student_report', 'ACSEE'),
            ('csee_student_report', 'CSEE'),
            ('plse_student_report', 'PLSE')
        ]
        
        results = []
        for generator_type, system_name in systems:
            try:
                config = {"system_name": f"HEALTH CHECK - {system_name}"}
                generator = PDFGeneratorFactory.create(generator_type, config)
                results.append({
                    'system': system_name,
                    'status': 'healthy',
                    'generator': generator_type
                })
            except Exception as e:
                results.append({
                    'system': system_name,
                    'status': 'unhealthy',
                    'error': str(e)
                })
        
        # Check if all systems are healthy
        all_healthy = all(r['status'] == 'healthy' for r in results)
        
        return jsonify({
            'success': True,
            'service': 'pdf-generation',
            'status': 'healthy' if all_healthy else 'degraded',
            'engine': 'fpdf2',
            'systems': results,
            'timestamp': datetime.now().isoformat(),
            'message': 'PDF generation service status'
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

@report_bp.route('/api/reports/validate', methods=['POST'])
def validate_report_data():
    """Validate student report data before generating PDF"""
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
        system_info = {}
        
        # Detect system from metadata
        if 'metadata' in data:
            metadata = data['metadata']
            system_rule = metadata.get('rule', '').lower()
            system_name = metadata.get('system', '')
            
            if system_rule:
                system_info['detected_system'] = system_rule.upper()
                system_info['system_name'] = system_name
                
                # Validate system-specific requirements
                if system_rule == 'acsee':
                    if 'students' in data:
                        for student in data['students']:
                            if 'summary' in student:
                                summary = student['summary']
                                if 'principals' not in summary:
                                    warnings.append("ACSEE reports typically include 'principals' count")
                                if 'division' not in summary:
                                    warnings.append("ACSEE reports require 'division'")
                
                elif system_rule == 'csee':
                    if 'students' in data:
                        for student in data['students']:
                            if 'summary' in student:
                                summary = student['summary']
                                if 'division' not in summary:
                                    warnings.append("CSEE reports require 'division'")
                
                elif system_rule == 'plse':
                    if 'students' in data:
                        for student in data['students']:
                            if 'summary' in student:
                                summary = student['summary']
                                if 'division' in summary and summary['division']:
                                    warnings.append("PLSE reports typically don't have divisions")
        
        # General validation
        if 'students' in data:
            students = data['students']
            if not students:
                errors.append("No students in data")
            else:
                for i, student in enumerate(students):
                    if 'student' not in student:
                        errors.append(f"Student {i}: Missing 'student' information")
                    else:
                        if not student['student'].get('name'):
                            errors.append(f"Student {i}: Name is required")
                        if not student['student'].get('admission'):
                            errors.append(f"Student {i}: Admission number is required")
                    
                    if 'summary' not in student:
                        errors.append(f"Student {i}: Missing 'summary' section")
                    else:
                        summary = student['summary']
                        if summary.get('average') is None:
                            errors.append(f"Student {i}: Average score is required")
                        if not summary.get('grade'):
                            errors.append(f"Student {i}: Grade is required")
        
        elif 'student_data' in data:
            student_data = data['student_data']
            if 'student' not in student_data:
                errors.append("Missing 'student' information")
            else:
                if not student_data['student'].get('name'):
                    errors.append("Student name is required")
                if not student_data['student'].get('admission'):
                    errors.append("Admission number is required")
            
            if 'summary' not in student_data:
                errors.append("Missing 'summary' section")
            else:
                summary = student_data['summary']
                if summary.get('average') is None:
                    errors.append("Average score is required")
                if not summary.get('grade'):
                    errors.append("Grade is required")
        else:
            errors.append("No student data found")
        
        if errors:
            return jsonify({
                'success': True,
                'valid': False,
                'system_info': system_info,
                'errors': errors,
                'warnings': warnings,
                'message': 'Data validation failed'
            })
        
        return jsonify({
            'success': True,
            'valid': True,
            'system_info': system_info,
            'warnings': warnings,
            'message': 'Data is valid for PDF generation'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'valid': False,
            'error': str(e)
        }), 500