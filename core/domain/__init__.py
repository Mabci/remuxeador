"""
Domain - Modelos de dominio y entidades de negocio

Contiene las entidades principales del sistema sin dependencias externas.
"""

from .models import Track, RemuxJob, RemuxResult, Episode, MediaInfo, DualVideoRemuxJob
from .enums import TrackType, JobStatus, CodecType, LanguageCode

__all__ = [
    'Track',
    'RemuxJob', 
    'RemuxResult',
    'Episode',
    'MediaInfo',
    'DualVideoRemuxJob',
    'TrackType',
    'JobStatus',
    'CodecType',
    'LanguageCode',
]
