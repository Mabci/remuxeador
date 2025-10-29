"""
Settings - Configuración centralizada

Configuración del sistema usando dataclasses.
Migrado y mejorado del config.py original.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import os


@dataclass
class PathSettings:
    """Configuración de rutas del sistema"""
    
    # Directorio base del proyecto
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    
    # Directorios
    external_dir: Path = field(init=False)
    mpv_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    
    # Ejecutables
    ffmpeg_path: str = "ffmpeg"
    ffprobe_path: str = "ffprobe"
    mkvmerge_path: Optional[str] = None
    mpv_path: Optional[str] = None
    
    def __post_init__(self):
        """Inicializa rutas derivadas"""
        self.external_dir = self.base_dir / "external"
        self.mpv_dir = self.external_dir / "mpv"
        self.logs_dir = self.base_dir / "logs"
        
        # Crear directorio de logs si no existe
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configurar MPV portable si existe
        mpv_exe = self.mpv_dir / "mpv.exe"
        if mpv_exe.exists():
            self.mpv_path = str(mpv_exe)
            # Agregar al PATH para libmpv
            mpv_dir_str = str(self.mpv_dir)
            if mpv_dir_str not in os.environ.get("PATH", ""):
                os.environ["PATH"] = mpv_dir_str + os.pathsep + os.environ.get("PATH", "")


@dataclass
class VideoSettings:
    """Configuración de video"""
    
    default_output_extension: str = ".mkv"
    default_video_codec: str = "copy"
    default_audio_codec: str = "copy"
    default_subtitle_codec: str = "copy"


@dataclass
class LanguageSettings:
    """Configuración de idiomas"""
    
    # Códigos ISO 639-2
    japanese_code: str = "jpn"
    spanish_code: str = "spa"
    english_code: str = "eng"
    portuguese_code: str = "por"
    
    # Títulos predeterminados
    default_audio_jp_title: str = "Japonés"
    default_audio_lat_title: str = "Español Latino"
    default_sub_lat_title: str = "Español Latino"


@dataclass
class PatternSettings:
    """Configuración de patrones de búsqueda"""
    
    # Patrones para archivos
    pattern_jp: str = "_JP.mkv"
    pattern_lat: str = "_LAT.mkv"


@dataclass
class UISettings:
    """Configuración de interfaz de usuario"""
    
    window_width: int = 1400
    window_height: int = 900
    theme: str = "dark"


@dataclass
class Settings:
    """
    Configuración global del sistema.
    
    Centraliza toda la configuración en un solo lugar.
    Usa dataclasses para type safety y valores por defecto.
    """
    
    paths: PathSettings = field(default_factory=PathSettings)
    video: VideoSettings = field(default_factory=VideoSettings)
    languages: LanguageSettings = field(default_factory=LanguageSettings)
    patterns: PatternSettings = field(default_factory=PatternSettings)
    ui: UISettings = field(default_factory=UISettings)
    
    # Configuración de logging
    log_level: str = "INFO"
    log_to_file: bool = True
    log_to_console: bool = True
    
    def __str__(self) -> str:
        """Representación legible"""
        return (
            f"Settings(\n"
            f"  Base Dir: {self.paths.base_dir}\n"
            f"  FFmpeg: {self.paths.ffmpeg_path}\n"
            f"  MKVMerge: {self.paths.mkvmerge_path or 'Not configured'}\n"
            f"  MPV: {self.paths.mpv_path or 'Not configured'}\n"
            f")"
        )


# Singleton global
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Obtiene la instancia global de configuración (Singleton).
    
    Returns:
        Settings global
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Resetea la configuración (útil para tests)"""
    global _settings
    _settings = None


# Compatibilidad con config.py antiguo
def get_legacy_config() -> dict:
    """
    Retorna configuración en formato del config.py antiguo.
    
    Para compatibilidad durante la migración.
    """
    settings = get_settings()
    
    return {
        'BASE_DIR': settings.paths.base_dir,
        'EXTERNAL_DIR': settings.paths.external_dir,
        'MPV_PORTABLE_DIR': settings.paths.mpv_dir,
        'FFMPEG_PATH': settings.paths.ffmpeg_path,
        'MPV_PATH': settings.paths.mpv_path,
        'DEFAULT_OUTPUT_EXTENSION': settings.video.default_output_extension,
        'JAPANESE_LANG': settings.languages.japanese_code,
        'SPANISH_LANG': settings.languages.spanish_code,
        'DEFAULT_AUDIO_JP_TITLE': settings.languages.default_audio_jp_title,
        'DEFAULT_AUDIO_LAT_TITLE': settings.languages.default_audio_lat_title,
        'DEFAULT_SUB_LAT_TITLE': settings.languages.default_sub_lat_title,
        'PATTERN_JP': settings.patterns.pattern_jp,
        'PATTERN_LAT': settings.patterns.pattern_lat,
        'WINDOW_WIDTH': settings.ui.window_width,
        'WINDOW_HEIGHT': settings.ui.window_height,
        'THEME': settings.ui.theme,
        'LOGS_DIR': settings.paths.logs_dir,
    }
