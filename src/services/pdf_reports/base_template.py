"""
base_template.py - ADD PDF METADATA
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BasePDFTemplate:
    """Base template with system branding and metadata"""
    
    def __init__(self, system_config=None):
        self.system_config = system_config or self._default_config()
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _default_config(self):
        """System metadata for PDF properties"""
        return {
            "system_name": "EDU-MANAGER PRO",
            "version": "2.0",
            "copyright": f"© {datetime.now().year} EduManager Pro",
            "support": "support@edumanager.com",
            "author": "EDU-MANAGER REPORT SYSTEM",
            "generator": "Python ReportLab",
            "company": "EduManager Solutions Ltd",
            "subject": "Student Academic Report",
            "keywords": "report, academic, school, results, tanzania, education"
        }
    
    def create_document(self, filepath, title, subject=None, author=None):
        """Create PDF document with proper metadata"""
        # Prepare metadata
        metadata = {
            'title': title,
            'author': author or self.system_config['author'],
            'subject': subject or self.system_config['subject'],
            'keywords': self.system_config['keywords'],
            'creator': self.system_config['system_name'],
            'producer': f"{self.system_config['system_name']} v{self.system_config['version']}",
        }
        
        # Create document with metadata
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            **metadata  # Pass metadata to document
        )
        
        return doc