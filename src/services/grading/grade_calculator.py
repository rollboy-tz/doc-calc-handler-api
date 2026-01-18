# services/grading/grade_calculator.py
"""
GRADE CALCULATOR - COMPLETE VERSION
"""
import datetime
from .grading_rules import get_grade_for_marks, calculate_division, GRADING_SYSTEMS


class GradeCalculator:
    """Calculate grades for CSEE, ACSEE, and PLSE"""
    
    def __init__(self, system="csee"):
        """Initialize with grading system"""
        self.system = system.lower()
        if self.system not in GRADING_SYSTEMS:
            self.system = "csee"
    
    def process_class_results(self, extracted_data, external_ids=None):
        """Process all student results"""
        external_ids = external_ids or {}
        
        # Get data
        students_raw = extracted_data.get("data", [])
        subject_columns = extracted_data.get("metadata", {}).get("subject_columns", [])
        
        if not students_raw:
            return {
                "success": False,
                "error": "No student data",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Process each student
        students_processed = []
        for student_data in students_raw:
            student_result = self._process_student(student_data, subject_columns)
            students_processed.append(student_result)
        
        # Calculate ranks
        from .analytics import ResultAnalytics
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
        """Process single student"""
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
            
            if marks in [None, '', ' ']:
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
                    marks = int(float(marks))
                    system_info = GRADING_SYSTEMS[self.system]
                    max_scale = system_info["scale"]
                    
                    if marks < 0 or marks > max_scale * 2:
                        subjects[subject] = {
                            "marks": marks,
                            "grade": "INV",
                            "points": None,
                            "remark": f"Invalid",
                            "pass": False,
                            "attended": True
                        }
                    else:
                        # Handle PLSE percentages
                        if self.system == "plse" and marks > 50:
                            marks = int((marks / 100) * 50)
                        
                        grade_info = get_grade_for_marks(self.system, marks)
                        
                        subjects[subject] = {
                            "marks": marks,
                            "grade": grade_info["grade"],
                            "points": grade_info.get("points"),
                            "remark": grade_info["remark"],
                            "pass": grade_info["grade"] not in ["F", "E", "ABS"],
                            "attended": True
                        }
                        
                        total_marks += marks
                        valid_subjects += 1
                        
                except:
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
            average = int(total_marks / valid_subjects)
            grade_info = get_grade_for_marks(self.system, average)
            
            summary.update({
                "total": total_marks,
                "average": average,
                "grade": grade_info["grade"],
                "remark": grade_info["remark"]
            })
            
            # CSEE points and division
            if self.system == "csee":
                total_points = 0
                for subj in subjects.values():
                    if subj.get("attended") and subj.get("points") is not None:
                        total_points += subj["points"]
                
                summary["points"] = total_points
                division = calculate_division(total_points, "csee")
                summary["division"] = division
                
                if division == "0":
                    summary["status"] = "FAIL"
                    summary["grade"] = "F"
                    summary["remark"] = "Fail"
                else:
                    summary["status"] = "PASS"
            
            # ACSEE points and division
            elif self.system == "acsee":
                # For ACSEE, use first 3 subjects as principals
                principal_subjects = subject_columns[:3] if len(subject_columns) >= 3 else subject_columns
                total_points = 0
                principal_count = 0
                
                for subject in principal_subjects:
                    if subject in subjects:
                        subj_data = subjects[subject]
                        if subj_data.get("attended") and subj_data.get("points") is not None:
                            total_points += subj_data["points"]
                            principal_count += 1
                
                summary["points"] = total_points
                summary["principals"] = principal_count
                
                # ACSEE requires at least 2 principal passes
                principal_passes = sum(1 for s in principal_subjects 
                                     if s in subjects and subjects[s].get("pass"))
                
                if principal_count >= 2 and principal_passes >= 2:
                    division = calculate_division(total_points, "acsee")
                    summary["division"] = division
                    
                    if division == "0":
                        summary["status"] = "FAIL"
                    else:
                        summary["status"] = "PASS"
                else:
                    summary["status"] = "FAIL"
                    summary["division"] = "0"
            
            # PLSE - simple pass/fail
            elif self.system == "plse":
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
        """Build metadata"""
        system_info = GRADING_SYSTEMS.get(self.system, GRADING_SYSTEMS["csee"])
        
        metadata = {
            "exam_id": external_ids.get("exam_id", ""),
            "class_id": external_ids.get("class_id", ""),
            "stream_id": external_ids.get("stream_id", ""),
            "rule": self.system,
            "system": system_info["name"],
            "scale": system_info["scale"],
            "students": len(students_data),
            "subjects": len(subject_columns),
            "subject_list": subject_columns,
            "processed": datetime.datetime.now().isoformat()
        }
        
        if external_ids.get("subject_ids"):
            metadata["subject_ids"] = external_ids["subject_ids"]
        
        return metadata