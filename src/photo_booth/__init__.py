"""
Photo Booth Module for Arcade Mode.

Provides selfie capture, 8-bit filtering, and composite generation
for shareable photo booth images at AWS re:Invent 2025.
"""

from .config import PhotoBoothConfig

# Import optional modules (may not exist yet during development)
__all__ = ["PhotoBoothConfig"]

try:
    from .controller import PhotoBoothController, PhotoBoothState

    __all__.extend(["PhotoBoothController", "PhotoBoothState"])
except ImportError:
    PhotoBoothController = None
    PhotoBoothState = None

try:
    from .retro_filter import RetroFilter

    __all__.append("RetroFilter")
except ImportError:
    RetroFilter = None

try:
    from .compositor import PhotoBoothCompositor

    __all__.append("PhotoBoothCompositor")
except ImportError:
    PhotoBoothCompositor = None
