"""
Electrochemical Analyzers Module

This module contains all analyzer classes for processing electrochemical data.
Each analyzer inherits from GenericAnalyzer and implements specific analysis
methods for different types of electrochemical measurements.

Templates:
- template_analyzer: Shows how to create custom analyzer classes
"""

from .base_analyzer import BaseAnalyzer

__all__ = [
    'BaseAnalyzer',
]