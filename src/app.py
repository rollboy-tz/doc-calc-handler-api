"""
PURE API GATEWAY ROUTER
Only handles: Security, Routing, Request/Response
Business logic will be in handler modules
"""
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import json
import tempfile
from datetime import datetime
import os
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

# CORS Configuration - flexible
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')
if ALLOWED_ORIGINS and ALLOWED_ORIGINS[0]:
    CORS(app, origins=ALLOWED_ORIGINS)
    logger.info(f"CORS allowed for: {ALLOWED_ORIGINS}")
else:
    CORS(app)  # Allow all for now
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

# Import our services
from services.documents.marksheet_template import MarkSheetTemplate
from services.calculations.grade_calculator import GradeCalculator


# ==================== ROUTES ====================
@app.route('/api/template/marksheet', methods=['POST'])
def generate_marksheet_template():
    """Handle document requests"""
    try:
        data = request.json
        
        # Extract data
        students = data.get('students', [])
        class_info = data.get('class_info', {})
        subjects = data.get('subjects', [])
        
        if not students:
            return jsonify({
                "error": "No students provided",
                "message": "Please provide student list"
            }), 400
        
        # Create mark sheet template
        template = MarkSheetTemplate(
            student_list=students,
            class_info=class_info,
            subjects=subjects,
            include_instructions=True
        )
        
        # Generate template
        template.generate()
        
        # Get Excel file as bytes
        excel_bytes = template.to_excel_bytes()
        
        # Generate filename
        filename = template._generate_filename()
        
        # Save to temp file for sending
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
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

@app.route('/api/process/marks', methods=['POST'])
def process_marks():
    """Handle calculation requests"""
    try:
        # Check if file was uploaded
        if 'file' in request.files:
            file = request.files['file']
            
            # Read Excel file
            df = pd.read_excel(file)
            
            # Get parameters from form
            subjects = request.form.get('subjects', '').split(',')
            grading_system = request.form.get('grading_system', 'KCSE')
            
        else:
            # Get JSON data
            data = request.json
            
            df = pd.DataFrame(data.get('students', []))
            subjects = data.get('subjects', [])
            grading_system = data.get('grading_system', 'KCSE')
        
        # Clean up subjects list
        if isinstance(subjects, str):
            subjects = [s.strip() for s in subjects.split(',') if s.strip()]
        
        # Identify subject columns (exclude student info columns)
        student_info_columns = ['admission_no', 'student_id', 'full_name', 'class', 'stream']
        if not subjects:
            # Auto-detect subjects (columns that are not student info)
            all_columns = df.columns.tolist()
            subjects = [col for col in all_columns if col not in student_info_columns]
        
        # Initialize grade calculator
        calculator = GradeCalculator(grading_system=grading_system)
        
        # Process marks
        processed_df = calculator.process_marksheet(df, subjects)
        
        # Get summary
        summary = calculator.get_class_summary(processed_df)
        
        # Convert to JSON response
        response_data = {
            "success": True,
            "summary": summary,
            "students": processed_df.to_dict('records'),
            "metadata": {
                "total_students": len(processed_df),
                "subjects_processed": len(subjects),
                "grading_system": grading_system
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route('/api/template/info', methods=['POST'])
def get_template_info():
    """Get information about template without generating file"""
    try:
        data = request.json
        
        students = data.get('students', [])
        class_info = data.get('class_info', {})
        subjects = data.get('subjects', [])
        
        template = MarkSheetTemplate(
            student_list=students,
            class_info=class_info,
            subjects=subjects
        )
        
        template.generate()
        
        return jsonify({
            "success": True,
            "template_info": template.get_template_info(),
            "metadata": template.get_metadata()
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500



@app.route('/api/process', methods=['POST'])
def process():
    """Generic processing endpoint"""
    try:
        data = request.get_json() or {}
        action = data.get('action', 'unknown')
        
        # TODO: Route to appropriate handler based on action
        # if action == 'generate_pdf':
        #     result = pdf_handler.generate(data)
        # elif action == 'validate_data':
        #     result = validation_handler.validate(data)
        
        return jsonify({
            "success": True,
            "message": f"Process request for action: {action}",
            "data": data,
            "handler": "process",
            "action": action
        }), 200
        
    except Exception as e:
        logger.error(f"Error in process: {str(e)}")
        return jsonify({
            "success": False,
            "error": "process_error",
            "message": str(e)
        }), 500

# ==================== UTILITY ENDPOINTS ====================
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "API Gateway Router",
        "timestamp": os.times().elapsed,
        "allowed_origins": ALLOWED_ORIGINS if ALLOWED_ORIGINS[0] else "ALL"
    }), 200

@app.route('/api/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "Document & Calculation API Gateway",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api/template/marksheet", "method": "POST", "desc": "Get marksheet template file"},
            {"path": "/api/template/info", "method": "POST", "desc": "Get information about template without generating file"},
            {"path": "/api/process/marks", "method": "POST", "desc": "Process uploaded marks and calculate grades"},
            {"path": "/api/process", "method": "POST", "desc": "Generic processing"},
            {"path": "/health", "method": "GET", "desc": "Health check"},
            {"path": "/api/info", "method": "GET", "desc": "API information"}
        ],
        "security": {
            "api_key_required": bool(os.getenv('API_KEY')),
            "allowed_origins": ALLOWED_ORIGINS if ALLOWED_ORIGINS[0] else "Open"
        }
    }), 200

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "not_found",
        "message": "Endpoint does not exist"
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "success": False,
        "error": "method_not_allowed",
        "message": f"Method {request.method} not allowed for this endpoint"
    }), 405

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({
        "success": False,
        "error": "internal_error",
        "message": "Internal server error occurred"
    }), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    
    logger.info("=" * 50)
    logger.info("🚀 API Gateway Router Starting...")
    logger.info(f"📡 Port: {port}")
    logger.info(f"🔒 API Key Required: {'Yes' if os.getenv('API_KEY') else 'No'}")
    logger.info(f"🌐 Allowed Origins: {ALLOWED_ORIGINS if ALLOWED_ORIGINS[0] else 'ALL'}")
    logger.info("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('DEBUG', 'False').lower() == 'true'
    )