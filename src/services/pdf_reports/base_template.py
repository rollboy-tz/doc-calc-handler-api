"""
base_template.py - FIXED WITH ALL STYLES
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
    """Fixed base template with ALL required styles"""
    
    def __init__(self, system_config=None):
        self.system_config = system_config or self._default_config()
        self.styles = self._get_complete_styles()  # CHANGED: Complete styles
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
    
    def _get_complete_styles(self):
        """Get COMPLETE styles including all required ones"""
        styles = getSampleStyleSheet()
        
        # ADD ALL REQUIRED STYLES
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
        
        # ✨ ADD MISSING STYLE: SectionHeader
        styles.add(ParagraphStyle(
            name='SectionHeader',  # THIS WAS MISSING
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#16A085'),
            spaceAfter=6,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#F8F9FA'),
            borderPadding=5
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
            alignment=1,
            leading=10
        ))
        
        styles.add(ParagraphStyle(
            name='TableCellRight',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=2,
            leading=10
        ))
        
        styles.add(ParagraphStyle(
            name='FooterText',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.grey,
            fontName='Helvetica'
        ))
        
        # Add more styles that might be needed
        styles.add(ParagraphStyle(
            name='Heading1',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Heading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2980B9'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Heading3',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#16A085'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Normal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            fontName='Helvetica'
        ))
        
        styles.add(ParagraphStyle(
            name='Italic',
            parent=styles['Italic'],
            fontSize=9,
            textColor=colors.grey,
            fontName='Helvetica-Oblique'
        ))
        
        return styles
    
    def _get_color_palette(self):
        """Professional color palette"""
        return {
            'primary': colors.HexColor('#2980B9'),
            'secondary': colors.HexColor('#2C3E50'),
            'accent': colors.HexColor('#16A085'),
            'success': colors.HexColor('#27AE60'),
            'warning': colors.HexColor('#F39C12'),
            'danger': colors.HexColor('#E74C3C'),
            'light': colors.HexColor('#F8F9FA'),
            'dark': colors.HexColor('#343A40'),
            'header': colors.HexColor('#2C3E50'),
            'row_even': colors.HexColor('#F8F9FA'),
            'row_odd': colors.white,
            'border': colors.HexColor('#DDDDDD')
        }
    
    def create_document(self, filepath, title, subject=None, author=None, orientation='portrait'):
        """Create PDF document"""
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
        """Enhanced header"""
        try:
            canvas.saveState()
            
            if school_name:
                canvas.setFont('Helvetica-Bold', 14)
                canvas.setFillColor(self.colors['primary'])
                canvas.drawCentredString(doc.width/2 + doc.leftMargin, 
                                        doc.height + doc.topMargin - 25, 
                                        school_name.upper())
            
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
        """Enhanced footer"""
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
            
            canvas.drawRightString(doc.width + doc.leftMargin - 10, 25, 
                                 f"Page {page_num}")
            
            # System info
            canvas.drawString(doc.leftMargin, 25, 
                            f"{self.system_config['system_name']} v{self.system_config['version']}")
            
            # Timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            canvas.drawCentredString(doc.width/2 + doc.leftMargin, 25, timestamp)
            
            # Copyright
            canvas.setFont('Helvetica', 6)
            canvas.setFillColor(colors.grey)
            canvas.drawCentredString(doc.width/2 + doc.leftMargin, 15, 
                                   self.system_config['copyright'])
            
            canvas.restoreState()
        except Exception as e:
            logger.warning(f"Footer error: {e}")