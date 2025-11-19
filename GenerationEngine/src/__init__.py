"""
R-Gen Generation Engine

Procedural content generation for fantasy worlds.
"""

from .content_generator import ContentGenerator
from .database import DatabaseManager

__version__ = "1.0.0"
__all__ = ["ContentGenerator", "DatabaseManager"]
