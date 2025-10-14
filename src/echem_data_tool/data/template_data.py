"""
Template for creating custom electrochemical data classes.

This template shows how to create your own data class by inheriting from BaseData.
Replace 'YourTechnique' with your specific measurement technique name.
"""

from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd
import numpy as np
from . import BaseData


@dataclass
class YourTechniqueData(BaseData):
    """
    Template data class for [Your Technique Name] measurements.
    
    This class holds the raw data structure for [your specific technique].
    Replace this docstring and the class name with your specific technique.
    
    Example techniques:
    - OpenCircuitVoltageData
    - CyclicVoltammetryData  
    - ChronoamperometryData
    - CyclingData
    - ElectrochemicalImpedanceSpectroscopyData
    """
    
    # Define your data fields here
    # Use numpy arrays for numerical data
    time: np.ndarray = None
    potential: np.ndarray = None  # V vs. reference
    current: np.ndarray = None    # A
    
    # Add additional fields specific to your technique
    # Examples:
    # temperature: np.ndarray = None  # K
    # frequency: np.ndarray = None    # Hz (for EIS)
    # cycle_number: np.ndarray = None # dimensionless (for cycling)
    
    def validate(self) -> bool:
        """
        Validate the data integrity and consistency.
        
        Implement your specific validation logic here.
        Check for:
        - Data array lengths match
        - Required fields are not None
        - Physical plausibility of values
        - Units and ranges
        
        Returns:
            bool: True if data is valid, False otherwise
        """
        try:
            # Example validations - customize for your data
            if self.time is None or self.potential is None or self.current is None:
                return False
                
            # Check that all arrays have the same length
            if not (len(self.time) == len(self.potential) == len(self.current)):
                return False
                
            # Check for NaN or infinite values
            for array in [self.time, self.potential, self.current]:
                if np.any(np.isnan(array)) or np.any(np.isinf(array)):
                    return False
            
            # Add your specific validation checks here
            # Examples:
            # - Time should be monotonically increasing
            # - Potential should be within reasonable range
            # - Current values should be reasonable
            
            return True
            
        except Exception:
            return False
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the data to a pandas DataFrame.
        
        Customize the column names and structure for your data.
        
        Returns:
            pd.DataFrame: Data as DataFrame with appropriate column names
        """
        data_dict = {
            'time_s': self.time,
            'potential_V': self.potential,
            'current_A': self.current,
        }
        
        # Add your additional fields here
        # Example:
        # if self.temperature is not None:
        #     data_dict['temperature_K'] = self.temperature
        
        return pd.DataFrame(data_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the data to a dictionary.
        
        Useful for serialization, saving to JSON, etc.
        
        Returns:
            Dict[str, Any]: Data as dictionary
        """
        result = {
            'time': self.time.tolist() if self.time is not None else None,
            'potential': self.potential.tolist() if self.potential is not None else None,
            'current': self.current.tolist() if self.current is not None else None,
            'file_path': self.file_path,
        }
        
        # Add your additional fields here
        # Example:
        # if self.temperature is not None:
        #     result['temperature'] = self.temperature.tolist()
        
        return result
    
    # Add custom methods specific to your technique
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Example custom method: Get a summary of the measurement data.
        
        Returns:
            Dict[str, Any]: Summary statistics
        """
        if not self.validate():
            return {"error": "Invalid data"}
        
        return {
            'duration_s': self.time[-1] - self.time[0] if len(self.time) > 1 else 0,
            'potential_range_V': [np.min(self.potential), np.max(self.potential)],
            'current_range_A': [np.min(self.current), np.max(self.current)],
            'data_points': len(self.time),
        }


# Example of a more specific implementation
@dataclass  
class CyclicVoltammetryData(BaseData):
    """
    Data class for Cyclic Voltammetry measurements.
    
    Contains the essential data for CV experiments including
    time, potential, and current traces.
    """
    
    time: np.ndarray = None         # s
    potential: np.ndarray = None    # V vs. reference
    current: np.ndarray = None      # A
    cycle_number: np.ndarray = None # dimensionless
    
    def validate(self) -> bool:
        """Validate CV-specific data."""
        try:
            if any(x is None for x in [self.time, self.potential, self.current]):
                return False
                
            if not (len(self.time) == len(self.potential) == len(self.current)):
                return False
                
            # CV-specific validations
            if self.scan_rate is not None and self.scan_rate <= 0:
                return False
                
            return True
        except Exception:
            return False
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert CV data to DataFrame."""
        data = {
            'time_s': self.time,
            'potential_V': self.potential, 
            'current_A': self.current,
        }
        
        if self.cycle_number is not None:
            data['cycle'] = self.cycle_number
            
        return pd.DataFrame(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert CV data to dictionary."""
        return {
            'time': self.time.tolist() if self.time is not None else None,
            'potential': self.potential.tolist() if self.potential is not None else None,
            'current': self.current.tolist() if self.current is not None else None,
            'cycle_number': self.cycle_number.tolist() if self.cycle_number is not None else None,
            'file_path': self.file_path,
        }
    
    def get_peak_currents(self) -> Dict[str, float]:
        """CV-specific method to find peak currents."""
        if not self.validate():
            return {}
            
        return {
            'anodic_peak_current': np.max(self.current),
            'cathodic_peak_current': np.min(self.current),
        }