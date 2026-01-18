# services/extractors/multi_subject_extractor.py
"""
MULTI SUBJECT EXTRACTOR
Extract data from multi-subject Excel files
"""
import pandas as pd
from typing import Dict, List, Any
from .base_extractor import BaseExtractor

class MultiSubjectExtractor(BaseExtractor):
    """Extract student data from multi-subject Excel files"""
    
    # Student information columns (should be in every file)
    STUDENT_INFO_COLUMNS = {
        'admission_no', 'student_id', 'full_name',
        'gender', 'class', 'stream', 'remarks'
    }
    
    def extract(self) -> Dict:
        """
        Extract multi-subject data from Excel
        
        Returns:
            Dict with extracted student data
        """
        try:
            # Read Excel file
            df = self._read_excel()
            
            # Clean column names
            df.columns = [self.clean_column_name(col) for col in df.columns]
            
            # Identify subject columns
            subject_columns = self._identify_subject_columns(df)
            
            # Extract student records
            self.raw_data = self._extract_student_records(df, subject_columns)
            
            # Set metadata
            self.metadata = {
                'extractor_type': 'multi_subject',
                'subject_columns': subject_columns,
                'student_count': len(self.raw_data),
                'columns_found': df.columns.tolist(),
                'file_shape': df.shape
            }
            
            return {
                'success': True,
                'data': self.raw_data,
                'metadata': self.metadata,
                'summary': f"Extracted {len(self.raw_data)} student records with {len(subject_columns)} subjects"
            }
            
        except Exception as e:
            self.add_error(f"Extraction failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': [],
                'metadata': {}
            }
    
    def _read_excel(self) -> pd.DataFrame:
        """Read Excel file with proper header detection"""
        # Try different header options
        for header_row in [0, 1, None]:
            try:
                df = pd.read_excel(self.file_path, header=header_row)
                
                # Check if we have reasonable column names
                if header_row is None:
                    # Use first row as headers
                    if len(df) > 0:
                        df.columns = df.iloc[0]
                        df = df.iloc[1:].reset_index(drop=True)
                
                # Check if we have student info columns
                normalized_columns = {self.clean_column_name(col) for col in df.columns}
                if 'admission_no' in normalized_columns or 'student_id' in normalized_columns:
                    return df
                    
            except Exception:
                continue
        
        raise ValueError("Cannot read Excel file with proper structure")
    
    def _identify_subject_columns(self, df: pd.DataFrame) -> List[str]:
        """Identify which columns are subject marks"""
        all_columns = df.columns.tolist()
        
        # Subject columns are those not in student info
        subject_columns = []
        for col in all_columns:
            if col not in self.STUDENT_INFO_COLUMNS:
                subject_columns.append(col)
        
        return subject_columns
    
    def _extract_student_records(self, df: pd.DataFrame, subject_columns: List[str]) -> List[Dict]:
        """Extract individual student records"""
        students = []
        
        for _, row in df.iterrows():
            # Skip rows without admission number or student ID
            if pd.isna(row.get('admission_no')) and pd.isna(row.get('student_id')):
                continue
            
            # Create student record
            student = {
                'admission_no': self.safe_string(row.get('admission_no', '')),
                'student_id': self.safe_string(row.get('student_id', '')),
                'full_name': self.safe_string(row.get('full_name', '')),
                'gender': self._normalize_gender(row.get('gender')),
                'class': self.safe_string(row.get('class', '')),
                'stream': self.safe_string(row.get('stream', '')),
                'remarks': self.safe_string(row.get('remarks', '')),
                'subjects': {}
            }
            
            # Add subject marks
            for subject in subject_columns:
                if subject in df.columns:
                    student['subjects'][subject] = self.safe_float(row[subject])
            
            students.append(student)
        
        return students
    
    def _normalize_gender(self, value: Any) -> str:
        """Normalize gender to M/F"""
        gender = self.safe_string(value).upper()
        
        if gender in ['M', 'MALE']:
            return 'M'
        elif gender in ['F', 'FEMALE']:
            return 'F'
        else:
            return 'M'  # Default