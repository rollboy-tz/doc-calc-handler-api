"""
Data validation for student reports
"""
from typing import Dict, Any, Tuple, List

class StudentReportValidator:
    """Validate student report data"""
    
    REQUIRED_STUDENT_FIELDS = ['name', 'admission']
    REQUIRED_SUMMARY_FIELDS = ['total', 'average', 'grade']
    
    @staticmethod
    def validate_student_data(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate student data structure"""
        if 'student' not in data:
            return False, "Missing 'student' section"
        
        student = data['student']
        missing = [f for f in StudentReportValidator.REQUIRED_STUDENT_FIELDS 
                  if f not in student]
        
        if missing:
            return False, f"Missing student fields: {', '.join(missing)}"
        
        if 'summary' not in data:
            return False, "Missing 'summary' section"
        
        summary = data['summary']
        missing = [f for f in StudentReportValidator.REQUIRED_SUMMARY_FIELDS 
                  if f not in summary]
        
        if missing:
            return False, f"Missing summary fields: {', '.join(missing)}"
        
        return True, "Valid"
    
    @staticmethod
    def validate_subjects(subjects: List[Dict]) -> Tuple[bool, str]:
        """Validate subjects data"""
        if not subjects:
            return True, "No subjects provided"
        
        for i, subject in enumerate(subjects):
            if 'name' not in subject:
                return False, f"Subject {i+1} missing 'name'"
            if 'score' not in subject and 'marks' not in subject:
                return False, f"Subject '{subject.get('name', f'{i+1}')}' missing 'score' or 'marks'"
        
        return True, "Valid"
    
    @staticmethod
    def validate_grades(grades: List[str]) -> Tuple[bool, str]:
        """Validate grade values"""
        valid_grades = ['A', 'B', 'C', 'D', 'E', 'F', 'I', 'II', 'III', 'IV', 'PASS', 'FAIL', 'ABS']
        
        for grade in grades:
            if grade and grade.upper() not in valid_grades:
                return False, f"Invalid grade: '{grade}'. Valid grades: {', '.join(valid_grades)}"
        
        return True, "Valid"
    
    @staticmethod
    def validate_scores(scores: List[float]) -> Tuple[bool, str]:
        """Validate score values"""
        for score in scores:
            if not isinstance(score, (int, float)):
                return False, f"Invalid score type: {type(score)}"
            if score < 0 or score > 100:
                return False, f"Score {score} out of range (0-100)"
        
        return True, "Valid"