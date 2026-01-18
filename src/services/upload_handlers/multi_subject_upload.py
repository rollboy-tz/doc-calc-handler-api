# services/upload_handlers/multi_subject_upload.py
"""
MULTI SUBJECT EXCEL EXTRACTOR
Extract raw data from Excel - NO grade calculations
Returns clean JSON for dashboard to edit/process
"""
import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class MultiSubjectUploadHandler:
    """
    Extract data from multi-subject Excel file
    Returns raw data for dashboard processing
    """
    
    def __init__(self):
        # No grading rules needed - just extraction
        pass
    
    def process_upload(self, excel_file_path: str) -> Dict:
        """
        Extract raw data from Excel file
        
        Args:
            excel_file_path: Path to uploaded Excel file
            
        Returns:
            Dictionary with extracted raw data
        """
        try:
            # 1. Read Excel file - ALWAYS use header=0 (row 1 is headers)
            df = pd.read_excel(excel_file_path, header=0)
            
            # 2. Clean column names (remove extra spaces, normalize)
            df.columns = [self._clean_column_name(col) for col in df.columns]
            
            logger.info(f"📊 File loaded: {len(df)} rows, {len(df.columns)} columns")
            logger.info(f"📋 Columns found: {df.columns.tolist()}")
            
            # 3. Validate basic structure
            validation = self._validate_structure(df)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Invalid file structure',
                    'details': validation['errors']
                }
            
            # 4. Extract raw student data
            student_records = self._extract_raw_data(df)
            
            # 5. Return raw data for dashboard
            return {
                'success': True,
                'extraction_type': 'excel',
                'student_count': len(student_records),
                'subjects_found': self._get_subjects_from_data(df),
                'raw_students': student_records,
                'file_info': {
                    'columns': df.columns.tolist(),
                    'rows': len(df),
                    'subjects_count': len(self._get_subjects_from_data(df))
                },
                'notes': [
                    'Data extracted successfully',
                    'No grade calculations performed',
                    'Send this data to /api/process/multi-subject/json for processing'
                ]
            }
            
        except Exception as e:
            logger.error(f"Excel extraction failed: {str(e)}")
            return {
                'success': False,
                'error': f'Extraction failed: {str(e)}'
            }
    
    def _clean_column_name(self, col_name) -> str:
        """Clean and normalize column names"""
        if not isinstance(col_name, str):
            col_name = str(col_name)
        
        # Clean up the name
        cleaned = col_name.strip()
        
        # Remove "Unnamed: " prefixes
        if cleaned.startswith('Unnamed:'):
            return 'remarks' if 'remarks' in cleaned.lower() else 'extra_' + cleaned.split(':')[-1].strip()
        
        # Convert to lowercase and replace spaces
        cleaned = cleaned.lower().replace(' ', '_').replace('-', '_')
        
        # Handle common variations
        name_mapping = {
            'adm_no': 'admission_no',
            'student_no': 'student_id',
            'name': 'full_name',
            'sex': 'gender',
            'class_name': 'class',
            'stream_name': 'stream',
            'comment': 'remarks'
        }
        
        return name_mapping.get(cleaned, cleaned)
    
    def _validate_structure(self, df: pd.DataFrame) -> Dict:
        """Basic validation of Excel structure"""
        errors = []
        
        # Check for required columns
        required_columns = ['admission_no', 'student_id', 'full_name']
        for col in required_columns:
            if col not in df.columns:
                errors.append(f'Missing column: {col}')
        
        # Check for at least one subject column
        subject_columns = self._get_subjects_from_data(df)
        if not subject_columns:
            errors.append('No subject columns found')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _get_subjects_from_data(self, df: pd.DataFrame) -> List[str]:
        """Get subject columns from DataFrame"""
        # Student info columns
        student_columns = {
            'admission_no', 'student_id', 'full_name', 
            'gender', 'class', 'stream', 'remarks'
        }
        
        # All columns that are NOT student info are subjects
        subject_columns = []
        for col in df.columns:
            if col not in student_columns:
                subject_columns.append(col)
        
        return subject_columns
    
    def _extract_raw_data(self, df: pd.DataFrame) -> List[Dict]:
        """Extract raw student data from DataFrame"""
        student_records = []
        
        for _, row in df.iterrows():
            # Skip rows with missing essential info
            if pd.isna(row.get('admission_no')) or pd.isna(row.get('student_id')):
                continue
            
            # Build student record
            student = {
                'admission_no': self._safe_str(row.get('admission_no')),
                'student_id': self._safe_str(row.get('student_id')),
                'full_name': self._safe_str(row.get('full_name', '')),
                'gender': self._safe_gender(row.get('gender')),
                'class': self._safe_str(row.get('class', '')),
                'stream': self._safe_str(row.get('stream', '')),
                'subjects': {},
                'remarks': self._safe_str(row.get('remarks', ''))
            }
            
            # Add subject marks
            subject_columns = self._get_subjects_from_data(df)
            for subject in subject_columns:
                if subject in df.columns:
                    mark = row[subject]
                    if pd.notna(mark):
                        try:
                            student['subjects'][subject] = float(mark)
                        except (ValueError, TypeError):
                            student['subjects'][subject] = None
                    else:
                        student['subjects'][subject] = None
            
            student_records.append(student)
        
        return student_records
    
    def _safe_str(self, value):
        """Safely convert value to string"""
        if pd.isna(value):
            return ''
        return str(value).strip()
    
    def _safe_gender(self, value):
        """Safely convert gender to M/F"""
        if pd.isna(value):
            return 'M'
        
        gender_str = str(value).strip().upper()
        if gender_str in ['M', 'MALE']:
            return 'M'
        elif gender_str in ['F', 'FEMALE']:
            return 'F'
        else:
            return 'M'  # Default