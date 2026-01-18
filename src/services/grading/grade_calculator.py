# services/grading/grade_calculator.py
# ADD ACSEE SPECIFIC LOGIC:

class GradeCalculator:
    
    def _process_student(self, student_data, subject_columns):
        # ... existing code ...
        
        # ACSEE specific - need to identify principal subjects
        if self.system == "acsee":
            # For ACSEE, we need to know which are principal subjects
            # Default: first 3 subjects are principals
            principal_subjects = subject_columns[:3] if len(subject_columns) >= 3 else subject_columns
            
            # Calculate points only for principal subjects
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
        
        # CSEE logic remains same
        elif self.system == "csee":
            total_points = sum(s.get("points", 0) for s in subjects.values() 
                             if s.get("attended") and s.get("points") is not None)
            summary["points"] = total_points
            
            division = calculate_division(total_points, "csee")
            summary["division"] = division
            
            if division == "0":
                summary["status"] = "FAIL"
                summary["grade"] = "F"
                summary["remark"] = "Fail"
            else:
                summary["status"] = "PASS"
        
        # PLSE logic
        else:
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