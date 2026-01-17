# services/calculations/grade_calculator.py
"""
TANZANIA NECTA GRADE CALCULATOR
For CSEE and PSLE examinations
"""
from typing import Dict, List

class GradeCalculator:
    """Calculate grades according to Tanzania NECTA system"""
    
    def __init__(self, grading_rules='CSEE'):
        """
        Initialize with grading rules
        
        Args:
            grading_rules: 'CSEE' or 'PSLE' - Tanzania NECTA systems
        """
        self.grading_rules = grading_rules
        self._validate_grading_rules()
    
    def _validate_grading_rules(self):
        """Validate grading rules"""
        valid_rules = ['CSEE', 'PSLE']
        if self.grading_rules not in valid_rules:
            raise ValueError(f"Invalid grading rules: {self.grading_rules}. Use 'CSEE' or 'PSLE'")
    
    def calculate_grade(self, marks: float) -> dict:
        """
        Calculate grade based on Tanzania NECTA system
        
        Args:
            marks: Student's marks (0-100)
            
        Returns:
            Dictionary with grade details
        """
        if marks is None or marks < 0 or marks > 100:
            return {
                'grade': 'INVALID',
                'remarks': 'Invalid marks',
                'points': 0
            }
        
        # TANZANIA NECTA GRADING (same for CSEE and PSLE)
        if marks >= 81:
            return {'grade': 'A', 'remarks': 'Excellent', 'points': 1}
        elif marks >= 61:
            return {'grade': 'B', 'remarks': 'Very Good', 'points': 2}
        elif marks >= 41:
            return {'grade': 'C', 'remarks': 'Good', 'points': 3}
        elif marks >= 21:
            return {'grade': 'D', 'remarks': 'Satisfactory', 'points': 4}
        else:
            return {'grade': 'E', 'remarks': 'Fail', 'points': 5}
    
    def get_grading_system_info(self) -> Dict:
        """Get information about Tanzania grading system"""
        return {
            'country': 'Tanzania',
            'exam_board': 'NECTA',
            'grading_rules': self.grading_rules,
            'grading_scale': {
                'A': {'range': '81-100', 'remarks': 'Excellent', 'points': 1},
                'B': {'range': '61-80', 'remarks': 'Very Good', 'points': 2},
                'C': {'range': '41-60', 'remarks': 'Good', 'points': 3},
                'D': {'range': '21-40', 'remarks': 'Satisfactory', 'points': 4},
                'E': {'range': '0-20', 'remarks': 'Fail', 'points': 5}
            }
        }