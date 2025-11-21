"""
Game Content Generator - Detached from GenerationEngine

This is a self-contained copy of the ContentGenerator for this game instance.
It allows the game to generate content independently without requiring the
GenerationEngine module.
"""

from .content_generator import ContentGenerator

__all__ = ['ContentGenerator']
