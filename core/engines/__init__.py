"""
Engines - Wrappers para herramientas externas

Cada engine encapsula la lógica de ejecución de una herramienta específica.
Siguen el patrón Strategy para permitir intercambiarlos fácilmente.

NOTA: FFmpegEngine fue eliminado. Ahora solo usamos MKVMerge para remuxeo.
"""

from .base_engine import BaseEngine
from .mkvmerge_engine import MKVMergeEngine
from .ffprobe_engine import FFprobeEngine

__all__ = [
    'BaseEngine',
    'MKVMergeEngine',
    'FFprobeEngine',
]
