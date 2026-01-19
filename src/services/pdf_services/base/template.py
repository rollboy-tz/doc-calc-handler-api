"""
Base PDF template using fpdf2 - COMPACT VERSION
"""
from fpdf import FPDF
from datetime import datetime
from .constants import PDFConstants

class BasePDFTemplate(FPDF):
    """Base class for all PDF generators - COMPACT DESIGN"""
    
    def __init__(self, config: dict = None):
        super().__init__()
        self.config = {**PDFConstants.SYSTEM_CONFIG, **(config or {})}
        self.constants = PDFConstants
        
        # COMPACT Setup
        self.set_margins(10, 10, 10)  # Smaller margins
        self.set_auto_page_break(auto=True, margin=10)  # Smaller bottom margin
        self.set_display_mode(zoom="default")
        
        # Add first page
        self.add_page()
        self._setup_fonts()
    
    def _setup_fonts(self):
        """Setup fonts"""
        # Using default Helvetica
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)  # Smaller default font
    
    def header(self):
        """Header template - override in child classes"""
        pass
    
    def footer(self):
        """Simple compact footer"""
        try:
            self.set_y(-12)  # Higher up
            self.set_font(PDFConstants.DEFAULT_FONT, "I", 7)  # Smaller
            self.set_text_color(*PDFConstants.SECONDARY_COLOR)
            
            page_num = self.page_no()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            # Page number on right
            self.cell(0, 5, f"Page {page_num}", 0, 0, 'R')
            
            # Timestamp on left
            self.set_x(10)
            self.cell(0, 5, timestamp, 0, 0, 'L')
        except:
            pass
    
    def add_title(self, text: str, size: int = 12):  # Smaller titles
        """Add centered title - COMPACT"""
        self.set_font(PDFConstants.BOLD_FONT, "B", size)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        self.cell(0, 6, text, 0, 1, 'C')  # Smaller height
        self.ln(3)  # Smaller spacing
    
    def add_subtitle(self, text: str, size: int = 10):  # Smaller subtitles
        """Add subtitle - COMPACT"""
        self.set_font(PDFConstants.BOLD_FONT, "B", size)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        self.cell(0, 5, text, 0, 1, 'L')  # Smaller height
        self.ln(2)  # Smaller spacing
    
    def add_paragraph(self, text: str, align: str = 'L'):
        """Add paragraph - COMPACT"""
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        self.multi_cell(0, 4, text, align=align)  # Smaller line height
        self.ln(3)  # Smaller spacing
    
    def add_separator(self):
        """Add horizontal line separator - COMPACT"""
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)  # Smaller spacing
    
    def reset_styles(self):
        """Reset to default styles"""
        self.set_font(PDFConstants.DEFAULT_FONT, "", 9)
        self.set_text_color(0, 0, 0)
    
    def add_page_break(self):
        """Add page break and preserve header"""
        self.add_page()