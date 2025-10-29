"""
Validators - Validadores de datos

Funciones para validar entradas y garantizar integridad de datos (SOLID).
"""
from pathlib import Path
from typing import List, Optional

from ..domain.models import Track, RemuxJob
from .file_utils import is_video_file, is_audio_file, is_subtitle_file


class ValidationError(Exception):
    """Excepción para errores de validación"""
    pass


def validate_file_exists(file_path: Path, file_type: str = "archivo") -> None:
    """
    Valida que un archivo existe.
    
    Args:
        file_path: Ruta del archivo
        file_type: Tipo de archivo para el mensaje de error
        
    Raises:
        ValidationError: Si el archivo no existe
    """
    if not file_path.exists():
        raise ValidationError(f"El {file_type} no existe: {file_path}")
    
    if not file_path.is_file():
        raise ValidationError(f"La ruta no es un archivo: {file_path}")


def validate_output_path(output_path: Path) -> None:
    """
    Valida que la ruta de salida es válida.
    
    Args:
        output_path: Ruta del archivo de salida
        
    Raises:
        ValidationError: Si la ruta no es válida
    """
    # Verificar que el directorio padre existe o se puede crear
    parent = output_path.parent
    if not parent.exists():
        try:
            parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValidationError(f"No se puede crear el directorio de salida: {e}")
    
    # Verificar que no es un directorio
    if output_path.exists() and output_path.is_dir():
        raise ValidationError(f"La ruta de salida es un directorio: {output_path}")


def validate_video_file(file_path: Path) -> None:
    """
    Valida que un archivo es de video.
    
    Args:
        file_path: Ruta del archivo
        
    Raises:
        ValidationError: Si no es un archivo de video válido
    """
    validate_file_exists(file_path, "archivo de video")
    
    if not is_video_file(file_path):
        raise ValidationError(
            f"El archivo no tiene una extensión de video válida: {file_path.suffix}"
        )


def validate_audio_file(file_path: Path) -> None:
    """
    Valida que un archivo es de audio.
    
    Args:
        file_path: Ruta del archivo
        
    Raises:
        ValidationError: Si no es un archivo de audio válido
    """
    validate_file_exists(file_path, "archivo de audio")
    
    if not is_audio_file(file_path):
        raise ValidationError(
            f"El archivo no tiene una extensión de audio válida: {file_path.suffix}"
        )


def validate_subtitle_file(file_path: Path) -> None:
    """
    Valida que un archivo es de subtítulos.
    
    Args:
        file_path: Ruta del archivo
        
    Raises:
        ValidationError: Si no es un archivo de subtítulos válido
    """
    validate_file_exists(file_path, "archivo de subtítulos")
    
    if not is_subtitle_file(file_path):
        raise ValidationError(
            f"El archivo no tiene una extensión de subtítulos válida: {file_path.suffix}"
        )


def validate_tracks(tracks: List[Track]) -> None:
    """
    Valida una lista de pistas.
    
    Args:
        tracks: Lista de pistas a validar
        
    Raises:
        ValidationError: Si las pistas no son válidas
    """
    if not tracks:
        return
    
    # Verificar que no hay IDs duplicados
    ids = [track.id for track in tracks]
    if len(ids) != len(set(ids)):
        raise ValidationError("Hay pistas con IDs duplicados")
    
    # Verificar que los offsets son razonables (< 1 hora)
    for track in tracks:
        if abs(track.offset_ms) > 3600000:  # 1 hora en ms
            raise ValidationError(
                f"El offset de la pista {track.id} es demasiado grande: "
                f"{track.offset_ms}ms"
            )


def validate_remux_job(job: RemuxJob) -> None:
    """
    Valida un trabajo de remuxeo completo.
    
    Args:
        job: Trabajo a validar
        
    Raises:
        ValidationError: Si el trabajo no es válido
    """
    # Validar archivo de video
    validate_video_file(job.video_file)
    
    # Validar ruta de salida
    validate_output_path(job.output_file)
    
    # Validar que la salida no sobrescribe la entrada
    if job.output_file.resolve() == job.video_file.resolve():
        raise ValidationError(
            "El archivo de salida no puede ser el mismo que el de entrada"
        )
    
    # Validar pistas
    validate_tracks(job.audio_tracks)
    validate_tracks(job.subtitle_tracks)
    
    # Validar que hay al menos algo que hacer
    if not job.audio_tracks and not job.subtitle_tracks:
        if not job.include_original_audio and not job.include_original_subtitles:
            raise ValidationError(
                "No hay pistas para incluir en el remuxeo"
            )
