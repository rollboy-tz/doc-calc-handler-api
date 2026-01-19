"""
services/pdf_services/factory.py
"""
import logging

logger = logging.getLogger(__name__)

class PDFGeneratorFactory:
    """Factory to create PDF generators"""
    
    @staticmethod
    def create_generator(report_type, config=None):  # <-- ADD config parameter
        """
        Create PDF generator based on type
        
        Args:
            report_type: 'student_report', 'class_results', 'transcript'
            config: Optional configuration dictionary
        
        Returns:
            PDF generator instance
        """
        try:
            if report_type == 'student_report':
                from .student_reports.generator import StudentReportGenerator
                return StudentReportGenerator(config)  # <-- PASS config
            
            elif report_type == 'class_results':
                from .class_results.generator import ClassResultsGenerator
                return ClassResultsGenerator(config)  # <-- PASS config
            
            elif report_type == 'transcript':
                from .transcripts.generator import TranscriptGenerator
                return TranscriptGenerator(config)  # <-- PASS config
            
            else:
                raise ValueError(f"Unknown report type: {report_type}")
                
        except ImportError as e:
            logger.error(f"Import error: {e}")
            raise
        except Exception as e:
            logger.error(f"Factory error: {e}")
            raise