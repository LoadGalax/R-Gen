"""
R-Gen Generation Engine

A powerful procedural content generation system for fantasy worlds.
"""

from .src.content_generator import ContentGenerator
from .src.database import DatabaseManager

__version__ = "1.0.0"
__all__ = ["ContentGenerator", "DatabaseManager"]
