"""
Archivo de configuración de ejemplo para Remuxeador FFmpeg.

IMPORTANTE: Este archivo es solo un ejemplo. No modifiques este archivo directamente.
Para personalizar la configuración, copia este archivo como 'config.local.py' y 
modifica los valores según tus necesidades.

El archivo config.local.py será ignorado por git (ver .gitignore).
"""
import os
from pathlib import Path

# ============================================
# RUTAS DE HERRAMIENTAS EXTERNAS
# ============================================

# MKVMerge (OBLIGATORIO)
# Si mkvmerge no está en el PATH del sistema, especifica la ruta completa aquí
MKVMERGE_PATH = "mkvmerge"
# Ejemplo Windows: MKVMERGE_PATH = r"C:\Program Files\MKVToolNix\mkvmerge.exe"
# Ejemplo Linux: MKVMERGE_PATH = "/usr/bin/mkvmerge"

# MPV (OPCIONAL - para previsualización)
# Si mpv no está en el PATH del sistema, especifica la ruta completa aquí
MPV_PATH = "mpv"
# Ejemplo Windows: MPV_PATH = r"C:\Program Files\mpv\mpv.exe"
# Ejemplo Linux: MPV_PATH = "/usr/bin/mpv"

# FFmpeg (LEGACY - actualmente no se usa, pero puede ser útil en el futuro)
FFMPEG_PATH = "ffmpeg"

# ============================================
# CONFIGURACIÓN DE LOGGING
# ============================================

# Nivel de logging: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# Guardar logs en archivos
LOG_TO_FILE = True

# Mostrar logs en consola
LOG_TO_CONSOLE = True

# Directorio donde se guardarán los logs
LOGS_DIR = Path("logs")

# Rotación de logs (días)
LOG_ROTATION_DAYS = 30  # Eliminar logs más antiguos de 30 días

# ============================================
# CONFIGURACIÓN DE VIDEO
# ============================================

# Extensión de salida por defecto
DEFAULT_OUTPUT_EXTENSION = ".mkv"

# Codecs por defecto (usar "copy" para no recodificar)
DEFAULT_VIDEO_CODEC = "copy"
DEFAULT_AUDIO_CODEC = "copy"
DEFAULT_SUBTITLE_CODEC = "copy"

# ============================================
# CONFIGURACIÓN DE IDIOMAS
# ============================================

# Códigos de idioma ISO 639-2
JAPANESE_LANG = "jpn"
SPANISH_LANG = "spa"
ENGLISH_LANG = "eng"
PORTUGUESE_LANG = "por"

# Títulos predeterminados para pistas
DEFAULT_AUDIO_JP_TITLE = "Japonés"
DEFAULT_AUDIO_LAT_TITLE = "Español Latino"
DEFAULT_AUDIO_ENG_TITLE = "Inglés"
DEFAULT_SUB_LAT_TITLE = "Español Latino"
DEFAULT_SUB_ENG_TITLE = "Inglés"

# ============================================
# PATRONES DE BÚSQUEDA
# ============================================

# Patrones para identificar archivos en modo Dual Sync
PATTERN_JP = "_JP.mkv"
PATTERN_LAT = "_LAT.mkv"

# Expresiones regulares para extraer números de episodio
# Puedes agregar más patrones según tus necesidades
EPISODE_PATTERNS = [
    r"[Ee][Pp]?(\d+)",           # EP01, ep01, E01, e01
    r"[Cc]ap[ií]tulo\s*(\d+)",   # Capítulo 01, capitulo 01
    r"[-\s](\d+)[-\s]",          # - 01 -
    r"[-\s](\d+)\.",             # - 01.
]

# ============================================
# CONFIGURACIÓN DE UI
# ============================================

# Dimensiones de ventana
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Tema: "dark" o "light"
THEME = "dark"

# Tamaño de fuente
FONT_SIZE = 10

# ============================================
# CONFIGURACIÓN DE PROCESAMIENTO
# ============================================

# Número máximo de procesos paralelos en modo batch
MAX_PARALLEL_PROCESSES = 1  # Por ahora solo soporta 1

# Timeout para operaciones de remuxeo (segundos)
REMUX_TIMEOUT = 3600  # 1 hora

# Reintentos en caso de error
MAX_RETRIES = 3

# ============================================
# CONFIGURACIÓN AVANZADA
# ============================================

# Directorio temporal para archivos intermedios
TEMP_DIR = Path("temp")

# Limpiar archivos temporales al finalizar
CLEANUP_TEMP_FILES = True

# Verificar integridad de archivos de salida
VERIFY_OUTPUT = True

# Crear backup de archivos originales antes de sobrescribir
CREATE_BACKUPS = False

# Directorio de backups
BACKUP_DIR = Path("backups")

# ============================================
# METADATOS PREDETERMINADOS
# ============================================

# Metadatos globales para archivos de salida
DEFAULT_METADATA = {
    "title": "",  # Dejar vacío para usar nombre de archivo
    "creation_time": "",  # Dejar vacío para usar fecha actual
}

# ============================================
# NOTAS
# ============================================

# Para aplicar esta configuración:
# 1. Copia este archivo como 'config.local.py'
# 2. Modifica los valores según tus necesidades
# 3. El sistema cargará automáticamente config.local.py si existe
# 4. Los valores en config.local.py sobrescribirán los valores por defecto
