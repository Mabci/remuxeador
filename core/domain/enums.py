"""
Enums - Enumeraciones del dominio

Define tipos y estados del sistema de forma clara y type-safe.
"""
from enum import Enum, auto


class TrackType(Enum):
    """Tipo de pista multimedia"""
    VIDEO = auto()
    AUDIO = auto()
    SUBTITLE = auto()
    ATTACHMENT = auto()


class JobStatus(Enum):
    """Estado de un trabajo de remuxeo"""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class CodecType(Enum):
    """Tipos de codec comunes"""
    # Video
    H264 = "h264"
    H265 = "hevc"
    VP9 = "vp9"
    AV1 = "av1"
    
    # Audio
    AAC = "aac"
    AC3 = "ac3"
    EAC3 = "eac3"
    OPUS = "opus"
    FLAC = "flac"
    
    # Subtítulos
    ASS = "ass"
    SRT = "srt"
    SUB = "sub"
    PGS = "pgs"
    
    # Copy (sin recodificar)
    COPY = "copy"


class LanguageCode(Enum):
    """
    Códigos de idioma ISO 639-1 con variantes regionales.
    
    Usa códigos de 2 letras (ISO 639-1) que son más comunes en streaming
    y plataformas web. Incluye variantes regionales para distinguir dialectos.
    """
    # Japonés
    JAPANESE = "ja"
    
    # Español (con variantes regionales)
    SPANISH = "es"              # Español genérico
    SPANISH_LATIN = "es-419"    # Español latino (América Latina)
    SPANISH_SPAIN = "es-ES"     # Español de España
    SPANISH_MEXICO = "es-MX"    # Español de México
    
    # Inglés (con variantes)
    ENGLISH = "en"
    ENGLISH_US = "en-US"        # Inglés estadounidense
    ENGLISH_UK = "en-GB"        # Inglés británico
    
    # Portugués (con variantes)
    PORTUGUESE = "pt"
    PORTUGUESE_BR = "pt-BR"     # Portugués brasileño
    PORTUGUESE_PT = "pt-PT"     # Portugués de Portugal
    
    # Otros idiomas
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    CHINESE = "zh"
    KOREAN = "ko"
    RUSSIAN = "ru"
    ARABIC = "ar"
    
    # Desconocido
    UNKNOWN = "und"
