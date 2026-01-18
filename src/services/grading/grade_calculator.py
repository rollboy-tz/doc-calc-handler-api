# services/grading/grade_calculator.py
"""
GRADE CALCULATOR - FIXED CONSTRUCTOR
"""
import datetime
from .grading_rules import get_grade_for_marks, calculate_division, GRADING_SYSTEMS
from .analytics import ResultAnalytics


class GradeCalculator:
    """Calculate grades with clean variables"""
    
    def __init__(self, system="csee"):
        """Initialize calculator with grading system"""
        self.system = system.lower()
        if self.system not in GRADING_SYSTEMS:
            self.system = "csee"
    
    def process_class_results(self, extracted_data, external_ids=None):
        """Process all student results"""
        external_ids = external_ids or {}
        
        # Get data
        students_raw = extracted_data.get("data", [])
        subject_columns = extracted_data.get("metadata", {}).get("subject_columns", [])
        
        if not students_raw or not subject_columns:
            return {
                "success": False,
                "error": "No student data or subjects provided",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Process each student
        students_processed = []
        for student_data in students_raw:
            student_result = self._process_student(student_data, subject_columns)
            students_processed.append(student_result)
        
        # Calculate ranks
        students_ranked = ResultAnalytics.calculate_ranks(students_processed)
        students_final = ResultAnalytics.calculate_subject_ranks(students_ranked, subject_columns)
        
        # Calculate analytics
        subject_analysis = ResultAnalytics.calculate_subject_analysis(
            students_final, subject_columns, external_ids
        )
        class_analysis = ResultAnalytics.calculate_class_analysis(
            students_final, subject_columns, external_ids
        )
        
        # Build metadata
        metadata = self._build_metadata(external_ids, students_final, subject_columns)
        
        return {
            "success": True,
            "metadata": metadata,
            "students": students_final,
            "analytics": {
                "subjects": subject_analysis,
                "class": class_analysis
            }
        }
    
    def _process_student(self, student_data, subject_columns):
        """Process single student results"""
        # Student info
        student_info = {
            "id": student_data.get("student_id", ""),
            "admission": student_data.get("admission_no", ""),
            "name": student_data.get("full_name", ""),
            "gender": student_data.get("gender", "Unknown").upper()
        }
        
        # Process subjects
        subjects = {}
        total_marks = 0
        valid_subjects = 0
        
        for subject in subject_columns:
            marks = student_data.get(subject)
            
            if marks is None or marks == '' or str(marks).strip() == '':
                # Absent
                subjects[subject] = {
                    "marks": None,
                    "grade": "ABS",
                    "points": None,
                    "remark": "Absent",
                    "pass": False,
                    "attended": False
                }
            else:
                try:
                    marks = float(marks)
                    if 0 <= marks <= 100:
                        grade_info = get_grade_for_marks(self.system, marks)
                        
                        subjects[subject] = {
                            "marks": round(marks, 2),
                            "grade": grade_info["grade"],
                            "points": grade_info.get("points"),
                            "remark": grade_info["remark"],
                            "pass": grade_info["grade"] not in ["F", "E", "ABS"],
                            "attended": True
                        }
                        
                        total_marks += marks
                        valid_subjects += 1
                    else:
                        # Invalid marks
                        subjects[subject] = {
                            "marks": marks,
                            "grade": "INV",
                            "points": None,
                            "remark": "Invalid Marks",
                            "pass": False,
                            "attended": True
                        }
                except (ValueError, TypeError):
                    # Couldn't convert to float
                    subjects[subject] = {
                        "marks": None,
                        "grade": "ERR",
                        "points": None,
                        "remark": "Error",
                        "pass": False,
                        "attended": False
                    }
        
        # Student summary
        summary = {
            "total": 0,
            "average": 0,
            "subjects_total": len(subject_columns),
            "subjects_attended": sum(1 for s in subjects.values() if s.get("attended")),
            "subjects_passed": sum(1 for s in subjects.values() if s.get("pass")),
            "points": 0,
            "rank": 0,
            "grade": "N/A",
            "remark": "Not calculated",
            "division": None,
            "status": "PENDING"
        }
        
        if valid_subjects > 0:
            avg_marks = total_marks / valid_subjects
            avg_grade = get_grade_for_marks(self.system, avg_marks)
            
            # Calculate total points for CSEE
            total_points = 0
            if self.system == "csee":
                total_points = sum(s.get("points", 0) for s in subjects.values() 
                                 if s.get("attended") and s.get("points") is not None)
            
            summary.update({
                "total": round(total_marks, 2),
                "average": round(avg_marks, 2),
                "points": total_points,
                "grade": avg_grade["grade"],
                "remark": avg_grade["remark"]
            })
            
            # CSEE division
            if self.system == "csee":
                division = calculate_division(total_points, self.system)
                summary["division"] = division
                
                if division == "0":
                    summary["status"] = "FAIL"
                    summary["grade"] = "F"
                    summary["remark"] = "Fail"
                else:
                    summary["status"] = "PASS"
            else:
                # Non-CSEE systems
                fail_count = sum(1 for s in subjects.values() if not s.get("pass"))
                if fail_count > len(subject_columns) * 0.4:
                    summary["status"] = "FAIL"
                else:
                    summary["status"] = "PASS"
        
        return {
            "student": student_info,
            "subjects": subjects,
            "summary": summary
        }
    
    def _build_metadata(self, external_ids, students_data, subject_columns):
        """Build metadata for response"""
        system_info = GRADING_SYSTEMS.get(self.system, GRADING_SYSTEMS["csee"])
        
        metadata = {
            "exam_id": external_ids.get("exam_id", ""),
            "class_id": external_ids.get("class_id", ""),
            "stream_id": external_ids.get("stream_id", ""),
            "rule": self.system,
            "system_name": system_info["name"],
            "students": len(students_data),
            "subjects": len(subject_columns),
            "subject_list": subject_columns,
            "processed": datetime.datetime.now().isoformat()
        }
        
        # Add subject IDs if available
        if external_ids.get("subject_ids"):
            metadata["subject_ids"] = external_ids["subject_ids"]
        
        return metadata