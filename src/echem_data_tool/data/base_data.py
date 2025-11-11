from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional
from pathlib import Path
import pandas as pd
import numpy as np


@dataclass
class BaseData(ABC):
    """
    Abstract base class for all electrochemical data types.
    
    This class defines the common interface and basic structure
    for all specific measurement technique data classes.
    for all specific measurement technique data classes. Methods
    marked as "abstractmethod" must be implemented by any subclass.
    Subclasses may also include additional attributes and methods
    specific to the measurement technique.
    """
    
    file_path: Optional[str] = None
    
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate the integrity and consistency of the data.
        
        Returns:
            bool: True if data is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the data to a pandas DataFrame.
        
        Returns:
            pd.DataFrame: Data as DataFrame
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the data to a dictionary.
        
        Returns:
            Dict[str, Any]: Data as dictionary
        """
        pass
    
    def __post_init__(self):
        """Post-initialization validation."""
    @abstractmethod
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the data to a pandas DataFrame.
        
        Returns:
            pd.DataFrame: Data as DataFrame
        """
        pass
    
    def __post_init__(self):
        """
        Post-initialization validation.
        
        This is automatically called after the dataclass is initialized.
        It ensures that the data is valid upon creation.
        """
        if not self.validate():
            raise ValueError("Data validation failed during initialization")