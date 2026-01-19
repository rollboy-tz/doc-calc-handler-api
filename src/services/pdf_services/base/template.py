"""
services/pdf_services/base/template.py
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PDFBaseTemplate:
    """Base template with proper footer and metadata"""
    
    def __init__(self, system_config=None):
        self.system_config = system_config or self._get_default_config()
        self.styles = getSampleStyleSheet()
    
    def _get_default_config(self):
        """Default system configuration"""
        return {
            "system_name": "EDU-MANAGER PRO",
            "version": "3.0",
            "domain": "edumanager.ac.tz",
            "support_email": "support@edumanager.ac.tz",
            "support_phone": "+255 123 456 789",
            "company": "EduManager Solutions Ltd",
            "copyright": f"© {datetime.now().year} EduManager Solutions Ltd"
        }
    
    def create_document(self, filepath, title, subject=None, author=None, orientation='portrait'):
        """
        Create PDF document with proper metadata
        
        Args:
            filepath: Path to save PDF
            title: Document title
            subject: Document subject
            author: Document author
            orientation: 'portrait' or 'landscape'
        
        Returns:
            SimpleDocTemplate object
        """
        pagesize = A4
        if orientation == 'landscape':
            pagesize = landscape(A4)
        
        # Create document with metadata
        doc = SimpleDocTemplate(
            filepath,
            pagesize=pagesize,
            title=title,
            author=author or self.system_config['system_name'],
            rightMargin=40,
            leftMargin=40,
            topMargin=60,  # Space for header
            bottomMargin=50  # Space for footer
        )
        
        # Store metadata for later use
        doc._custom_metadata = {
            'subject': subject or "Academic Report",
            'creator': self.system_config['system_name'],
            'producer': f"{self.system_config['system_name']} v{self.system_config['version']}",
            'keywords': "education, report, academic, school"
        }
        
        return doc
    
    def add_metadata_to_canvas(self, canvas, doc):
        """Add PDF metadata to canvas"""
        try:
            if hasattr(doc, '_custom_metadata'):
                metadata = doc._custom_metadata
                canvas.setTitle(doc.title)
                canvas.setAuthor(doc.author)
                canvas.setSubject(metadata.get('subject', ''))
                canvas.setCreator(metadata.get('creator', ''))
                canvas.setProducer(metadata.get('producer', ''))
                canvas.setKeywords(metadata.get('keywords', ''))
        except Exception as e:
            logger.warning(f"Metadata error: {e}")
    
    def add_footer(self, canvas, doc):
        """
        Add footer to PDF
        
        Layout:
        LEFT: System domain
        CENTER: Page number
        RIGHT: Support contact info
        """
        try:
            # Add metadata first
            self.add_metadata_to_canvas(canvas, doc)
            
            canvas.saveState()
            
            # Footer configuration
            footer_y = 30
            font_name = 'Helvetica'
            font_size = 8
            
            # LEFT: System domain
            canvas.setFont(font_name, font_size)
            canvas.setFillColor(colors.HexColor('#666666'))
            left_text = f"www.{self.system_config['domain']}"
            canvas.drawString(doc.leftMargin, footer_y, left_text)
            
            # CENTER: Page number
            page_num = canvas.getPageNumber()
            center_text = f"Page {page_num}"
            canvas.drawCentredString(doc.width/2 + doc.leftMargin, footer_y, center_text)
            
            # RIGHT: Support contact
            right_text = f"Support: {self.system_config['support_phone']} | {self.system_config['support_email']}"
            canvas.drawRightString(doc.width + doc.leftMargin, footer_y, right_text)
            
            # Separator line
            canvas.setStrokeColor(colors.HexColor('#DDDDDD'))
            canvas.setLineWidth(0.5)
            canvas.line(doc.leftMargin, footer_y + 15, 
                       doc.width + doc.leftMargin, footer_y + 15)
            
            canvas.restoreState()
            
        except Exception as e:
            logger.warning(f"Footer error: {e}")
    
    def add_header(self, canvas, doc, school_name=None, report_title=None):
        """
        Add header to PDF
        
        Args:
            canvas: PDF canvas
            doc: Document object
            school_name: Name of school
            report_title: Title of report
        """
        try:
            canvas.saveState()
            
            # Top margin for header
            header_y = doc.height + doc.topMargin - 20
            
            # School name at top
            if school_name:
                canvas.setFont('Helvetica-Bold', 14)
                canvas.setFillColor(colors.HexColor('#2C3E50'))
                canvas.drawCentredString(doc.width/2 + doc.leftMargin, header_y, school_name)
            
            # Report title below school name
            if report_title:
                canvas.setFont('Helvetica', 11)
                canvas.setFillColor(colors.HexColor('#2980B9'))
                canvas.drawCentredString(doc.width/2 + doc.leftMargin, header_y - 20, report_title)
            
            # Separator line
            canvas.setStrokeColor(colors.HexColor('#DDDDDD'))
            canvas.setLineWidth(0.5)
            canvas.line(doc.leftMargin, header_y - 30, 
                       doc.width + doc.leftMargin, header_y - 30)
            
            canvas.restoreState()
            
        except Exception as e:
            logger.warning(f"Header error: {e}")