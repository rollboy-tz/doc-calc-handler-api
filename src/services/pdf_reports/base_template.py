"""
base_template.py - UPGRADED WITH LANDSCAPE SUPPORT
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Spacer, PageBreak
from reportlab.lib.units import inch, mm
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BasePDFTemplate:
    """Enhanced base template with landscape support"""
    
    def __init__(self, system_config=None):
        self.system_config = system_config or self._default_config()
        self.styles = self._get_enhanced_styles()
        self.colors = self._get_color_palette()
    
    def _default_config(self):
        """System metadata"""
        return {
            "system_name": "EDU-MANAGER PRO",
            "version": "3.0",
            "copyright": f"© {datetime.now().year} EduManager Pro",
            "author": "EDU-MANAGER REPORT SYSTEM",
            "company": "EduManager Solutions Ltd",
            "generator": "Professional Report Engine"
        }
    
    def _get_enhanced_styles(self):
        """Enhanced styles for better typography"""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='SchoolHeader',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=10,
            alignment=1,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2980B9'),
            spaceAfter=8,
            alignment=1,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#16A085'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='DataLabel',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#34495E'),
            fontName='Helvetica'
        ))
        
        styles.add(ParagraphStyle(
            name='TableCell',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=0,
            leading=10
        ))
        
        styles.add(ParagraphStyle(
            name='TableCellCenter',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=1,  # Center
            leading=10
        ))
        
        styles.add(ParagraphStyle(
            name='TableCellRight',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=2,  # Right
            leading=10
        ))
        
        styles.add(ParagraphStyle(
            name='FooterText',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.grey,
            fontName='Helvetica'
        ))
        
        return styles
    
    def _get_color_palette(self):
        """Professional color palette"""
        return {
            'primary': colors.HexColor('#2980B9'),      # Blue
            'secondary': colors.HexColor('#2C3E50'),    # Dark Blue
            'accent': colors.HexColor('#16A085'),       # Teal
            'success': colors.HexColor('#27AE60'),      # Green
            'warning': colors.HexColor('#F39C12'),      # Orange
            'danger': colors.HexColor('#E74C3C'),       # Red
            'light': colors.HexColor('#F8F9FA'),        # Light Gray
            'dark': colors.HexColor('#343A40'),         # Dark Gray
            'header': colors.HexColor('#2C3E50'),       # Table Header
            'row_even': colors.HexColor('#F8F9FA'),     # Even Row
            'row_odd': colors.white,                    # Odd Row
            'border': colors.HexColor('#DDDDDD')        # Table Border
        }
    
    def create_document(self, filepath, title, subject=None, author=None, orientation='portrait'):
        """Create PDF document with orientation support"""
        pagesize = A4
        if orientation == 'landscape':
            pagesize = landscape(A4)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=pagesize,
            title=title,
            author=author or self.system_config['author'],
            rightMargin=36,
            leftMargin=36,
            topMargin=50,
            bottomMargin=40
        )
        
        doc._custom_metadata = {
            'subject': subject or "Academic Report",
            'creator': self.system_config['system_name'],
            'producer': f"{self.system_config['system_name']} v{self.system_config['version']}",
            'keywords': "education, report, academic, results, school"
        }
        
        return doc
    
    def _add_metadata_to_canvas(self, canvas, doc):
        """Add metadata to PDF canvas"""
        try:
            if hasattr(doc, '_custom_metadata'):
                metadata = doc._custom_metadata
                canvas.setSubject(metadata.get('subject', ''))
                canvas.setCreator(metadata.get('creator', ''))
                canvas.setProducer(metadata.get('producer', ''))
                canvas.setKeywords(metadata.get('keywords', ''))
        except:
            pass
    
    def add_professional_header(self, canvas, doc, school_name=None, page_title=None):
        """Enhanced header with school name and page title"""
        try:
            canvas.saveState()
            
            # School name at top
            if school_name:
                canvas.setFont('Helvetica-Bold', 14)
                canvas.setFillColor(self.colors['primary'])
                canvas.drawCentredString(doc.width/2 + doc.leftMargin, 
                                        doc.height + doc.topMargin - 25, 
                                        school_name.upper())
            
            # Page title
            if page_title:
                canvas.setFont('Helvetica', 10)
                canvas.setFillColor(self.colors['secondary'])
                canvas.drawCentredString(doc.width/2 + doc.leftMargin, 
                                        doc.height + doc.topMargin - 45, 
                                        page_title)
            
            # Separator line
            canvas.setStrokeColor(self.colors['border'])
            canvas.setLineWidth(0.5)
            canvas.line(doc.leftMargin, 
                       doc.height + doc.topMargin - 50, 
                       doc.width + doc.leftMargin, 
                       doc.height + doc.topMargin - 50)
            
            canvas.restoreState()
        except Exception as e:
            logger.warning(f"Header error: {e}")
    
    def add_footer(self, canvas, doc):
        """Enhanced footer with pagination"""
        try:
            self._add_metadata_to_canvas(canvas, doc)
            
            canvas.saveState()
            
            # Footer line
            canvas.setStrokeColor(self.colors['border'])
            canvas.setLineWidth(0.5)
            canvas.line(doc.leftMargin, 35, doc.width + doc.leftMargin, 35)
            
            # Page number
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(self.colors['dark'])
            page_num = canvas.getPageNumber()
            total_pages = f" of {page_num}"  # Simple approach
            
            canvas.drawRightString(doc.width + doc.leftMargin - 10, 25, 
                                 f"Page {page_num}")
            
            # System info
            canvas.drawString(doc.leftMargin, 25, 
                            f"{self.system_config['system_name']} v{self.system_config['version']}")
            
            # Timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            canvas.drawCentredString(doc.width/2 + doc.leftMargin, 25, timestamp)
            
            # Copyright at bottom
            canvas.setFont('Helvetica', 6)
            canvas.setFillColor(colors.grey)
            canvas.drawCentredString(doc.width/2 + doc.leftMargin, 15, 
                                   self.system_config['copyright'])
            
            canvas.restoreState()
        except Exception as e:
            logger.warning(f"Footer error: {e}")