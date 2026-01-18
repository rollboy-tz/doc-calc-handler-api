# services/validators/excel_validator.py
"""
EXCEL VALIDATOR - Validate Excel file uploads
"""
import os
from typing import Dict
from .base_validator import BaseValidator

class ExcelValidator(BaseValidator):
    """Validate Excel files for school management system"""
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}
    
    # Maximum file size (5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    def __init__(self):
        super().__init__()
        self.file_path: str = None
        self.file_size: int = 0
    
    def validate(self, file_path: str) -> bool:
        """
        Validate Excel file
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            bool: True if valid, False otherwise
        """
        self.file_path = file_path
        self.clear_errors()
        
        # Check 1: File exists
        if not self._check_file_exists():
            return False
        
        # Check 2: File extension
        if not self._check_file_extension():
            return False
        
        # Check 3: File size
        if not self._check_file_size():
            return False
        
        # Check 4: File can be opened (basic check)
        if not self._check_file_readable():
            return False
        
        self.is_valid = True
        return True
    
    def _check_file_exists(self) -> bool:
        """Check if file exists"""
        if not os.path.exists(self.file_path):
            self.add_error(f"File does not exist: {self.file_path}")
            return False
        return True
    
    def _check_file_extension(self) -> bool:
        """Check file extension"""
        _, ext = os.path.splitext(self.file_path)
        if ext.lower() not in self.ALLOWED_EXTENSIONS:
            self.add_error(f"Invalid file extension: {ext}. Allowed: {self.ALLOWED_EXTENSIONS}")
            return False
        return True
    
    def _check_file_size(self) -> bool:
        """Check file size"""
        try:
            self.file_size = os.path.getsize(self.file_path)
            if self.file_size > self.MAX_FILE_SIZE:
                self.add_error(f"File too large: {self.file_size} bytes. Max: {self.MAX_FILE_SIZE} bytes")
                return False
        except OSError:
            self.add_error("Cannot determine file size")
            return False
        return True
    
    def _check_file_readable(self) -> bool:
        """Basic check if file can be opened"""
        try:
            with open(self.file_path, 'rb') as f:
                f.read(100)  # Read first 100 bytes
            return True
        except Exception as e:
            self.add_error(f"Cannot read file: {str(e)}")
            return False
    
    def get_validation_summary(self) -> Dict:
        """Get validation summary"""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'file_info': {
                'path': self.file_path,
                'size_bytes': self.file_size,
                'size_mb': round(self.file_size / (1024 * 1024), 2)
            }
        }