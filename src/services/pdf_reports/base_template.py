"""
base_template.py - FIXED METADATA
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BasePDFTemplate:
    """Base template with system branding"""
    
    def __init__(self, system_config=None):
        self.system_config = system_config or self._default_config()
        self.styles = self._get_styles()
    
    def _default_config(self):
        """System metadata"""
        return {
            "system_name": "EDU-MANAGER PRO",
            "version": "2.0",
            "copyright": f"© {datetime.now().year} EduManager Pro",
            "author": "EDU-MANAGER REPORT SYSTEM",
            "company": "EduManager Solutions Ltd",
        }
    
    def _get_styles(self):
        """Get styles without setup method"""
        from reportlab.lib.styles import getSampleStyleSheet
        return getSampleStyleSheet()
    
    def create_document(self, filepath, title, subject=None, author=None):
        """Create PDF document - FIXED VERSION"""
        # SimpleDocTemplate doesn't accept 'keywords' directly
        # We need to use canvas methods to set metadata
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            title=title,
            author=author or self.system_config['author'],
        )
        
        # Store metadata for later use
        doc._custom_metadata = {
            'subject': subject or "Student Academic Report",
            'creator': self.system_config['system_name'],
            'producer': f"{self.system_config['system_name']} v{self.system_config['version']}",
        }
        
        return doc
    
    def _add_metadata_to_canvas(self, canvas, doc):
        """Add metadata to PDF canvas"""
        try:
            # Set additional metadata
            if hasattr(doc, '_custom_metadata'):
                metadata = doc._custom_metadata
                canvas.setSubject(metadata.get('subject', ''))
                canvas.setCreator(metadata.get('creator', ''))
                canvas.setProducer(metadata.get('producer', ''))
                canvas.setKeywords("report, academic, school, results")
        except:
            pass  # Skip if metadata fails
    
    def add_footer(self, canvas, doc):
        """Add system footer"""
        try:
            # Add metadata first
            self._add_metadata_to_canvas(canvas, doc)
            
            # Add footer text
            canvas.saveState()
            canvas.setFont('Helvetica', 7)
            canvas.setFillColor(colors.grey)
            
            footer_text = f"{self.system_config['system_name']} | Page {canvas.getPageNumber()}"
            canvas.drawCentredString(doc.width/2, 15, footer_text)
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            canvas.drawString(40, 15, timestamp)
            
            canvas.restoreState()
        except Exception as e:
            logger.warning(f"Footer error: {e}")