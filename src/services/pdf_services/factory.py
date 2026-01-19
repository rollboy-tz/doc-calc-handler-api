"""
Factory for creating PDF generators - ROOT LEVEL
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PDFGeneratorFactory:
    """Factory to create PDF generator instances"""
    
    # Available generator types mapping
    GENERATOR_TYPES = {
        # Short aliases (most commonly used)
        'acsee': 'ACSEEReportGenerator',
        'csee': 'CSEEReportGenerator', 
        'plse': 'PLSEReportGenerator',
        'generic': 'GenericReportGenerator',
        'student_report': 'StudentReportGenerator',
        
        # Full names
        'acsee_student_report': 'ACSEEReportGenerator',
        'csee_student_report': 'CSEEReportGenerator',
        'plse_student_report': 'PLSEReportGenerator',
        'generic_report': 'GenericReportGenerator',
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
        """
        try:
            config = config or {}
            generator_type = generator_type.lower().strip()
            
            # Import dynamically to avoid circular imports
            from .student_reports.generator import (
                StudentReportGenerator,
                ACSEEReportGenerator,
                CSEEReportGenerator,
                PLSEReportGenerator,
                GenericReportGenerator
            )
            
            # Map type to actual class
            type_to_class = {
                'student_report': StudentReportGenerator,
                'acsee': ACSEEReportGenerator,
                'csee': CSEEReportGenerator,
                'plse': PLSEReportGenerator,
                'generic': GenericReportGenerator,
                'acsee_student_report': ACSEEReportGenerator,
                'csee_student_report': CSEEReportGenerator,
                'plse_student_report': PLSEReportGenerator,
                'generic_report': GenericReportGenerator,
            }
            
            if generator_type not in type_to_class:
                available = ', '.join(sorted(type_to_class.keys()))
                raise ValueError(
                    f"Unknown generator type: '{generator_type}'. "
                    f"Available: {available}"
                )
            
            generator_class = type_to_class[generator_type]
            
            # Create instance
            logger.info(f"Creating {generator_class.__name__} instance")
            return generator_class(config)
            
        except ImportError as e:
            logger.error(f"Import error: {e}")
            raise ValueError(f"Cannot import generator modules: {e}")
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
        elif 'summary' in student_data and 'system' in student_data['summary']:
            system_rule = student_data['summary']['system'].lower()
        
        # Default to PLSE if class is primary
        if 'student' in student_data:
            student_class = student_data['student'].get('class', '').lower()
            if any(primary_class in student_class for primary_class in ['std', 'primary', 'grade', 'darasa']):
                system_rule = 'plse'
        
        # Create generator
        return PDFGeneratorFactory.create(system_rule, config)
    
    @staticmethod
    def list_generators() -> Dict[str, str]:
        """List all available generator types"""
        return {
            'acsee': 'Advanced Certificate of Secondary Education (Form 6)',
            'csee': 'Certificate of Secondary Education (Form 4)',
            'plse': 'Primary School Leaving Examination (Std 7)',
            'generic': 'Generic academic report',
            'student_report': 'Auto-detect system from data'
        }
    
    @staticmethod
    def get_default_config(system_rule: str) -> Dict[str, Any]:
        """Get default configuration for a system"""
        configs = {
            'acsee': {
                'system_name': 'Advanced Certificate of Secondary Education',
                'confidential': True,
                'show_points': True
            },
            'csee': {
                'system_name': 'Certificate of Secondary Education',
                'confidential': True,
                'show_points': True
            },
            'plse': {
                'system_name': 'Primary School Leaving Examination',
                'confidential': False,
                'show_points': False
            },
            'generic': {
                'system_name': 'Academic Performance Report',
                'confidential': False
            }
        }
        return configs.get(system_rule.lower(), {})


# Convenience functions for common use cases
def create_student_report_generator(system_rule: str = None, **kwargs):
    """
    Create a student report generator
    
    Args:
        system_rule: acsee, csee, plse, or generic
        **kwargs: Additional configuration
    
    Returns:
        PDF generator instance
    """
    config = kwargs.get('config', {})
    
    if system_rule:
        return PDFGeneratorFactory.create(system_rule, config)
    else:
        # Auto-detect based on config or return generic
        return PDFGeneratorFactory.create('generic', config)

def create_plse_report_generator(**kwargs):
    """Create PLSE report generator"""
    return PDFGeneratorFactory.create('plse', kwargs.get('config', {}))

def create_acsee_report_generator(**kwargs):
    """Create ACSEE report generator"""
    return PDFGeneratorFactory.create('acsee', kwargs.get('config', {}))

def create_csee_report_generator(**kwargs):
    """Create CSEE report generator"""
    return PDFGeneratorFactory.create('csee', kwargs.get('config', {}))


# Test the factory
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    print("PDF Generator Factory Test")
    print("=" * 50)
    
    try:
        # Test creating a PLSE generator
        plse_gen = create_plse_report_generator()
        print(f"✓ Created PLSE generator: {type(plse_gen).__name__}")
        
        # Test listing generators
        print("\nAvailable Generators:")
        print("-" * 30)
        for name, desc in PDFGeneratorFactory.list_generators().items():
            print(f"  {name:15} - {desc}")
        
        # Test default config
        print("\nDefault Config for PLSE:")
        print("-" * 30)
        plse_config = PDFGeneratorFactory.get_default_config('plse')
        for key, value in plse_config.items():
            print(f"  {key:15}: {value}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()