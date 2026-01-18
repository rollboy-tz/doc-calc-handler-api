# services/grading/grade_calculator.py
"""
GRADE CALCULATOR - CLEAN VARIABLES
"""

class GradeCalculator:
    
    def _process_student(self, student_data, subject_columns):
        # Student info - clean
        student_info = {
            "id": student_data.get("student_id", ""),
            "admission": student_data.get("admission_no", ""),
            "name": student_data.get("full_name", ""),
            "gender": student_data.get("gender", "Unknown").upper()
        }
        
        # Process subjects - clean variables
        subjects = {}
        total_marks = 0
        valid_subjects = 0
        
        for subject in subject_columns:
            marks = student_data.get(subject)
            
            if marks is None or marks == '':
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
                except:
                    subjects[subject] = {
                        "marks": None,
                        "grade": "ERR",
                        "remark": "Error",
                        "pass": False,
                        "attended": False
                    }
        
        # Student summary - clean
        summary = {
            "total": round(total_marks, 2) if valid_subjects > 0 else 0,
            "average": round(total_marks / valid_subjects, 2) if valid_subjects > 0 else 0,
            "subjects_total": len(subject_columns),
            "subjects_attended": sum(1 for s in subjects.values() if s.get("attended")),
            "subjects_passed": sum(1 for s in subjects.values() if s.get("pass")),
            "rank": 0,
            "grade": "N/A",
            "remark": "Not calculated",
            "status": "PENDING"
        }
        
        # Calculate overall grade
        if valid_subjects > 0:
            avg_marks = total_marks / valid_subjects
            avg_grade = get_grade_for_marks(self.system, avg_marks)
            
            summary.update({
                "grade": avg_grade["grade"],
                "remark": avg_grade["remark"]
            })
        
        # CSEE specific
        if self.system == "csee":
            total_points = sum(s.get("points", 0) for s in subjects.values() 
                             if s.get("attended") and s.get("points") is not None)
            summary["points"] = total_points
            summary["division"] = calculate_division(total_points, self.system)
            
            # Status
            if summary.get("division") == "0":
                summary["status"] = "FAIL"
                summary["grade"] = "F"
                summary["remark"] = "Fail"
            else:
                summary["status"] = "PASS"
        
        return {
            "student": student_info,
            "subjects": subjects,
            "summary": summary
        }