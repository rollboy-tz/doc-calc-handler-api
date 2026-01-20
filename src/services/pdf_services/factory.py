"""
Factory for creating PDF generators - ROOT LEVEL
FIXED IMPORT ISSUE
"""
import os
import sys
import logging
from typing import Dict, Any, Optional

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

logger = logging.getLogger(__name__)

class PDFGeneratorFactory:
    """Factory to create PDF generator instances"""
    
    @staticmethod
    def create(generator_type: str, config: Optional[Dict[str, Any]] = None):
        """
        Create a PDF generator instance
        
        Args:
            generator_type: Type of generator (acsee, csee, plse, generic, student_report)
            config: Optional configuration dictionary
        
        Returns:
            PDF generator instance
        """
        try:
            config = config or {}
            generator_type = generator_type.lower().strip()
            
            # DEBUG: Print import paths
            logger.debug(f"Creating generator: {generator_type}")
            
            # DYNAMIC IMPORT - Fix for circular imports
            try:
                # Try relative import first
                from .student_reports.generator import (
                    StudentReportGenerator,
                    ACSEEReportGenerator,
                    CSEEReportGenerator,
                    PLSEReportGenerator,
                    GenericReportGenerator
                )
            except ImportError as e1:
                logger.warning(f"Relative import failed: {e1}")
                try:
                    # Try absolute import
                    from src.services.pdf_services.student_reports.generator import (
                        StudentReportGenerator,
                        ACSEEReportGenerator,
                        CSEEReportGenerator,
                        PLSEReportGenerator,
                        GenericReportGenerator
                    )
                except ImportError as e2:
                    logger.error(f"Absolute import failed: {e2}")
                    # Try direct file import
                    import_path = os.path.join(current_dir, "student_reports", "generator.py")
                    if os.path.exists(import_path):
                        import importlib.util
                        spec = importlib.util.spec_from_file_location("generator", import_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        StudentReportGenerator = module.StudentReportGenerator
                        ACSEEReportGenerator = module.ACSEEReportGenerator
                        CSEEReportGenerator = module.CSEEReportGenerator
                        PLSEReportGenerator = module.PLSEReportGenerator
                        GenericReportGenerator = module.GenericReportGenerator
                    else:
                        raise ImportError(f"Cannot find generator module at {import_path}")
            
            # Map generator types to classes
            generator_map = {
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
            
            if generator_type not in generator_map:
                available = ', '.join(sorted(generator_map.keys()))
                raise ValueError(
                    f"Unknown generator type: '{generator_type}'. "
                    f"Available: {available}"
                )
            
            generator_class = generator_map[generator_type]
            
            # Create instance
            logger.info(f"Created {generator_class.__name__} instance")
            return generator_class(config)
            
        except Exception as e:
            logger.error(f"Factory error creating '{generator_type}': {e}")
            # Provide helpful error message
            error_msg = str(e)
            if "No module named" in error_msg:
                error_msg += f"\nCurrent dir: {current_dir}"
                error_msg += f"\nLooking for: student_reports/generator.py"
                error_msg += f"\nFiles in student_reports/: {os.listdir(os.path.join(current_dir, 'student_reports')) if os.path.exists(os.path.join(current_dir, 'student_reports')) else 'Directory not found'}"
            
            raise RuntimeError(f"Failed to create PDF generator: {error_msg}")
    
    @staticmethod
    def create_auto_detected(student_data: Dict[str, Any], 
                            class_info: Optional[Dict[str, Any]] = None,
                            config: Optional[Dict[str, Any]] = None):
        """
        Auto-detect and create appropriate generator
        
        Args:
            student_data: Student data
            class_info: Class information
            config: Additional configuration
        
        Returns:
            PDF generator instance
        """
        # Determine system rule
        system_rule = 'generic'
        
        if class_info and 'rule' in class_info:
            system_rule = class_info['rule'].lower()
        elif 'system_rule' in student_data:
            system_rule = student_data['system_rule'].lower()
        
        # Auto-detect from class name
        if 'student' in student_data:
            student_class = student_data['student'].get('class', '').lower()
            if any(term in student_class for term in ['std', 'primary', 'darasa', 'grade 1-7']):
                system_rule = 'plse'
            elif any(term in student_class for term in ['form 5', 'form 6', 'advanced']):
                system_rule = 'acsee'
            elif any(term in student_class for term in ['form 1-4', 'ordinary']):
                system_rule = 'csee'
        
        logger.info(f"Auto-detected system: {system_rule}")
        return PDFGeneratorFactory.create(system_rule, config)
    
    @staticmethod
    def get_available_types() -> Dict[str, str]:
        """Get available generator types with descriptions"""
        return {
            'acsee': 'Advanced Level (Form 5-6)',
            'csee': 'Ordinary Level (Form 1-4)',
            'plse': 'Primary School (Std 1-7)',
            'generic': 'Generic academic report',
            'student_report': 'Auto-detect from data'
        }
    
    @staticmethod
    def test_imports():
        """Test if all imports are working"""
        try:
            from .student_reports.generator import (
                StudentReportGenerator,
                ACSEEReportGenerator,
                CSEEReportGenerator,
                PLSEReportGenerator,
                GenericReportGenerator
            )
            return True, "All imports successful"
        except ImportError as e:
            return False, f"Import error: {e}"


# SIMPLER CONVENIENCE FUNCTIONS

def get_pdf_generator(generator_type: str = 'plse', **kwargs):
    """Get PDF generator - simple wrapper"""
    return PDFGeneratorFactory.create(generator_type, kwargs.get('config'))

def get_plse_generator(**kwargs):
    """Get PLSE generator"""
    return PDFGeneratorFactory.create('plse', kwargs.get('config'))

def get_acsee_generator(**kwargs):
    """Get ACSEE generator"""
    return PDFGeneratorFactory.create('acsee', kwargs.get('config'))

def get_csee_generator(**kwargs):
    """Get CSEE generator"""
    return PDFGeneratorFactory.create('csee', kwargs.get('config'))

def get_generator_for_data(student_data: Dict, class_info: Dict = None, **kwargs):
    """Get generator auto-detected from data"""
    return PDFGeneratorFactory.create_auto_detected(
        student_data, 
        class_info, 
        kwargs.get('config')
    )


# Test function
def test_factory():
    """Test the factory"""
    print("Testing PDF Generator Factory")
    print("=" * 50)
    
    # Test imports
    success, message = PDFGeneratorFactory.test_imports()
    print(f"Import test: {'✓' if success else '✗'} {message}")
    
    if success:
        # List available types
        print("\nAvailable Generator Types:")
        print("-" * 30)
        for gen_type, desc in PDFGeneratorFactory.get_available_types().items():
            print(f"  {gen_type:20} - {desc}")
        
        # Try to create a generator
        try:
            generator = get_plse_generator()
            print(f"\n✓ Created PLSE generator: {type(generator).__name__}")
            
            # Test with sample data
            sample_data = {
                'student': {'name': 'Test Student', 'class': 'STD7 A'},
                'summary': {'total': 300, 'average': 75.5, 'grade': 'B'}
            }
            
            auto_generator = get_generator_for_data(sample_data)
            print(f"✓ Auto-detected generator: {type(auto_generator).__name__}")
            
        except Exception as e:
            print(f"\n✗ Error creating generator: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\nCannot proceed due to import errors")
    
    print("\n" + "=" * 50)


# Run test if executed directly
if __name__ == "__main__":
    test_factory()