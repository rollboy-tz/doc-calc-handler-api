"""
base_template.py - UPGRADED VERSION
Same logic, better design
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Spacer
from reportlab.lib.units import inch
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BasePDFTemplate:
    """Upgraded base template with professional styling"""
    
    def __init__(self, system_config=None):
        self.system_config = system_config or self._default_config()
        self.styles = self._get_enhanced_styles()
        self.colors = self._get_color_palette()
    
    def _default_config(self):
        """System metadata - SAME LOGIC"""
        return {
            "system_name": "EDU-MANAGER PRO",
            "version": "2.5",
            "copyright": f"© {datetime.now().year} EduManager Pro",
            "author": "EDU-MANAGER REPORT SYSTEM",
            "company": "EduManager Solutions Ltd",
            "generator": "Enhanced ReportLab Engine"
        }
    
    def _get_enhanced_styles(self):
        """Enhanced styles - SAME LOGIC, BETTER STYLES"""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='SchoolHeader',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=12,
            alignment=1  # Center
        ))
        
        styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2980B9'),
            spaceAfter=8,
            alignment=1
        ))
        
        styles.add(ParagraphStyle(
            name='StudentInfo',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495E'),
            leftIndent=20
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#16A085'),
            spaceAfter=6,
            backColor=colors.HexColor('#F8F9FA'),
            borderPadding=5
        ))
        
        styles.add(ParagraphStyle(
            name='FooterText',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.grey
        ))
        
        return styles
    
    def _get_color_palette(self):
        """Professional color palette"""
        return {
            'primary': colors.HexColor('#2980B9'),
            'secondary': colors.HexColor('#2C3E50'),
            'success': colors.HexColor('#27AE60'),
            'warning': colors.HexColor('#F39C12'),
            'danger': colors.HexColor('#E74C3C'),
            'light': colors.HexColor('#F8F9FA'),
            'dark': colors.HexColor('#343A40'),
            'header': colors.HexColor('#2C3E50'),
            'row_even': colors.HexColor('#F8F9FA'),
            'row_odd': colors.white
        }
    
    def create_document(self, filepath, title, subject=None, author=None):
        """Create PDF document - SAME LOGIC, METADATA FIXED"""
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            title=title,
            author=author or self.system_config['author'],
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Store metadata for later
        doc._custom_metadata = {
            'subject': subject or "Academic Report",
            'creator': self.system_config['system_name'],
            'producer': f"{self.system_config['system_name']} v{self.system_config['version']}",
            'keywords': "education, report, academic, results"
        }
        
        return doc
    
    def _add_metadata_to_canvas(self, canvas, doc):
        """Add metadata - SAME LOGIC"""
        try:
            if hasattr(doc, '_custom_metadata'):
                metadata = doc._custom_metadata
                canvas.setSubject(metadata.get('subject', ''))
                canvas.setCreator(metadata.get('creator', ''))
                canvas.setProducer(metadata.get('producer', ''))
                canvas.setKeywords(metadata.get('keywords', ''))
        except:
            pass
    
    def add_professional_header(self, canvas, doc, school_name=None):
        """Enhanced header"""
        try:
            canvas.saveState()
            
            # School name header
            if school_name:
                canvas.setFont('Helvetica-Bold', 14)
                canvas.setFillColor(self.colors['primary'])
                canvas.drawCentredString(doc.width/2 + doc.leftMargin, 
                                        doc.height + doc.topMargin - 20, 
                                        school_name)
            
            # System watermark
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.HexColor('#E8E8E8'))
            canvas.rotate(45)
            canvas.drawString(200, -150, self.system_config['system_name'])
            canvas.rotate(-45)
            
            canvas.restoreState()
        except:
            pass
    
    def add_footer(self, canvas, doc):
        """Enhanced footer"""
        try:
            self._add_metadata_to_canvas(canvas, doc)
            
            canvas.saveState()
            
            # Footer background
            canvas.setFillColor(self.colors['light'])
            canvas.rect(doc.leftMargin, 15, doc.width, 20, fill=1, stroke=0)
            
            # Page number
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(self.colors['dark'])
            page_text = f"Page {canvas.getPageNumber()}"
            canvas.drawRightString(doc.width + doc.leftMargin - 10, 20, page_text)
            
            # System info
            system_text = f"{self.system_config['system_name']} v{self.system_config['version']}"
            canvas.drawString(doc.leftMargin, 20, system_text)
            
            # Timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            canvas.drawCentredString(doc.width/2 + doc.leftMargin, 20, timestamp)
            
            # Copyright
            canvas.setFont('Helvetica', 6)
            canvas.setFillColor(colors.grey)
            canvas.drawCentredString(doc.width/2 + doc.leftMargin, 10, 
                                   self.system_config['copyright'])
            
            canvas.restoreState()
        except Exception as e:
            logger.warning(f"Footer error: {e}")