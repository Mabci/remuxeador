"""
Configuración del Remuxeador FFmpeg
"""
import os
import sys
from pathlib import Path

# Detectar directorio base del proyecto
BASE_DIR = Path(__file__).parent
EXTERNAL_DIR = BASE_DIR / "external"
MPV_PORTABLE_DIR = EXTERNAL_DIR / "mpv"
MPV_PORTABLE_EXE = MPV_PORTABLE_DIR / "mpv.exe"

# Rutas de herramientas externas
FFMPEG_PATH = "ffmpeg"  # Cambiar si FFmpeg no está en PATH

# MPV: usar portable si existe, sino buscar en PATH
if MPV_PORTABLE_EXE.exists():
    MPV_PATH = str(MPV_PORTABLE_EXE)
    LIBMPV_PATH = str(MPV_PORTABLE_DIR / "libmpv-2.dll")
    
    # IMPORTANTE: Agregar directorio de MPV al PATH para python-mpv
    mpv_dir_str = str(MPV_PORTABLE_DIR)
    if mpv_dir_str not in os.environ.get("PATH", ""):
        os.environ["PATH"] = mpv_dir_str + os.pathsep + os.environ.get("PATH", "")
        print(f"✅ Agregado {mpv_dir_str} al PATH para libmpv")
else:
    MPV_PATH = "mpv"  # Buscar en PATH del sistema
    LIBMPV_PATH = None

# Configuración de video
DEFAULT_OUTPUT_EXTENSION = ".mkv"
DEFAULT_VIDEO_CODEC = "copy"
DEFAULT_AUDIO_CODEC = "copy"
DEFAULT_SUBTITLE_CODEC = "copy"

# Configuración de idiomas
JAPANESE_LANG = "jpn"
SPANISH_LANG = "spa"
PORTUGUESE_LANG = "por"

# Metadatos predeterminados
DEFAULT_AUDIO_JP_TITLE = "Japonés"
DEFAULT_AUDIO_LAT_TITLE = "Español Latino"
DEFAULT_SUB_LAT_TITLE = "Español Latino"

# Patrones de búsqueda para archivos
PATTERN_JP = "_JP.mkv"
PATTERN_LAT = "_LAT.mkv"

# Directorio de logs
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Configuración de UI
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
THEME = "dark-blue"
