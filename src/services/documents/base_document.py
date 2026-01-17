# services/documents/base_document.py
"""
BASE DOCUMENT CLASS
Mama ya documents zote
Common functions zote documents zinahitaji
"""
from abc import ABC, abstractmethod
from io import BytesIO
import pandas as pd
from datetime import datetime
import os

class BaseDocument(ABC):
    """Abstract base class for all documents"""
    
    def __init__(self, data, document_type=None, **kwargs):
        """
        Initialize document
        
        Args:
            data: Raw data for document
            document_type: Type of document (marksheet, report_card, etc.)
            **kwargs: Additional parameters
        """
        self.raw_data = data
        self.document_type = document_type or self.__class__.__name__.lower()
        self.params = kwargs
        self.processed_data = None
        self.generated_at = datetime.now()
        
        # Common metadata
        self.metadata = {
            'document_type': self.document_type,
            'created_at': self.generated_at.isoformat(),
            'parameters': kwargs,
            'version': '1.0.0'
        }
    
    def _prepare_data(self):
        """Convert data to DataFrame if needed"""
        if isinstance(self.raw_data, pd.DataFrame):
            return self.raw_data.copy()
        elif isinstance(self.raw_data, dict):
            return pd.DataFrame([self.raw_data])
        elif isinstance(self.raw_data, list):
            return pd.DataFrame(self.raw_data)
        else:
            raise ValueError(f"Unsupported data type: {type(self.raw_data)}")
    
    @abstractmethod
    def generate(self):
        """
        Generate document - MUST be implemented by child classes
        
        Returns:
            self (for method chaining)
        """
        pass
    
    def validate(self):
        """
        Validate document data
        Returns: (is_valid, errors)
        """
        errors = []
        
        if self.processed_data is None:
            errors.append("Document not generated yet")
        
        if self.processed_data is not None and self.processed_data.empty:
            errors.append("Document data is empty")
        
        return len(errors) == 0, errors
    
    def get_metadata(self):
        """Get document metadata"""
        return {
            **self.metadata,
            'rows': len(self.processed_data) if self.processed_data is not None else 0,
            'columns': list(self.processed_data.columns) if self.processed_data is not None else [],
            'validation': self.validate()
        }
    
    def save_to_file(self, filepath):
        """
        Save document to file (for testing/debugging)
        
        Args:
            filepath: Path to save file
            
        Returns:
            filepath if successful
        """
        if self.processed_data is None:
            raise ValueError("Document not generated. Call generate() first.")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save based on file extension
        if filepath.endswith('.xlsx'):
            self.processed_data.to_excel(filepath, index=False)
        elif filepath.endswith('.csv'):
            self.processed_data.to_csv(filepath, index=False)
        elif filepath.endswith('.json'):
            self.processed_data.to_json(filepath, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported file format: {filepath}")
        
        return filepath
    
    def __str__(self):
        """String representation"""
        return f"{self.document_type.upper()} Document (Generated: {self.generated_at})"
    
    def __repr__(self):
        """Representation"""
        return f"<{self.__class__.__name__}: {self.document_type}>"