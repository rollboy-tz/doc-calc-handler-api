"""
Class Result Sheet
"""
from .base_template import BasePDFTemplate
from reportlab.platypus import Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4, landscape
import tempfile
import os

class ClassSheet(BasePDFTemplate):
    """Generate class result sheet"""
    
    def generate(self, class_data, school_info=None):
        try:
            filename = self._create_filename(class_data, school_info)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # Landscape for class sheet
            doc = SimpleDocTemplate(
                filepath,
                pagesize=landscape(A4),
                title=f"Class Sheet - {class_data['metadata']['class_id']}",
                author=self.system_config['author']
            )
            
            story = []
            
            # Header
            story.append(Paragraph(
                f"CLASS RESULTS SHEET - {class_data['metadata']['class_id']}",
                self.styles['Heading1']
            ))
            
            # Class summary
            story.append(self._create_class_summary(class_data))
            story.append(Spacer(1, 10))
            
            # Students table
            story.append(self._create_students_table(class_data))
            
            doc.build(story, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Class sheet error: {e}")
            return self._create_error_pdf(str(e))
    
    def _create_filename(self, class_data, school_info):
        class_id = class_data['metadata']['class_id']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        school_code = school_info.get('code', 'SCH') if school_info else 'SCH'
        
        return f"{school_code}_CLASS_{class_id}_{timestamp}.pdf"