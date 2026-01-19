"""
Factory for creating PDF generators with system-specific templates
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PDFGeneratorFactory:
    """Factory to create PDF generator instances for different systems"""
    
    GENERATORS = {
        # System-specific generators
        'acsee_student_report': {
            'module': 'student_reports.generator',
            'class': 'ACSEEReportGenerator'
        },
        'csee_student_report': {
            'module': 'student_reports.generator',
            'class': 'CSEEReportGenerator'
        },
        'plse_student_report': {
            'module': 'student_reports.generator',
            'class': 'PLSEReportGenerator'
        },
        # Generic fallback
        'student_report': {
            'module': 'student_reports.generator',
            'class': 'GenericReportGenerator'
        }
    }
    
    @staticmethod
    def create(generator_type: str, config: Dict[str, Any] = None):
        """
        Create a PDF generator instance based on system type
        
        Args:
            generator_type: Type of generator (acsee_student_report, csee_student_report, plse_student_report)
            config: Optional configuration dictionary
        
        Returns:
            PDF generator instance
        """
        try:
            # If generic type, determine specific type from config
            if generator_type == 'student_report' and config:
                system_rule = config.get('system_rule', '').lower()
                if system_rule in ['acsee', 'advanced']:
                    generator_type = 'acsee_student_report'
                elif system_rule in ['csee', 'certificate']:
                    generator_type = 'csee_student_report'
                elif system_rule in ['plse', 'primary']:
                    generator_type = 'plse_student_report'
            
            if generator_type not in PDFGeneratorFactory.GENERATORS:
                available = ', '.join(PDFGeneratorFactory.GENERATORS.keys())
                raise ValueError(
                    f"Unknown generator type: {generator_type}. "
                    f"Available: {available}"
                )
            
            generator_info = PDFGeneratorFactory.GENERATORS[generator_type]
            module_name = generator_info['module']
            class_name = generator_info['class']
            
            # Dynamic import
            module_path = f"services.pdf_services.{module_name}"
            module = __import__(module_path, fromlist=[class_name])
            generator_class = getattr(module, class_name)
            
            # Create instance
            return generator_class(config or {})
            
        except ImportError as e:
            logger.error(f"Import error for {generator_type}: {e}")
            raise ValueError(f"Cannot load generator: {generator_type}")
        except AttributeError as e:
            logger.error(f"Class not found: {e}")
            raise ValueError(f"Generator class not found: {generator_type}")
        except Exception as e:
            logger.error(f"Factory error: {e}")
            raise