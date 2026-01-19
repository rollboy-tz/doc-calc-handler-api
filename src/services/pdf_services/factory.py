"""
Factory for creating PDF generators - ROOT LEVEL
"""
import logging
from typing import Dict, Any, Optional
from .student_reports.generator import (
    StudentReportGenerator,
    ACSEEReportGenerator,
    CSEEReportGenerator,
    PLSEReportGenerator,
    GenericReportGenerator
)

logger = logging.getLogger(__name__)

class PDFGeneratorFactory:
    """Factory to create PDF generator instances"""
    
    # Available generator types
    GENERATOR_TYPES = {
        'student_report': StudentReportGenerator,
        'acsee_student_report': ACSEEReportGenerator,
        'csee_student_report': CSEEReportGenerator,
        'plse_student_report': PLSEReportGenerator,
        'generic_report': GenericReportGenerator,
        'acsee': ACSEEReportGenerator,  # Aliases
        'csee': CSEEReportGenerator,
        'plse': PLSEReportGenerator,
        'generic': GenericReportGenerator
    }
    
    @staticmethod
    def create(generator_type: str, config: Optional[Dict[str, Any]] = None):
        """
        Create a PDF generator instance
        
        Args:
            generator_type: Type of generator
                - 'student_report', 'acsee', 'csee', 'plse', 'generic'
                - Or full names like 'acsee_student_report'
            config: Optional configuration dictionary
        
        Returns:
            PDF generator instance
        
        Raises:
            ValueError: If generator type is unknown
        """
        try:
            config = config or {}
            
            # Normalize generator type
            generator_type = generator_type.lower().strip()
            
            # Get generator class
            if generator_type not in PDFGeneratorFactory.GENERATOR_TYPES:
                available = ', '.join(sorted(PDFGeneratorFactory.GENERATOR_TYPES.keys()))
                raise ValueError(
                    f"Unknown generator type: '{generator_type}'. "
                    f"Available types: {available}"
                )
            
            generator_class = PDFGeneratorFactory.GENERATOR_TYPES[generator_type]
            
            # Create and return instance
            logger.debug(f"Creating {generator_class.__name__} instance")
            return generator_class(config)
            
        except Exception as e:
            logger.error(f"Factory error creating '{generator_type}': {e}")
            raise
    
    @staticmethod
    def create_from_system_rule(system_rule: str, config: Optional[Dict[str, Any]] = None):
        """
        Create generator based on system rule (simplified)
        
        Args:
            system_rule: System rule (acsee, csee, plse, generic)
            config: Optional configuration
        
        Returns:
            PDF generator instance
        """
        system_rule = system_rule.lower().strip()
        
        # Map to appropriate generator
        if system_rule == 'acsee':
            return PDFGeneratorFactory.create('acsee_student_report', config)
        elif system_rule == 'csee':
            return PDFGeneratorFactory.create('csee_student_report', config)
        elif system_rule == 'plse':
            return PDFGeneratorFactory.create('plse_student_report', config)
        else:
            return PDFGeneratorFactory.create('generic_report', config)
    
    @staticmethod
    def create_for_student_report(student_data: Dict[str, Any], 
                                  class_info: Optional[Dict[str, Any]] = None,
                                  config: Optional[Dict[str, Any]] = None):
        """
        Create appropriate generator based on student data
        
        Args:
            student_data: Student data dictionary
            class_info: Class information (optional)
            config: Additional configuration
        
        Returns:
            Configured PDF generator instance
        """
        # Determine system rule from data
        system_rule = 'generic'
        
        if class_info and 'rule' in class_info:
            system_rule = class_info['rule'].lower()
        elif 'system_rule' in student_data:
            system_rule = student_data['system_rule'].lower()
        
        # Create generator
        generator = PDFGeneratorFactory.create_from_system_rule(system_rule, config)
        
        return generator
    
    @staticmethod
    def list_available_generators() -> Dict[str, str]:
        """
        List all available generator types with descriptions
        
        Returns:
            Dictionary of generator types and descriptions
        """
        return {
            'student_report': 'Generic student report (auto-detects system)',
            'acsee_student_report': 'Advanced Certificate of Secondary Education',
            'csee_student_report': 'Certificate of Secondary Education',
            'plse_student_report': 'Primary School Leaving Examination',
            'generic_report': 'Generic academic report',
            'acsee': 'Alias for acsee_student_report',
            'csee': 'Alias for csee_student_report', 
            'plse': 'Alias for plse_student_report',
            'generic': 'Alias for generic_report'
        }


# Convenience function
def create_pdf_generator(generator_type: str, **kwargs):
    """
    Convenience function to create PDF generator
    
    Example:
        generator = create_pdf_generator('plse', config={'confidential': True})
    """
    return PDFGeneratorFactory.create(generator_type, kwargs.get('config'))


# Example usage
if __name__ == "__main__":
    # Test the factory
    print("Available PDF Generators:")
    print("=" * 40)
    
    for gen_type, description in PDFGeneratorFactory.list_available_generators().items():
        print(f"{gen_type:25} - {description}")
    
    print("\n" + "=" * 40)
    
    # Create a PLSE generator
    try:
        plse_generator = PDFGeneratorFactory.create('plse')
        print(f"\nCreated generator: {type(plse_generator).__name__}")
    except Exception as e:
        print(f"\nError creating generator: {e}")