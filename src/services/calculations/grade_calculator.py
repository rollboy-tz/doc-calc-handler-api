# services/calculations/grade_calculator.py
"""
GRADE CALCULATOR
Calculate grades, points, totals, averages, positions
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime

class GradeCalculator:
    """
    Calculate grades based on different grading systems
    
    Supports:
    - KCSE grading system
    - KCPE grading system
    - Custom grading systems
    """
    
    # KCSE Grading System (Kenya)
    KCSE_GRADES = {
        'A': (80, 100, 12),
        'A-': (75, 79, 11),
        'B+': (70, 74, 10),
        'B': (65, 69, 9),
        'B-': (60, 64, 8),
        'C+': (55, 59, 7),
        'C': (50, 54, 6),
        'C-': (45, 49, 5),
        'D+': (40, 44, 4),
        'D': (35, 39, 3),
        'D-': (30, 34, 2),
        'E': (0, 29, 1)
    }
    
    # KCPE Grading System
    KCPE_GRADES = {
        'A': (80, 100, 5),
        'B': (60, 79, 4),
        'C': (40, 59, 3),
        'D': (20, 39, 2),
        'E': (0, 19, 1)
    }
    
    def __init__(self, grading_rules='CSEE'):
        """
        Initialize calculator
        
        Args:
            grading_system: 'KCSE' or 'KCPE' or custom dict
        """
        if grading_system == 'KCSE':
            self.grading_system = self.KCSE_GRADES
        elif grading_system == 'KCPE':
            self.grading_system = self.KCPE_GRADES
        elif isinstance(grading_system, dict):
            self.grading_system = grading_system
        else:
            raise ValueError(f"Unknown grading system: {grading_system}")
        
        self.system_name = grading_system if isinstance(grading_system, str) else 'CUSTOM'
    
    def calculate_grade(self, mark: float) -> Tuple[str, int]:
        """
        Calculate grade and points for a mark
        
        Args:
            mark: Numeric mark (0-100)
            
        Returns:
            (grade, points)
        """
        if not isinstance(mark, (int, float)) or pd.isna(mark):
            return ('-', 0)
        
        mark = float(mark)
        
        for grade, (min_score, max_score, points) in self.grading_system.items():
            if min_score <= mark <= max_score:
                return (grade, points)
        
        return ('E', 1)  # Default
    
    def process_marksheet(self, df: pd.DataFrame, subject_columns: List[str]) -> pd.DataFrame:
        """
        Process complete marksheet with all calculations
        
        Args:
            df: DataFrame with student marks
            subject_columns: List of subject column names
            
        Returns:
            DataFrame with all calculations
        """
        result_df = df.copy()
        
        # Calculate grades and points for each subject
        for subject in subject_columns:
            if subject in result_df.columns:
                # Create grade and points columns
                grade_col = f"{subject}_grade"
                points_col = f"{subject}_points"
                
                result_df[[grade_col, points_col]] = result_df[subject].apply(
                    lambda x: pd.Series(self.calculate_grade(x))
                )
        
        # Calculate totals
        points_columns = [f"{subject}_points" for subject in subject_columns if f"{subject}_points" in result_df.columns]
        mark_columns = [subject for subject in subject_columns if subject in result_df.columns]
        
        if points_columns:
            result_df['total_points'] = result_df[points_columns].sum(axis=1, skipna=True)
        
        if mark_columns:
            result_df['total_marks'] = result_df[mark_columns].sum(axis=1, skipna=True)
            
            # Calculate average
            valid_counts = result_df[mark_columns].notna().sum(axis=1)
            result_df['average_mark'] = result_df['total_marks'] / valid_counts.replace(0, np.nan)
            
            # Calculate average grade
            result_df['average_grade'] = result_df['average_mark'].apply(
                lambda x: self.calculate_grade(x)[0] if pd.notna(x) else '-'
            )
        
        # Calculate class position
        if 'total_marks' in result_df.columns:
            result_df['position'] = result_df['total_marks'].rank(
                method='min', 
                ascending=False
            ).astype('Int64')
        
        # Add remarks
        result_df['remarks'] = result_df['average_grade'].apply(self._get_remarks)
        
        return result_df
    
    def _get_remarks(self, grade: str) -> str:
        """Get remarks based on grade"""
        remarks_map = {
            'A': 'Excellent performance',
            'A-': 'Very good performance',
            'B+': 'Good performance',
            'B': 'Above average',
            'B-': 'Average performance',
            'C+': 'Fair performance',
            'C': 'Below average',
            'C-': 'Poor performance',
            'D+': 'Very poor performance',
            'D': 'Weak performance',
            'D-': 'Very weak performance',
            'E': 'Failed',
            '-': 'No marks entered'
        }
        return remarks_map.get(grade, 'Performance not rated')
    
    def get_grade_distribution(self, df: pd.DataFrame, grade_column: str = 'average_grade') -> Dict:
        """Get distribution of grades"""
        if grade_column not in df.columns:
            return {}
        
        distribution = df[grade_column].value_counts().to_dict()
        return dict(sorted(distribution.items()))
    
    def get_class_summary(self, df: pd.DataFrame) -> Dict:
        """Get class summary statistics"""
        summary = {
            'total_students': len(df),
            'grading_system': self.system_name
        }
        
        if 'total_marks' in df.columns:
            summary.update({
                'class_average': df['total_marks'].mean(),
                'highest_score': df['total_marks'].max(),
                'lowest_score': df['total_marks'].min(),
                'top_student': df.loc[df['total_marks'].idxmax(), 'full_name'] if 'full_name' in df.columns else 'Unknown'
            })
        
        if 'average_grade' in df.columns:
            summary['grade_distribution'] = self.get_grade_distribution(df, 'average_grade')
        
        return summary