"""
R-Gen Simulation Engine

A living world simulation system built on top of R-Gen Generation Engine.
"""

from .src.core.world import World
from .src.simulation.simulator import WorldSimulator

__version__ = "0.1.0"
__all__ = ["World", "WorldSimulator"]
