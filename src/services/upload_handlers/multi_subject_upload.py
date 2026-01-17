# services/upload_handlers/multi_subject_upload.py
"""
MULTI SUBJECT UPLOAD HANDLER  
Process uploaded Excel with marks for MULTIPLE subjects
Returns clean data for Node.js to save to database
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Set
from ..calculations.grade_calculator import GradeCalculator

class MultiSubjectUploadHandler:
    """
    Handle upload of Excel file with MULTIPLE subjects marks
    
    Expected Excel structure:
    - Columns A-E: Student info (read-only)
    - Columns F onward: Subject marks (one column per subject)
    """
    
    def __init__(self, subjects: List[str], grading_system: str = 'KCSE'):
        self.subjects = subjects
        self.grading_system = grading_system
        self.calculator = GradeCalculator(grading_system)
        
        # Base columns that should always be present
        self.base_columns = ['admission_no', 'student_id', 'full_name', 'class', 'stream']
    
    def process_upload(self, excel_file_path: str) -> Dict:
        """
        Process uploaded multi-subject Excel file
        
        Args:
            excel_file_path: Path to uploaded Excel file
            
        Returns:
            Dictionary with processed data for Node.js
        """
        try:
            # 1. Read Excel file
            df = pd.read_excel(excel_file_path)
            
            # 2. Detect subjects from file
            detected_subjects = self._detect_subjects(df)
            
            # 3. Validate file structure
            validation = self._validate_structure(df, detected_subjects)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Invalid file structure',
                    'details': validation['errors'],
                    'detected_subjects': detected_subjects
                }
            
            # 4. Extract and clean data for each student
            student_records = self._extract_student_records(df, detected_subjects)
            
            # 5. Calculate grades for each subject
            processed_records = self._calculate_all_grades(student_records, detected_subjects)
            
            # 6. Calculate student summaries (totals, averages, positions)
            final_results = self._calculate_summaries(processed_records, detected_subjects)
            
            # 7. Generate class-wide statistics
            class_summary = self._generate_class_summary(final_results, detected_subjects)
            
            # 8. Return comprehensive data for Node.js
            return {
                'success': True,
                'subjects_processed': detected_subjects,
                'total_students': len(final_results),
                'grading_system': self.grading_system,
                'class_summary': class_summary,
                'student_records': final_results,  # Complete data for Node.js to save
                'processing_stats': {
                    'valid_students': len([s for s in final_results if s['valid']]),
                    'invalid_students': len([s for s in final_results if not s['valid']]),
                    'subjects_found': len(detected_subjects),
                    'subjects_missing': list(set(self.subjects) - set(detected_subjects)) if self.subjects else []
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}',
                'subjects_expected': self.subjects
            }
    
    def _detect_subjects(self, df: pd.DataFrame) -> List[str]:
        """Detect subject columns in the uploaded file"""
        all_columns = df.columns.tolist()
        
        # Subject columns are those not in base columns
        subject_columns = [col for col in all_columns if col not in self.base_columns]
        
        # If subjects were specified, filter to only those
        if self.subjects:
            subject_columns = [col for col in subject_columns if col in self.subjects]
        
        return subject_columns
    
    def _validate_structure(self, df: pd.DataFrame, subjects: List[str]) -> Dict:
        """Validate Excel file structure"""
        errors = []
        
        # Check base columns
        for col in self.base_columns[:3]:  # First 3 are required
            if col not in df.columns:
                errors.append(f'Missing required column: {col}')
        
        # Check if we have any subject columns
        if not subjects:
            errors.append('No subject columns found in file')
        
        # Validate each row
        for idx, row in df.iterrows():
            row_num = idx + 2
            
            # Check student info
            if pd.isna(row.get('admission_no')) or pd.isna(row.get('student_id')):
                errors.append(f'Row {row_num}: Missing admission_no or student_id')
                continue
            
            # Validate marks for each subject
            for subject in subjects:
                if subject in df.columns and pd.notna(row[subject]):
                    try:
                        mark = float(row[subject])
                        if not (0 <= mark <= 100):  # Assuming 100 max
                            errors.append(f'Row {row_num}: {subject} marks {mark} out of range')
                    except ValueError:
                        errors.append(f'Row {row_num}: {subject} invalid marks format')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors[:10],  # Limit to first 10 errors
            'total_errors': len(errors)
        }
    
    def _extract_student_records(self, df: pd.DataFrame, subjects: List[str]) -> List[Dict]:
        """Extract student records from DataFrame"""
        records = []
        
        for _, row in df.iterrows():
            # Skip rows with missing essential info
            if pd.isna(row.get('admission_no')) or pd.isna(row.get('student_id')):
                continue
            
            record = {
                'admission_no': str(row['admission_no']).strip(),
                'student_id': str(row['student_id']).strip(),
                'full_name': str(row.get('full_name', '')).strip(),
                'class': str(row.get('class', '')).strip(),
                'stream': str(row.get('stream', '')).strip(),
                'subjects': {},
                'valid': True,
                'errors': []
            }
            
            # Extract marks for each subject
            for subject in subjects:
                if subject in df.columns:
                    if pd.notna(row[subject]):
                        try:
                            record['subjects'][subject] = {
                                'mark': float(row[subject]),
                                'grade': None,  # Will be calculated
                                'points': None   # Will be calculated
                            }
                        except:
                            record['subjects'][subject] = {'mark': None, 'error': 'Invalid format'}
                    else:
                        record['subjects'][subject] = {'mark': None, 'status': 'ABSENT'}
            
            records.append(record)
        
        return records
    
    def _calculate_all_grades(self, records: List[Dict], subjects: List[str]) -> List[Dict]:
        """Calculate grades for all subjects"""
        for record in records:
            for subject, data in record['subjects'].items():
                if data.get('mark') is not None:
                    grade, points = self.calculator.calculate_grade(data['mark'])
                    record['subjects'][subject]['grade'] = grade
                    record['subjects'][subject]['points'] = points
        
        return records
    
    def _calculate_summaries(self, records: List[Dict], subjects: List[str]) -> List[Dict]:
        """Calculate student summaries (totals, averages, etc.)"""
        for record in records:
            # Get all valid marks
            marks = []
            points = []
            grades = []
            
            for subject, data in record['subjects'].items():
                if data.get('mark') is not None:
                    marks.append(data['mark'])
                    points.append(data.get('points', 0))
                    grades.append(data.get('grade', ''))
            
            if marks:
                record['summary'] = {
                    'total_marks': sum(marks),
                    'average_mark': sum(marks) / len(marks),
                    'total_points': sum(points),
                    'mean_points': sum(points) / len(points) if points else 0,
                    'subjects_with_marks': len(marks),
                    'subjects_count': len(subjects),
                    'grades': grades
                }
            else:
                record['summary'] = {
                    'total_marks': 0,
                    'average_mark': 0,
                    'total_points': 0,
                    'mean_points': 0,
                    'subjects_with_marks': 0,
                    'subjects_count': len(subjects),
                    'grades': []
                }
        
        # Calculate class positions based on total marks
        valid_records = [r for r in records if r['summary']['total_marks'] > 0]
        valid_records.sort(key=lambda x: x['summary']['total_marks'], reverse=True)
        
        # Assign positions
        for position, record in enumerate(valid_records, start=1):
            record['summary']['class_position'] = position
        
        # For records with no marks
        for record in records:
            if 'class_position' not in record['summary']:
                record['summary']['class_position'] = None
        
        return records
    
    def _generate_class_summary(self, records: List[Dict], subjects: List[str]) -> Dict:
        """Generate class-wide statistics"""
        # Subject-wise statistics
        subject_stats = {}
        for subject in subjects:
            marks = []
            for record in records:
                if subject in record['subjects'] and record['subjects'][subject].get('mark') is not None:
                    marks.append(record['subjects'][subject]['mark'])
            
            if marks:
                subject_stats[subject] = {
                    'average': np.mean(marks),
                    'highest': max(marks),
                    'lowest': min(marks),
                    'students_with_marks': len(marks),
                    'students_absent': len(records) - len(marks)
                }
        
        # Overall class statistics
        total_marks = [r['summary']['total_marks'] for r in records if r['summary']['total_marks'] > 0]
        
        return {
            'subject_statistics': subject_stats,
            'class_average': np.mean(total_marks) if total_marks else 0,
            'class_highest_total': max(total_marks) if total_marks else 0,
            'class_lowest_total': min(total_marks) if total_marks else 0,
            'total_students': len(records),
            'students_with_complete_marks': len(total_marks),
            'grading_system': self.grading_system
        }
    
    def get_expected_template(self) -> Dict:
        """Get expected template structure for multiple subjects"""
        return {
            'required_base_columns': self.base_columns,
            'subject_columns': self.subjects,
            'instructions': 'Fill marks in subject columns only. Do not edit student information.',
            'validation_rules': {
                'marks_range': '0-100 for all subjects',
                'required_fields': self.base_columns[:3],
                'optional_fields': self.base_columns[3:] + ['Remarks']
            }
        }