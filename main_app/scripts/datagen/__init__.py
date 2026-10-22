"""
Vigil: Synthetic login data generator
File location: main_app/datagen/__init__.py
"""

from .generator import generate
from .writer import write_outputs

__all__ = ["generate", "write_outputs"]
