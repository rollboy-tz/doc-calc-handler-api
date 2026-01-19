"""
services/pdf_services/base/template.py
"""
from fpdf import FPDF
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PDFBaseTemplate(FPDF):
    """Base template for all PDFs using fpdf2"""
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.colors = self._get_colors()
        
        # Setup font
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        
        # Add fonts (using default Helvetica for simplicity)
        # For custom fonts, add them with: self.add_font()
        self.set_font("helvetica", "", 10)
    
    def _get_colors(self):
        """Basic colors - RGB tuples"""
        return {
            'primary': (41, 128, 185),     # #2980B9
            'dark': (44, 62, 80),          # #2C3E50
            'light': (248, 249, 250),      # #F8F9FA
            'border': (221, 221, 221)      # #DDDDDD
        }
    
    def header(self):
        """Header to be overridden by child classes"""
        pass
    
    def footer(self):
        """Simple footer"""
        try:
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.set_text_color(*self.colors['dark'])
            
            page_num = self.page_no()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            # Page number on right
            self.cell(0, 10, f"Page {page_num}", 0, 0, 'R')
            
            # Timestamp on left
            self.set_x(10)
            self.cell(0, 10, timestamp, 0, 0, 'L')
        except:
            pass