"""
File Utils - Utilidades para manejo de archivos

Funciones reutilizables para operaciones con archivos (DRY).
"""
from pathlib import Path
from typing import List, Optional


# Extensiones soportadas
VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.mov', '.webm', '.flv', '.m4v'}
AUDIO_EXTENSIONS = {'.m4a', '.aac', '.mp3', '.flac', '.opus', '.ogg', '.wav'}
SUBTITLE_EXTENSIONS = {'.ass', '.srt', '.sub', '.ssa', '.vtt'}


def ensure_directory(path: Path) -> Path:
    """
    Asegura que un directorio existe, creándolo si es necesario.
    
    Args:
        path: Ruta del directorio
        
    Returns:
        Path del directorio creado
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(file_path: Path) -> str:
    """
    Obtiene la extensión de un archivo en minúsculas.
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        Extensión en minúsculas (ej: '.mkv')
    """
    return file_path.suffix.lower()


def is_video_file(file_path: Path) -> bool:
    """
    Verifica si un archivo es de video.
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        True si es archivo de video
    """
    return get_file_extension(file_path) in VIDEO_EXTENSIONS


def is_audio_file(file_path: Path) -> bool:
    """
    Verifica si un archivo es de audio.
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        True si es archivo de audio
    """
    return get_file_extension(file_path) in AUDIO_EXTENSIONS


def is_subtitle_file(file_path: Path) -> bool:
    """
    Verifica si un archivo es de subtítulos.
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        True si es archivo de subtítulos
    """
    return get_file_extension(file_path) in SUBTITLE_EXTENSIONS


def get_file_size(file_path: Path) -> int:
    """
    Obtiene el tamaño de un archivo en bytes.
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        Tamaño en bytes
    """
    return file_path.stat().st_size if file_path.exists() else 0


def find_files_by_extension(
    directory: Path,
    extensions: List[str],
    recursive: bool = False
) -> List[Path]:
    """
    Busca archivos por extensión en un directorio.
    
    Args:
        directory: Directorio donde buscar
        extensions: Lista de extensiones (ej: ['.mkv', '.mp4'])
        recursive: Si True, busca recursivamente
        
    Returns:
        Lista de archivos encontrados
    """
    if not directory.exists():
        return []
    
    extensions_lower = {ext.lower() for ext in extensions}
    pattern = "**/*" if recursive else "*"
    
    files = []
    for file_path in directory.glob(pattern):
        if file_path.is_file() and get_file_extension(file_path) in extensions_lower:
            files.append(file_path)
    
    return sorted(files)


def generate_output_filename(
    input_file: Path,
    suffix: str = "_REMUX",
    extension: Optional[str] = None
) -> Path:
    """
    Genera un nombre de archivo de salida basado en el archivo de entrada.
    
    Args:
        input_file: Archivo de entrada
        suffix: Sufijo a agregar antes de la extensión
        extension: Nueva extensión (si None, usa la original)
        
    Returns:
        Path del archivo de salida
    """
    stem = input_file.stem
    ext = extension if extension else input_file.suffix
    
    return input_file.parent / f"{stem}{suffix}{ext}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo removiendo caracteres inválidos.
    
    Args:
        filename: Nombre de archivo a sanitizar
        
    Returns:
        Nombre de archivo sanitizado
    """
    # Caracteres inválidos en Windows
    invalid_chars = '<>:"/\\|?*'
    
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    
    return sanitized
