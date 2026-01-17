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
from services.documents.subject_marksheet import SubjectMarkSheet
from services.upload_handlers.single_subject_upload import SingleSubjectUploadHandler
from services.upload_handlers.multi_subject_upload import MultiSubjectUploadHandler

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


@app.route('/api/template/subject', methods=['POST'])
def generate_subject_marksheet():
    """Generate mark sheet for ONE subject only"""
    try:
        data = request.json
        
        # Extract data
        students = data.get('students', [])
        subject_info = data.get('subject_info', {})
        
        if not students:
            return jsonify({
                "error": "No students provided",
                "message": "Please provide student list"
            }), 400
        
        if not subject_info.get('name'):
            return jsonify({
                "error": "Subject name required",
                "message": "Please provide subject name"
            }), 400
        
        # Create subject mark sheet
        template = SubjectMarkSheet(
            student_list=students,
            subject_info=subject_info
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

# ======== EXCEL UPLOAD TEST ROUTE ================
@app.route('/api/debug/xlxs/upload-test', methods=['POST'])
def debug_upload_test():
    """Debug endpoint to see exactly what's in the file"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file"}), 400
        
        file = request.files['file']
        
        # Save temp file
        import tempfile
        import os
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        file.save(temp_path.name)
        
        # Read with pandas
        import pandas as pd
        import numpy as np
        
        # Read Excel
        df = pd.read_excel(temp_path.name, engine='openpyxl')
        
        # CONVERT numpy types to Python native types
        def convert_to_serializable(obj):
            """Convert numpy/pandas types to JSON-serializable types"""
            if pd.isna(obj):
                return None
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, (pd.Timestamp, pd.DatetimeIndex)):
                return obj.isoformat()
            else:
                return str(obj)
        
        # Get serializable data
        info = {
            "filename": file.filename,
            "file_size_bytes": os.path.getsize(temp_path.name),
            "columns_found": df.columns.tolist(),
            "columns_count": len(df.columns),
            "rows_count": len(df),
            "data_types": {col: str(df[col].dtype) for col in df.columns},
            "first_3_rows": [],
            "column_details": []
        }
        
        # Convert first rows
        for i in range(min(3, len(df))):
            row_data = {}
            for col in df.columns:
                value = df.iloc[i][col]
                row_data[col] = convert_to_serializable(value)
            info["first_3_rows"].append(row_data)
        
        # Column details
        for col in df.columns:
            # Get sample values (convert to serializable)
            sample_vals = []
            for val in df[col].dropna().head(3):
                sample_vals.append(convert_to_serializable(val))
            
            col_info = {
                "name": col,
                "type": str(df[col].dtype),
                "non_null_count": int(df[col].notna().sum()),  # Convert to int
                "null_count": int(df[col].isna().sum()),      # Convert to int
                "sample_values": sample_vals
            }
            info["column_details"].append(col_info)
        
        # Clean up
        os.unlink(temp_path.name)
        
        return jsonify({
            "success": True,
            "debug_info": info,
            "expected_columns": [
                "admission_no",
                "student_id", 
                "full_name",
                "class",
                "stream",
                "MATHEMATICS",
                "Remarks"
            ]
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
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


@app.route('/api/process/subject/marks', methods=['POST'])
def process_subject_marks():
    """
    Process uploaded marks for ONE subject
    
    Can be used by subject teachers to submit marks
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                "error": "No file uploaded",
                "message": "Please upload Excel file"
            }), 400
        
        file = request.files['file']
        
        # Read Excel file
        df = pd.read_excel(file)
        
        # Get subject info from form
        subject_name = request.form.get('subject_name', 'Mathematics')
        subject_code = request.form.get('subject_code', 'MATH')
        max_score = int(request.form.get('max_score', 100))
        teacher_id = request.form.get('teacher_id', '')
        
        # Validate file structure
        required_columns = ['admission_no', 'student_id', 'full_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return jsonify({
                "error": "Invalid file structure",
                "message": f"Missing columns: {', '.join(missing_columns)}"
            }), 400
        
        # Extract marks column (should be the subject column)
        subject_columns = [col for col in df.columns if col not in required_columns + ['class', 'stream', 'Remarks']]
        
        if not subject_columns:
            return jsonify({
                "error": "No subject marks found",
                "message": "File should contain subject marks column"
            }), 400
        
        subject_column = subject_columns[0]  # First non-student-info column
        
        # Initialize grade calculator
        from services.calculations.grade_calculator import GradeCalculator
        calculator = GradeCalculator()
        
        # Process marks for this subject
        results = []
        subject_marks = []
        
        for _, row in df.iterrows():
            mark = row.get(subject_column)
            
            if pd.isna(mark):
                grade = '-'
                points = 0
            else:
                try:
                    mark_value = float(mark)
                    if 0 <= mark_value <= max_score:
                        grade, points = calculator.calculate_grade(mark_value)
                    else:
                        grade = 'INVALID'
                        points = 0
                except:
                    grade = 'INVALID'
                    points = 0
            
            results.append({
                'admission_no': row.get('admission_no'),
                'student_id': row.get('student_id'),
                'full_name': row.get('full_name'),
                'class': row.get('class', ''),
                'stream': row.get('stream', ''),
                'subject': subject_name,
                'mark': mark if not pd.isna(mark) else None,
                'grade': grade,
                'points': points,
                'remarks': row.get('Remarks', '')
            })
            
            if pd.notna(mark):
                try:
                    subject_marks.append(float(mark))
                except:
                    pass
        
        # Calculate subject statistics
        if subject_marks:
            subject_stats = {
                'subject_average': sum(subject_marks) / len(subject_marks),
                'subject_highest': max(subject_marks),
                'subject_lowest': min(subject_marks),
                'students_with_marks': len(subject_marks),
                'students_missing': len(df) - len(subject_marks)
            }
        else:
            subject_stats = {
                'subject_average': 0,
                'subject_highest': 0,
                'subject_lowest': 0,
                'students_with_marks': 0,
                'students_missing': len(df)
            }
        
        return jsonify({
            "success": True,
            "subject": subject_name,
            "teacher_id": teacher_id,
            "students_processed": len(results),
            "subject_statistics": subject_stats,
            "marks_data": results,
            "summary": {
                "file_received": file.filename,
                "subject_column": subject_column,
                "max_score": max_score,
                "processed_at": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
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
            {"path": "/api/template/subject", "method": "POST", "desc": "Generate mark sheet for ONE subject only"},
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