# services/extractors/single_subject_extractor.py
"""
SINGLE SUBJECT EXTRACTOR
Extract data from single subject Excel files
"""
import pandas as pd
from typing import Dict, List
from .base_extractor import BaseExtractor

class SingleSubjectExtractor(BaseExtractor):
    """Extract student data from single subject Excel files"""
    
    def __init__(self, file_path: str, subject_name: str = None):
        super().__init__(file_path)
        self.subject_name = subject_name
    
    def extract(self) -> Dict:
        """
        Extract single subject data from Excel
        
        Returns:
            Dict with extracted student data
        """
        try:
            # Read Excel file
            df = self._read_excel()
            
            # Clean column names
            df.columns = [self.clean_column_name(col) for col in df.columns]
            
            # Detect subject name if not provided
            if not self.subject_name:
                self.subject_name = self._detect_subject_name(df)
            
            # Extract student records
            self.raw_data = self._extract_student_records(df)
            
            # Set metadata
            self.metadata = {
                'extractor_type': 'single_subject',
                'subject_name': self.subject_name,
                'student_count': len(self.raw_data),
                'columns_found': df.columns.tolist()
            }
            
            return {
                'success': True,
                'data': self.raw_data,
                'metadata': self.metadata,
                'summary': f"Extracted {len(self.raw_data)} student records for subject: {self.subject_name}"
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
        """Read Excel file"""
        # Try with header row 0 (most common)
        try:
            df = pd.read_excel(self.file_path, header=0)
            return df
        except Exception:
            # Fallback to no header
            df = pd.read_excel(self.file_path, header=None)
            if len(df) > 0:
                # Use first row as headers
                df.columns = df.iloc[0]
                df = df.iloc[1:].reset_index(drop=True)
            return df
    
    def _detect_subject_name(self, df: pd.DataFrame) -> str:
        """Detect subject name from Excel columns"""
        student_columns = {'admission_no', 'student_id', 'full_name', 'gender', 'class', 'stream', 'remarks'}
        
        # Find non-student columns
        for col in df.columns:
            if col not in student_columns:
                return col
        
        return 'Subject'  # Default
    
    def _extract_student_records(self, df: pd.DataFrame) -> List[Dict]:
        """Extract student records"""
        students = []
        
        for _, row in df.iterrows():
            # Skip rows without basic info
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
                'marks': self.safe_float(row.get(self.subject_name))
            }
            
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