"""
Data validation for student reports
"""
from typing import Dict, Any, Tuple

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
    def validate_subjects(subjects: list) -> Tuple[bool, str]:
        """Validate subjects data"""
        if not subjects:
            return True, "No subjects provided"
        
        for i, subject in enumerate(subjects):
            if 'name' not in subject:
                return False, f"Subject {i+1} missing 'name'"
            if 'score' not in subject:
                return False, f"Subject {subject.get('name', f'{i+1}')} missing 'score'"
        
        return True, "Valid"