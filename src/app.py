"""
PURE API GATEWAY ROUTER - Tanzania School Management System
Only handles: Security, Routing, Request/Response
Business logic in handler modules
"""
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import tempfile
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import middleware
from middleware.security import SecurityMiddleware

# Initialize Flask app
app = Flask(__name__)

# CORS Configuration
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')
if ALLOWED_ORIGINS and ALLOWED_ORIGINS[0]:
    CORS(app, origins=ALLOWED_ORIGINS)
    logger.info(f"CORS allowed for: {ALLOWED_ORIGINS}")
else:
    CORS(app)
    logger.warning("ALLOWED_ORIGINS not set - allowing all origins")

# Initialize security middleware
security = SecurityMiddleware(app)

# ==================== GLOBAL MIDDLEWARE ====================
@app.before_request
def global_middleware():
    """Global middleware for all requests"""
    # Apply security checks
    security_result = security.check_request(request)
    if security_result.get('blocked'):
        return jsonify({
            "success": False,
            "error": security_result['error'],
            "message": security_result['message']
        }), security_result.get('code', 403)
    
    # Log request
    logger.info(f"📨 {request.method} {request.path} from {request.remote_addr}")

# Import our services (ADD NEW IMPORTS HERE)
from services.documents.marksheet_template import MarkSheetTemplate
from services.documents.subject_marksheet import SubjectMarkSheet
from services.upload_handlers.single_subject_upload import SingleSubjectUploadHandler
from services.upload_handlers.single_subject_json_upload import SingleSubjectJSONUploadHandler
from services.upload_handlers.multi_subject_upload import MultiSubjectUploadHandler
from services.upload_handlers.multi_subject_json_upload import MultiSubjectJSONUploadHandler

# ==================== HEALTH & INFO ====================
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "School Management API",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }), 200

@app.route('/api/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "Tanzania School Management System API",
        "version": "2.0.0",
        "description": "Tanzania NECTA Grading System",
        "grading_systems": ["CSEE", "PSLE"],
        "endpoints": {
            "templates": {
                "/api/templates/full": "Download full mark sheet template",
                "/api/templates/subject": "Download single subject template",
                "/api/templates/info": "Get template information"
            },
            "processing": {
                "/api/process/single-subject/excel": "Process single subject Excel",
                "/api/process/single-subject/json": "Process single subject JSON",
                "/api/process/multi-subject/excel": "Process multiple subjects Excel",
                "/api/process/multi-subject/json": "Process multiple subjects JSON"
            },
            "debug": {
                "/api/debug/excel": "Debug Excel file structure"
            },
            "utility": {
                "/health": "Health check",
                "/api/info": "API information"
            }
        }
    }), 200

# ==================== TEMPLATE ENDPOINTS ====================
@app.route('/api/templates/full', methods=['POST'])
def download_full_template():
    """Download FULL mark sheet template (all subjects)"""
    try:
        data = request.json
        
        if not data or 'students' not in data:
            return jsonify({
                "success": False,
                "error": "Missing student data",
                "message": "Please provide student list"
            }), 400
        
        students = data.get('students', [])
        class_info = data.get('class_info', {})
        subjects = data.get('subjects', [
            'Mathematics', 'English', 'Kiswahili', 
            'Science', 'Geography', 'History', 
            'Civics', 'Commerce', 'Bookkeeping'
        ])
        
        if not students:
            return jsonify({
                "success": False,
                "error": "Empty student list",
                "message": "Student list cannot be empty"
            }), 400
        
        # Create template
        template = MarkSheetTemplate(
            student_list=students,
            class_info=class_info,
            subjects=subjects
        )
        
        template.generate()
        excel_bytes = template.to_excel_bytes()
        filename = template._generate_filename()
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_file.write(excel_bytes.getvalue())
        temp_file.close()
        
        # Return file
        return send_file(
            temp_file.name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Full template error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/templates/subject', methods=['POST'])
def download_subject_template():
    """Download SINGLE subject mark sheet template"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        students = data.get('students', [])
        subject_info = data.get('subject_info', {})
        
        if not students:
            return jsonify({
                "success": False,
                "error": "No students provided"
            }), 400
        
        if not subject_info.get('name'):
            return jsonify({
                "success": False,
                "error": "Subject name required"
            }), 400
        
        # Create template
        template = SubjectMarkSheet(
            student_list=students,
            subject_info=subject_info
        )
        
        template.generate()
        excel_bytes = template.to_excel_bytes()
        filename = template._generate_filename()
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_file.write(excel_bytes.getvalue())
        temp_file.close()
        
        # Return file
        return send_file(
            temp_file.name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Subject template error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/templates/info', methods=['POST'])
def get_template_info():
    """Get template information without downloading"""
    try:
        data = request.json
        template_type = data.get('type', 'subject')
        
        if template_type == 'subject':
            subject_info = data.get('subject_info', {})
            students = data.get('students', [])
            
            template = SubjectMarkSheet(
                student_list=students,
                subject_info=subject_info
            )
            info = template.get_template_summary()
            
        elif template_type == 'full':
            class_info = data.get('class_info', {})
            subjects = data.get('subjects', [])
            students = data.get('students', [])
            
            template = MarkSheetTemplate(
                student_list=students,
                class_info=class_info,
                subjects=subjects
            )
            info = template.get_template_summary()
        
        else:
            return jsonify({
                "success": False,
                "error": "Invalid template type. Use 'subject' or 'full'"
            }), 400
        
        return jsonify({
            "success": True,
            "template_type": template_type,
            "template_info": info
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== DEBUG ENDPOINTS ====================
@app.route('/api/debug/excel', methods=['POST'])
def debug_excel_file():
    """Debug Excel file structure"""
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file uploaded"
            }), 400
        
        file = request.files['file']
        
        # Save temp file
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        file.save(temp_path.name)
        
        # Read Excel with header row 1
        df = pd.read_excel(temp_path.name, header=1)
        
        # Get column info
        columns_found = df.columns.tolist()
        
        # Normalize column names
        def normalize(col):
            return str(col).lower().strip().replace(' ', '_')
        
        normalized_columns = [normalize(col) for col in columns_found]
        
        # Check for required columns
        required_columns = ['admission_no', 'student_id', 'full_name', 'gender']
        missing_columns = []
        
        for req in required_columns:
            if req not in normalized_columns:
                missing_columns.append(req)
        
        # Sample data
        sample_data = []
        for i in range(min(3, len(df))):
            row = {}
            for col in df.columns:
                value = df.iloc[i][col]
                row[col] = str(value) if not pd.isna(value) else None
            sample_data.append(row)
        
        # Clean up
        os.unlink(temp_path.name)
        
        return jsonify({
            "success": True,
            "file_info": {
                "filename": file.filename,
                "row_count": len(df),
                "column_count": len(columns_found),
                "columns": columns_found,
                "normalized_columns": normalized_columns,
                "required_columns_check": {
                    "admission_no": "admission_no" in normalized_columns,
                    "student_id": "student_id" in normalized_columns,
                    "full_name": "full_name" in normalized_columns,
                    "gender": "gender" in normalized_columns
                },
                "missing_columns": missing_columns,
                "sample_data": sample_data
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== SINGLE SUBJECT PROCESSING ====================
@app.route('/api/process/single-subject/excel', methods=['POST'])
def process_single_subject_excel():
    """Process single subject Excel upload"""
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file uploaded"
            }), 400
        
        file = request.files['file']
        
        # Get parameters
        subject_name = request.form.get('subject_name', 'Mathematics')
        max_score = int(request.form.get('max_score', 100))
        grading_rules = request.form.get('grading_rules', 'CSEE')
        
        # Save uploaded file temporarily
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        file.save(temp_path.name)
        
        # Initialize handler
        handler = SingleSubjectUploadHandler(
            subject_name=subject_name,
            max_score=max_score,
            grading_rules=grading_rules
        )
        
        # Process upload
        result = handler.process_upload(temp_path.name)
        
        # Clean up temp file
        os.unlink(temp_path.name)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Single subject Excel error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/process/single-subject/json', methods=['POST'])
def process_single_subject_json():
    """Process single subject JSON data"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        # Get parameters
        subject_name = request.args.get('subject', 'Mathematics')
        max_score = int(request.args.get('max_score', 100))
        grading_rules = request.args.get('grading_rules', 'CSEE')
        
        # Initialize handler
        handler = SingleSubjectJSONUploadHandler(
            subject_name=subject_name,
            max_score=max_score,
            grading_rules=grading_rules
        )
        
        # Process JSON
        result = handler.process_json(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Single subject JSON error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/json-structure/single-subject', methods=['GET'])
def get_single_subject_json_structure():
    """Get expected JSON structure for single subject"""
    subject = request.args.get('subject', 'Mathematics')
    grading_rules = request.args.get('grading_rules', 'CSEE')
    max_score = int(request.args.get('max_score', 100))
    
    handler = SingleSubjectJSONUploadHandler(
        subject_name=subject,
        max_score=max_score,
        grading_rules=grading_rules
    )
    
    return jsonify(handler.get_expected_structure())

# ==================== MULTI SUBJECT PROCESSING ====================
@app.route('/api/process/multi-subject/excel', methods=['POST'])
def process_multi_subject_excel():
    """Process multiple subjects Excel upload"""
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "No file uploaded"
            }), 400
        
        file = request.files['file']
        
        # Get subjects from form
        subjects_str = request.form.get('subjects', '')
        subjects = [s.strip() for s in subjects_str.split(',')] if subjects_str else []
        grading_rules = request.form.get('grading_rules', 'CSEE')
        
        # Save uploaded file temporarily
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        file.save(temp_path.name)
        
        # If subjects not provided, detect from file
        if not subjects:
            df = pd.read_excel(temp_path.name, header=1)
            all_columns = df.columns.tolist()
            base_columns = ['admission_no', 'student_id', 'full_name', 'gender', 'class', 'stream', 'Remarks']
            subjects = [col for col in all_columns if col not in base_columns]
        
        if not subjects:
            os.unlink(temp_path.name)
            return jsonify({
                "success": False,
                "error": "No subjects found in file or provided"
            }), 400
        
        # Initialize handler
        handler = MultiSubjectUploadHandler(
            subjects=subjects,
            grading_rules=grading_rules
        )
        
        # Process upload
        result = handler.process_upload(temp_path.name)
        
        # Clean up temp file
        os.unlink(temp_path.name)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Multi subject Excel error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/process/multi-subject/json', methods=['POST'])
def process_multi_subject_json():
    """Process multiple subjects JSON data"""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        # Get parameters
        subjects_str = request.args.get('subjects', '')
        subjects = [s.strip() for s in subjects_str.split(',')] if subjects_str else []
        grading_rules = request.args.get('grading_rules', 'CSEE')
        
        # If subjects not in URL, detect from first student
        if not subjects and isinstance(data, list) and len(data) > 0:
            first_student = data[0]
            if isinstance(first_student.get('subjects'), dict):
                subjects = list(first_student['subjects'].keys())
        
        if not subjects:
            return jsonify({
                "success": False,
                "error": "No subjects specified"
            }), 400
        
        # Initialize handler
        handler = MultiSubjectJSONUploadHandler(
            subjects=subjects,
            grading_rules=grading_rules
        )
        
        # Process JSON
        result = handler.process_json(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Multi subject JSON error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/json-structure/multi-subject', methods=['GET'])
def get_multi_subject_json_structure():
    """Get expected JSON structure for multiple subjects"""
    subjects_str = request.args.get('subjects', 'Mathematics,English,Kiswahili,Science,Geography')
    subjects = [s.strip() for s in subjects_str.split(',')]
    grading_rules = request.args.get('grading_rules', 'CSEE')
    
    handler = MultiSubjectJSONUploadHandler(
        subjects=subjects,
        grading_rules=grading_rules
    )
    
    return jsonify(handler.get_expected_structure())

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "endpoint_not_found",
        "message": "The requested endpoint does not exist"
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "success": False,
        "error": "method_not_allowed",
        "message": f"Method {request.method} is not allowed for this endpoint"
    }), 405

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({
        "success": False,
        "error": "internal_server_error",
        "message": "An internal server error occurred"
    }), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    
    logger.info("=" * 50)
    logger.info("🚀 Tanzania School Management API Starting...")
    logger.info(f"📡 Port: {port}")
    logger.info(f"🇹🇿 Grading System: NECTA (CSEE/PSLE)")
    logger.info(f"📊 Endpoints: 12 available")
    logger.info("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('DEBUG', 'False').lower() == 'true'
    )