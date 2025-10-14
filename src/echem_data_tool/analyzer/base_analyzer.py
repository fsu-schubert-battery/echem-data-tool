from abc import ABC, abstractmethod
from typing import Any, Union, List
from ..data import BaseData


class BaseAnalyzer(ABC):
    """
    Abstract base class for all electrochemical data analyzers.
    
    This class defines the common interface for all specific
    analysis methods that can be applied to electrochemical data.
    """
    
    def __init__(self, input_data: Union[BaseData, List[BaseData]]):
        """
        Initialize the analyzer with input data.
        
        Args:
            input_data: Single BaseData object or list of BaseData objects
        """
        if isinstance(input_data, list):
            self.input_data = input_data
        else:
            self.input_data = [input_data]
        
        # Validate input data types
        if not self._validate_input_types():
            raise TypeError(f"Invalid input data type for {self.__class__.__name__}")
    
    @abstractmethod
    def process(self) -> Any:
        """
        Process the input data and return analysis results.
        
        Returns:
            Any: Analysis results (format depends on specific analyzer)
        """
        pass
    
    @abstractmethod
    def _validate_input_types(self) -> bool:
        """
        Validate that the input data types are compatible with this analyzer.
        
        Returns:
            bool: True if input types are valid, False otherwise
        """
        pass
    
    def _validate_data(self) -> bool:
        """
        Validate all input data objects.
        
        Returns:
            bool: True if all data is valid, False otherwise
        """
        return all(data.validate() for data in self.input_data)