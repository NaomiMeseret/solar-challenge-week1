"""
Solar Analysis Package
MoonLight Energy Solutions - Solar Challenge Week 1
"""

__version__ = "1.0.0"
__author__ = "MoonLight Energy Solutions Analytics Team"

from . import data_loader
from . import data_profiler
from . import data_cleaner
from . import eda_analyzer
from . import visualization

__all__ = [
    'data_loader',
    'data_profiler',
    'data_cleaner',
    'eda_analyzer',
    'visualization'
]
