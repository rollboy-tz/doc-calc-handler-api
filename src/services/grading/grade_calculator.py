# services/grading/grade_calculator.py
"""
MAIN GRADE CALCULATOR
"""
import datetime
from .grading_rules import get_grade_for_marks, calculate_division, GRADING_SYSTEMS
from .analytics import ResultAnalytics


class GradeCalculator:
    """Calculate grades and generate results"""
    
    def __init__(self, system="csee"):
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
                "subject_level": subject_analysis,
                "class_level": class_analysis
            }
        }
    
    def _process_student(self, student_data, subject_columns):
        """Process single student results"""
        # Student info
        student_info = {
            "student_id": student_data.get("student_id", ""),
            "admission_no": student_data.get("admission_no", ""),
            "full_name": student_data.get("full_name", ""),
            "gender": student_data.get("gender", "Unknown").upper()
        }
        
        # Process subjects
        subjects = {}
        total_marks = 0
        valid_subjects = 0
        total_points = 0
        
        for subject in subject_columns:
            marks = student_data.get(subject)
            
            if marks is None or marks == '' or str(marks).strip() == '':
                # Absent
                subjects[subject] = {
                    "marks": None,
                    "grade": "ABS",
                    "points": None,
                    "is_pass": False,
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
                            "description": grade_info["description"],
                            "is_pass": grade_info["grade"] not in ["F", "E", "ABS"],
                            "attended": True
                        }
                        
                        total_marks += marks
                        if grade_info.get("points"):
                            total_points += grade_info["points"]
                        valid_subjects += 1
                    else:
                        # Invalid marks
                        subjects[subject] = {
                            "marks": marks,
                            "grade": "INV",
                            "points": None,
                            "is_pass": False,
                            "attended": True
                        }
                except (ValueError, TypeError):
                    subjects[subject] = {
                        "marks": None,
                        "grade": "ERR",
                        "points": None,
                        "is_pass": False,
                        "attended": False
                    }
        
        # Student summary
        summary = {
            "total_marks": 0,
            "average_marks": 0,
            "subjects_count": len(subject_columns),
            "passing_subjects": sum(1 for s in subjects.values() if s.get('is_pass')),
            "total_points": 0,
            "class_rank": 0,
            "overall_grade": "N/A",
            "overall_description": "Not calculated"
        }
        
        if valid_subjects > 0:
            avg_marks = total_marks / valid_subjects
            avg_grade = get_grade_for_marks(self.system, avg_marks)
            
            summary.update({
                "total_marks": round(total_marks, 2),
                "average_marks": round(avg_marks, 2),
                "total_points": round(total_points, 2),
                "overall_grade": avg_grade["grade"],
                "overall_description": avg_grade["description"]
            })
            
            # Division for CSEE
            if self.system == "csee":
                summary["division"] = calculate_division(total_points)
        
        return {
            "student_info": student_info,
            "subjects": subjects,
            "summary": summary
        }
    
    def _build_metadata(self, external_ids, students_data, subject_columns):
        """Build metadata for response"""
        metadata = {
            "class_id": external_ids.get("class_id", ""),
            "exam_id": external_ids.get("exam_id", ""),
            "stream_id": external_ids.get("stream_id", ""),
            "grading_rule": self.system,
            "students_count": len(students_data),
            "subjects_count": len(subject_columns),
            "subjects": subject_columns,
            "processing_time": datetime.datetime.now().isoformat(),
            "grading_system_name": GRADING_SYSTEMS[self.system]["name"]
        }
        
        # Add subject IDs if available
        if external_ids.get("subject_ids"):
            metadata["subject_ids"] = external_ids["subject_ids"]
        
        return metadata