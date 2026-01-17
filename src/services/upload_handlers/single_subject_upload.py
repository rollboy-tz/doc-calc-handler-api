# services/upload_handlers/single_subject_upload.py
"""
SINGLE SUBJECT UPLOAD HANDLER
Process uploaded Excel with marks for ONE subject only
Returns clean data for Node.js to save to database
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from ..calculations.grade_calculator import GradeCalculator

class SingleSubjectUploadHandler:
    """
    Handle upload of Excel file with ONE subject marks
    
    Expected Excel structure:
    - Columns A-E: Student info (read-only)
    - Column F: Subject marks
    - Column G: Remarks (optional)
    """
    
    def __init__(self, subject_name: str, max_score: int = 100, grading_system: str = 'KCSE'):
        self.subject_name = subject_name
        self.max_score = max_score
        self.grading_system = grading_system
        self.calculator = GradeCalculator(grading_system)
        
        # Expected columns in uploaded file
        self.expected_columns = [
            'admission_no', 'student_id', 'full_name', 
            'class', 'stream', subject_name, 'Remarks'
        ]
    
    def process_upload(self, excel_file_path: str) -> Dict:
        """
        Process uploaded single subject Excel file
        
        Args:
            excel_file_path: Path to uploaded Excel file
            
        Returns:
            Dictionary with processed data for Node.js
        """
        try:
            # 1. Read Excel file
            df = pd.read_excel(excel_file_path, header=1)
            
            # 2. Validate file structure
            validation = self._validate_structure(df)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Invalid file structure',
                    'details': validation['errors']
                }
            
            # 3. Extract and clean data
            cleaned_data = self._extract_data(df)
            
            # 4. Calculate grades and points
            processed_data = self._calculate_grades(cleaned_data)
            
            # 5. Generate summary statistics
            summary = self._generate_summary(processed_data)
            
            # 6. Return data for Node.js to save
            return {
                'success': True,
                'subject': self.subject_name,
                'max_score': self.max_score,
                'grading_system': self.grading_system,
                'students_processed': len(processed_data),
                'summary': summary,
                'student_data': processed_data,  # For Node.js to save to DB
                'validation_stats': {
                    'valid_rows': len(processed_data),
                    'invalid_rows': validation['invalid_count'],
                    'absent_students': summary['absent_count']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}',
                'subject': self.subject_name
            }
    
    def _validate_structure(self, df: pd.DataFrame) -> Dict:
        """Validate Excel file structure"""
        errors = []
        valid_count = 0
        invalid_count = 0
        
        # Check for required columns
        required_columns = ['admission_no', 'student_id', 'full_name', self.subject_name]
        
        for col in required_columns:
            if col not in df.columns:
                errors.append(f'Missing required column: {col}')
        
        if errors:
            return {'valid': False, 'errors': errors, 'invalid_count': len(df)}
        
        # Validate each row
        for idx, row in df.iterrows():
            row_num = idx + 2  # Excel row number (header is row 1)
            
            # Check student info
            if pd.isna(row['admission_no']) or pd.isna(row['student_id']) or pd.isna(row['full_name']):
                errors.append(f'Row {row_num}: Missing student information')
                invalid_count += 1
                continue
            
            # Check marks if present
            if pd.notna(row[self.subject_name]):
                try:
                    mark = float(row[self.subject_name])
                    if not (0 <= mark <= self.max_score):
                        errors.append(f'Row {row_num}: Marks {mark} out of range (0-{self.max_score})')
                        invalid_count += 1
                        continue
                except ValueError:
                    errors.append(f'Row {row_num}: Invalid marks format: {row[self.subject_name]}')
                    invalid_count += 1
                    continue
            
            valid_count += 1
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'valid_count': valid_count,
            'invalid_count': invalid_count
        }
    
    def _extract_data(self, df: pd.DataFrame) -> List[Dict]:
        """Extract and clean data from DataFrame"""
        data = []
        
        for _, row in df.iterrows():
            # Skip rows with missing student info
            if pd.isna(row['admission_no']) or pd.isna(row['student_id']):
                continue
            
            student_data = {
                'admission_no': str(row['admission_no']).strip(),
                'student_id': str(row['student_id']).strip(),
                'full_name': str(row['full_name']).strip() if pd.notna(row['full_name']) else '',
                'class': str(row['class']).strip() if 'class' in df.columns and pd.notna(row['class']) else '',
                'stream': str(row['stream']).strip() if 'stream' in df.columns and pd.notna(row['stream']) else '',
                'marks': None,
                'remarks': str(row['Remarks']).strip() if 'Remarks' in df.columns and pd.notna(row['Remarks']) else ''
            }
            
            # Extract marks if present
            if pd.notna(row[self.subject_name]):
                try:
                    student_data['marks'] = float(row[self.subject_name])
                except:
                    student_data['marks'] = None
            
            data.append(student_data)
        
        return data
    
    def _calculate_grades(self, student_data: List[Dict]) -> List[Dict]:
        """Calculate grades and points for each student"""
        for student in student_data:
            if student['marks'] is not None:
                grade, points = self.calculator.calculate_grade(student['marks'])
                student['grade'] = grade
                student['points'] = points
            else:
                student['grade'] = 'ABSENT'
                student['points'] = 0
        
        return student_data
    
    def _generate_summary(self, student_data: List[Dict]) -> Dict:
        """Generate summary statistics for the subject"""
        marks = [s['marks'] for s in student_data if s['marks'] is not None]
        grades = [s.get('grade', 'ABSENT') for s in student_data]
        
        summary = {
            'total_students': len(student_data),
            'students_with_marks': len(marks),
            'absent_count': grades.count('ABSENT'),
            'subject_average': np.mean(marks) if marks else 0,
            'subject_highest': max(marks) if marks else 0,
            'subject_lowest': min(marks) if marks else 0,
            'grade_distribution': pd.Series(grades).value_counts().to_dict()
        }
        
        return summary
    
    def get_expected_template(self) -> Dict:
        """Get expected template structure for this subject"""
        return {
            'subject': self.subject_name,
            'max_score': self.max_score,
            'required_columns': self.expected_columns,
            'instructions': f'Fill {self.subject_name} marks in column 6 only',
            'validation_rules': {
                'marks_range': f'0-{self.max_score}',
                'required_fields': ['admission_no', 'student_id', 'full_name'],
                'optional_fields': ['Remarks']
            }
        }