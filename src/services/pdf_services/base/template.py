"""
Base PDF template using fpdf2 - PROPER SPACING
"""
from fpdf import FPDF
from datetime import datetime
from .constants import PDFConstants

class BasePDFTemplate(FPDF):
    """Base class for all PDF generators - PROPER SPACING"""
    
    def __init__(self, config: dict = None):
        super().__init__()
        self.config = {**PDFConstants.SYSTEM_CONFIG, **(config or {})}
        self.constants = PDFConstants
        
        # Setup with proper spacing
        self.set_margins(15, 15, 15)  # Standard margins
        self.set_auto_page_break(auto=True, margin=15)
        self.set_display_mode(zoom="default")
        
        # Add first page
        self.add_page()
        self._setup_fonts()
    
    def _setup_fonts(self):
        """Setup fonts"""
        self.set_font(PDFConstants.DEFAULT_FONT, "", 10)  # Normal font size
    
    def header(self):
        """Header template"""
        pass
    
    def footer(self):
        """Simple footer"""
        try:
            self.set_y(-15)
            self.set_font(PDFConstants.DEFAULT_FONT, "I", 8)
            self.set_text_color(*PDFConstants.SECONDARY_COLOR)
            
            page_num = self.page_no()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            self.cell(0, 8, f"Page {page_num} | {timestamp}", 0, 0, 'C')
        except:
            pass
    
    def add_title(self, text: str, size: int = 14):
        """Add centered title"""
        self.set_font(PDFConstants.BOLD_FONT, "B", size)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        self.cell(0, 8, text, 0, 1, 'C')
        self.ln(5)
    
    def add_subtitle(self, text: str, size: int = 12):
        """Add subtitle"""
        self.set_font(PDFConstants.BOLD_FONT, "B", size)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        self.cell(0, 7, text, 0, 1, 'L')
        self.ln(3)
    
    def add_paragraph(self, text: str, align: str = 'L'):
        """Add paragraph"""
        self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
        self.multi_cell(0, 5, text, align=align)
        self.ln(5)
    
    def add_separator(self):
        """Add horizontal line separator"""
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(5)
    
    def reset_styles(self):
        """Reset to default styles"""
        self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
        self.set_text_color(0, 0, 0)
    
    def add_page_break(self):
        """Add page break"""
        self.add_page()