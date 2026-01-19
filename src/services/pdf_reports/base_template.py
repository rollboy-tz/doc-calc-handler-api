"""
base_template.py - FIXED
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BasePDFTemplate:
    """Base template with system branding"""
    
    def __init__(self, system_config=None):
        self.system_config = system_config or self._default_config()
        self.styles = getSampleStyleSheet()
        self._setup_styles()  # ✨ This calls the method
    
    def _default_config(self):
        """System metadata"""
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
    
    def _setup_styles(self):
        """Setup PDF styles - ✨ THIS METHOD WAS MISSING!"""
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.grey,
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.navy,
            alignment=1,  # Center
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='SchoolHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.darkblue,
            alignment=1,
            spaceAfter=6
        ))
    
    def create_document(self, filepath, title, subject=None, author=None):
        """Create PDF document with proper metadata"""
        from reportlab.lib.pagesizes import A4
        
        # Prepare metadata
        metadata = {
            'title': title,
            'author': author or self.system_config['author'],
            'subject': subject or self.system_config['subject'],
            'keywords': self.system_config['keywords'],
            'creator': self.system_config['system_name'],
            'producer': f"{self.system_config['system_name']} v{self.system_config['version']}",
        }
        
        # Create document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            **metadata
        )
        
        return doc
    
    def add_footer(self, canvas, doc):
        """Add system footer to every page"""
        try:
            canvas.saveState()
            canvas.setFont('Helvetica', 7)
            canvas.setFillColor(colors.grey)
            
            footer_text = f"{self.system_config['system_name']} v{self.system_config['version']} | {self.system_config['copyright']} | Page {canvas.getPageNumber()}"
            canvas.drawCentredString(doc.width/2, 15, footer_text)
            
            canvas.drawString(40, 15, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            canvas.restoreState()
        except Exception as e:
            logger.warning(f"Footer error: {e}")