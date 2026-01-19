"""
Base PDF template using fpdf2
"""
from fpdf import FPDF
from datetime import datetime
from .constants import PDFConstants

class BasePDFTemplate(FPDF):
    """Base class for all PDF generators"""
    
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
        self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
    
    def header(self):
        """Header template - can be overridden by subclasses"""
        # Default empty header
        pass
    
    def footer(self):
        """Simple footer with page number"""
        try:
            self.set_y(-15)
            self.set_font(PDFConstants.DEFAULT_FONT, "I", 8)
            self.set_text_color(*PDFConstants.SECONDARY_COLOR)
            
            page_num = self.page_no()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            # Center-aligned footer
            self.cell(0, 8, f"Page {page_num} | {timestamp}", 0, 0, 'C')
        except:
            # Silently fail if footer generation fails
            pass
    
    def add_title(self, text: str, size: int = 14, align: str = 'C'):
        """Add title with styling"""
        self.set_font(PDFConstants.BOLD_FONT, "B", size)
        self.set_text_color(*PDFConstants.PRIMARY_COLOR)
        self.cell(0, 8, text, 0, 1, align)
        self.ln(5)
    
    def add_subtitle(self, text: str, size: int = 12, align: str = 'L'):
        """Add subtitle with styling"""
        self.set_font(PDFConstants.BOLD_FONT, "B", size)
        self.set_text_color(*PDFConstants.SECONDARY_COLOR)
        self.cell(0, 7, text, 0, 1, align)
        self.ln(3)
    
    def add_paragraph(self, text: str, align: str = 'L', line_height: int = 5):
        """Add paragraph text"""
        self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
        self.multi_cell(0, line_height, text, align=align)
        self.ln(5)
    
    def add_separator(self, color: tuple = None):
        """Add horizontal line separator"""
        if color is None:
            color = PDFConstants.BORDER_COLOR
        
        y = self.get_y()
        self.set_draw_color(*color)
        self.line(15, y, 195, y)
        self.set_draw_color(0, 0, 0)  # Reset to black
        self.ln(5)
    
    def reset_styles(self):
        """Reset to default styles"""
        self.set_font(PDFConstants.DEFAULT_FONT, "", 10)
        self.set_text_color(0, 0, 0)
    
    def add_page_break(self):
        """Add page break"""
        self.add_page()
    
    def draw_table_header(self, headers: list, col_widths: list, fill_color: tuple = None):
        """Draw table header row"""
        if fill_color is None:
            fill_color = PDFConstants.PRIMARY_COLOR
        
        self.set_fill_color(*fill_color)
        self.set_text_color(255, 255, 255)
        self.set_font(PDFConstants.BOLD_FONT, "B", 9)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, 'C', 1)
        self.ln()
        
        # Reset colors
        self.set_text_color(0, 0, 0)
        self.set_fill_color(255, 255, 255)