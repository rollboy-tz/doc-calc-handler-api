"""
Factory for creating PDF generators
"""
import logging

logger = logging.getLogger(__name__)

class PDFGeneratorFactory:
    """Factory to create PDF generator instances"""
    
    @staticmethod
    def create(generator_type: str, config: dict = None):
        """
        Create a PDF generator instance
        
        Args:
            generator_type: Type of generator
                - 'student_report': Generic (auto-detects system)
                - 'acsee_student_report': ACSEE specific
                - 'csee_student_report': CSEE specific  
                - 'plse_student_report': PLSE specific
            config: Optional configuration dictionary
        
        Returns:
            PDF generator instance
        """
        try:
            config = config or {}
            
            # Map generator types to classes
            generator_map = {
                'student_report': 'StudentReportGenerator',
                'acsee_student_report': 'ACSEEReportGenerator',
                'csee_student_report': 'CSEEReportGenerator',
                'plse_student_report': 'PLSEReportGenerator',
                'generic_report': 'GenericReportGenerator'
            }
            
            if generator_type not in generator_map:
                available = ', '.join(generator_map.keys())
                raise ValueError(
                    f"Unknown generator type: {generator_type}. "
                    f"Available: {available}"
                )
            
            class_name = generator_map[generator_type]
            
            # Import module and get class
            from .student_reports.generator import (
                StudentReportGenerator,
                ACSEEReportGenerator,
                CSEEReportGenerator,
                PLSEReportGenerator,
                GenericReportGenerator
            )
            
            # Map class names to actual classes
            class_map = {
                'StudentReportGenerator': StudentReportGenerator,
                'ACSEEReportGenerator': ACSEEReportGenerator,
                'CSEEReportGenerator': CSEEReportGenerator,
                'PLSEReportGenerator': PLSEReportGenerator,
                'GenericReportGenerator': GenericReportGenerator
            }
            
            generator_class = class_map[class_name]
            
            # Create instance
            return generator_class(config)
            
        except ImportError as e:
            logger.error(f"Import error for {generator_type}: {e}")
            raise ValueError(f"Cannot load generator: {generator_type}")
        except KeyError as e:
            logger.error(f"Class not found: {e}")
            raise ValueError(f"Generator class not found: {generator_type}")
        except Exception as e:
            logger.error(f"Factory error: {e}")
            raise