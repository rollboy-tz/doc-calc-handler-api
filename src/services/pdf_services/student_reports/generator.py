"""
Factory for creating PDF generators
"""
import logging
from typing import Dict, Any, Optional

# Import generators
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
        # Full names
        'student_report': StudentReportGenerator,
        'acsee_student_report': ACSEEReportGenerator,
        'csee_student_report': CSEEReportGenerator,
        'plse_student_report': PLSEReportGenerator,
        'generic_report': GenericReportGenerator,
        
        # Short aliases
        'acsee': ACSEEReportGenerator,
        'csee': CSEEReportGenerator,
        'plse': PLSEReportGenerator,
        'generic': GenericReportGenerator,
        
        # Legacy names
        'acsee_report': ACSEEReportGenerator,
        'csee_report': CSEEReportGenerator,
        'plse_report': PLSEReportGenerator,
    }
    
    @staticmethod
    def create(generator_type: str, config: Optional[Dict[str, Any]] = None):
        """
        Create a PDF generator instance
        
        Args:
            generator_type: Type of generator
            config: Optional configuration dictionary
        
        Returns:
            PDF generator instance
        
        Raises:
            ValueError: If generator type is unknown
        """
        try:
            config = config or {}
            generator_type = generator_type.lower().strip()
            
            # Get generator class
            if generator_type not in PDFGeneratorFactory.GENERATOR_TYPES:
                available = ', '.join(sorted(PDFGeneratorFactory.GENERATOR_TYPES.keys()))
                raise ValueError(
                    f"Unknown generator type: '{generator_type}'. "
                    f"Available: {available}"
                )
            
            generator_class = PDFGeneratorFactory.GENERATOR_TYPES[generator_type]
            
            # Create instance
            logger.info(f"Creating {generator_class.__name__} instance")
            return generator_class(config)
            
        except Exception as e:
            logger.error(f"Factory error: {e}")
            raise
    
    @staticmethod
    def create_from_data(student_data: Dict[str, Any], 
                         class_info: Optional[Dict[str, Any]] = None,
                         config: Optional[Dict[str, Any]] = None):
        """
        Create appropriate generator based on data
        
        Args:
            student_data: Student data
            class_info: Class information
            config: Additional configuration
        
        Returns:
            Configured PDF generator
        """
        # Determine system rule
        system_rule = 'generic'
        
        if class_info and 'rule' in class_info:
            system_rule = class_info['rule'].lower()
        elif 'system_rule' in student_data:
            system_rule = student_data['system_rule'].lower()
        
        # Create generator
        return PDFGeneratorFactory.create(system_rule, config)
    
    @staticmethod
    def list_generators() -> Dict[str, str]:
        """List all available generator types"""
        return {
            'student_report': 'Generic student report (auto-detects)',
            'acsee': 'Advanced Certificate of Secondary Education',
            'csee': 'Certificate of Secondary Education',
            'plse': 'Primary School Leaving Examination',
            'generic': 'Generic academic report'
        }


# Convenience functions
def create_generator(generator_type: str, **kwargs):
    """Convenience function to create generator"""
    return PDFGeneratorFactory.create(generator_type, kwargs.get('config'))

def create_plse_generator(**kwargs):
    """Create PLSE generator"""
    return PDFGeneratorFactory.create('plse', kwargs.get('config'))

def create_acsee_generator(**kwargs):
    """Create ACSEE generator"""
    return PDFGeneratorFactory.create('acsee', kwargs.get('config'))

def create_csee_generator(**kwargs):
    """Create CSEE generator"""
    return PDFGeneratorFactory.create('csee', kwargs.get('config'))


# Example usage
if __name__ == "__main__":
    print("PDF Generator Factory")
    print("=" * 50)
    
    # List available generators
    generators = PDFGeneratorFactory.list_generators()
    for name, desc in generators.items():
        print(f"  {name:20} - {desc}")
    
    print("\n" + "=" * 50)
    
    # Test creating a generator
    try:
        plse_gen = create_plse_generator()
        print(f"\n✓ Created PLSE generator: {type(plse_gen).__name__}")
    except Exception as e:
        print(f"\n✗ Error: {e}")