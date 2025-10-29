"""
Time Utils - Utilidades para manejo de tiempo y timestamps

Conversiones entre diferentes formatos de tiempo (DRY).
"""
import re
from typing import Optional


def seconds_to_milliseconds(seconds: float) -> int:
    """
    Convierte segundos a milisegundos.
    
    Args:
        seconds: Tiempo en segundos
        
    Returns:
        Tiempo en milisegundos
    """
    return int(seconds * 1000)


def milliseconds_to_seconds(milliseconds: int) -> float:
    """
    Convierte milisegundos a segundos.
    
    Args:
        milliseconds: Tiempo en milisegundos
        
    Returns:
        Tiempo en segundos
    """
    return milliseconds / 1000.0


def format_timestamp(seconds: float, format_type: str = "srt") -> str:
    """
    Formatea segundos a timestamp según el formato especificado.
    
    Args:
        seconds: Tiempo en segundos
        format_type: Tipo de formato ('srt', 'ass', 'ffmpeg')
        
    Returns:
        Timestamp formateado
    """
    if seconds < 0:
        seconds = 0
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    
    if format_type == "srt":
        # 00:01:23,456
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    elif format_type == "ass":
        # 0:01:23.45 (centésimas)
        centiseconds = milliseconds // 10
        return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"
    elif format_type == "ffmpeg":
        # 00:01:23.456
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    else:
        raise ValueError(f"Formato desconocido: {format_type}")


def parse_timestamp(timestamp: str, format_type: str = "auto") -> Optional[float]:
    """
    Parsea un timestamp a segundos.
    
    Args:
        timestamp: Timestamp como string
        format_type: Tipo de formato ('srt', 'ass', 'ffmpeg', 'auto')
        
    Returns:
        Tiempo en segundos o None si no se puede parsear
    """
    timestamp = timestamp.strip()
    
    if format_type == "auto":
        # Detectar formato automáticamente
        if "," in timestamp:
            format_type = "srt"
        elif "." in timestamp:
            # Puede ser ASS o FFmpeg
            parts = timestamp.split(":")
            if len(parts) == 3 and len(parts[0]) == 1:
                format_type = "ass"
            else:
                format_type = "ffmpeg"
        else:
            return None
    
    try:
        if format_type == "srt":
            # 00:01:23,456
            match = re.match(r'(\d+):(\d+):(\d+),(\d+)', timestamp)
            if match:
                h, m, s, ms = map(int, match.groups())
                return h * 3600 + m * 60 + s + ms / 1000.0
        
        elif format_type == "ass":
            # 0:01:23.45
            match = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', timestamp)
            if match:
                h, m, s, cs = map(int, match.groups())
                return h * 3600 + m * 60 + s + cs / 100.0
        
        elif format_type == "ffmpeg":
            # 00:01:23.456
            match = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', timestamp)
            if match:
                h, m, s, ms = map(int, match.groups())
                return h * 3600 + m * 60 + s + ms / 1000.0
    
    except (ValueError, AttributeError):
        pass
    
    return None


def format_duration(seconds: float) -> str:
    """
    Formatea una duración de forma legible.
    
    Args:
        seconds: Duración en segundos
        
    Returns:
        Duración formateada (ej: "1h 23m 45s")
    """
    if seconds < 0:
        return "0s"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def parse_ffmpeg_time(time_str: str) -> Optional[float]:
    """
    Parsea el formato de tiempo de FFmpeg (time=00:01:23.45).
    
    Args:
        time_str: String con formato de FFmpeg
        
    Returns:
        Tiempo en segundos o None
    """
    match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', time_str)
    if match:
        hours, minutes, seconds = match.groups()
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    return None
