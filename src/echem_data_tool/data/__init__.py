"""
Electrochemical Data Module

This module contains all data classes for different electrochemical measurement techniques.
Each data class inherits from GenericData and implements the specific data structure
for its corresponding measurement method.

Templates:
- template_data: Shows how to create custom data classes
"""

from .base_data import BaseData

__all__ = [
    'BaseData',
]