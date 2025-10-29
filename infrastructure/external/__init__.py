"""
External - Gestión de herramientas externas
"""

from .mpv_manager import MPVManager, check_mpv_installation
from .tool_detector import ToolDetector, ToolInfo

__all__ = [
    'MPVManager',
    'check_mpv_installation',
    'ToolDetector',
    'ToolInfo',
]
