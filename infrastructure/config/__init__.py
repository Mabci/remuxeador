"""
Config - Configuración del sistema
"""

from .settings import (
    Settings,
    PathSettings,
    VideoSettings,
    LanguageSettings,
    PatternSettings,
    UISettings,
    get_settings,
    reset_settings,
    get_legacy_config
)

__all__ = [
    'Settings',
    'PathSettings',
    'VideoSettings',
    'LanguageSettings',
    'PatternSettings',
    'UISettings',
    'get_settings',
    'reset_settings',
    'get_legacy_config',
]
