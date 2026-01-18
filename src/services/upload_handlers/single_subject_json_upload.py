# services/upload_handlers/single_subject_upload.py
"""
SINGLE SUBJECT EXCEL EXTRACTOR
Extract raw data from single subject Excel
"""

class SingleSubjectUploadHandler:
    
    def process_upload(self, excel_file_path: str) -> dict:
        try:
            # Read with header=0
            df = pd.read_excel(excel_file_path, header=0)
            
            # Clean columns
            df.columns = [self._clean_col_name(col) for col in df.columns]
            
            # Extract data
            students = []
            for _, row in df.iterrows():
                student = {
                    'admission_no': str(row.get('admission_no', '')).strip(),
                    'student_id': str(row.get('student_id', '')).strip(),
                    'full_name': str(row.get('full_name', '')).strip(),
                    'gender': self._normalize_gender(row.get('gender')),
                    'class': str(row.get('class', '')).strip(),
                    'stream': str(row.get('stream', '')).strip(),
                    'marks': self._safe_float(row.get(self.subject_name)) if self.subject_name in df.columns else None,
                    'remarks': str(row.get('remarks', '')).strip()
                }
                students.append(student)
            
            return {
                'success': True,
                'subject': self.subject_name,
                'raw_students': students,
                'extraction_info': {
                    'student_count': len(students),
                    'has_marks': any(s['marks'] is not None for s in students)
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _clean_col_name(self, col):
        """Same cleaning logic as multi-subject"""
        # ... implementation ...