"""
Essential utilities for PDF generation
"""
import os
from datetime import datetime
from typing import Optional, Dict

class SafeImageHandler:
    """Safe image handling - won't crash if logo missing"""
    
    @staticmethod
    def load_logo(logo_path: str):
        """Load logo safely"""
        if not logo_path or not os.path.exists(logo_path):
            return None
        
        try:
            from reportlab.lib.utils import ImageReader
            return ImageReader(logo_path)
        except:
            return None

class ReportMetadata:
    """Simple metadata for reports"""
    
    def __init__(self, school_info: Dict = None, exam_info: Dict = None):
        self.school_info = school_info or {}
        self.exam_info = exam_info or {}
        self.generated_at = datetime.now()
        self.system = "EDU-MANAGER PRO v2.0"
    
    def to_dict(self):
        """Convert to dictionary for PDF metadata"""
        return {
            "school": self.school_info.get('name', ''),
            "exam": self.exam_info.get('exam_id', ''),
            "class": self.exam_info.get('class_id', ''),
            "generated": self.generated_at.isoformat(),
            "system": self.system
        }