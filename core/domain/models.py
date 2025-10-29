"""
Models - Modelos de dominio

Entidades principales del sistema. Son inmutables (frozen dataclasses) para garantizar integridad de datos.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from .enums import TrackType, JobStatus, CodecType, LanguageCode


@dataclass(frozen=True)
class Track:
    """
    Representa una pista de audio, video o subtítulos.
    
    Inmutable para garantizar integridad de datos.
    """
    id: int
    type: TrackType
    codec: str
    language: LanguageCode = LanguageCode.UNKNOWN
    title: Optional[str] = None
    offset_ms: int = 0
    is_default: bool = False
    is_forced: bool = False
    file_path: Optional[Path] = None  # Ruta del archivo de la pista (para externas)
    
    # Metadatos adicionales
    bitrate: Optional[int] = None
    duration: Optional[float] = None
    
    def __str__(self) -> str:
        """Representación legible"""
        return f"{self.type.name} #{self.id}: {self.codec} ({self.language.value})"
    
    def with_offset(self, offset_ms: int) -> 'Track':
        """Retorna una nueva pista con offset modificado (inmutable)"""
        return Track(
            id=self.id,
            type=self.type,
            codec=self.codec,
            language=self.language,
            title=self.title,
            offset_ms=offset_ms,
            is_default=self.is_default,
            is_forced=self.is_forced,
            file_path=self.file_path,
            bitrate=self.bitrate,
            duration=self.duration
        )


@dataclass(frozen=True)
class MediaInfo:
    """
    Información de un archivo multimedia.
    
    Contiene todas las pistas y metadatos del archivo.
    """
    file_path: Path
    duration: float
    format_name: str
    size_bytes: int
    
    video_tracks: List[Track] = field(default_factory=list)
    audio_tracks: List[Track] = field(default_factory=list)
    subtitle_tracks: List[Track] = field(default_factory=list)
    
    # Metadatos adicionales
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_video(self) -> bool:
        """Verifica si tiene pistas de video"""
        return len(self.video_tracks) > 0
    
    @property
    def has_audio(self) -> bool:
        """Verifica si tiene pistas de audio"""
        return len(self.audio_tracks) > 0
    
    @property
    def has_subtitles(self) -> bool:
        """Verifica si tiene subtítulos"""
        return len(self.subtitle_tracks) > 0
    
    def __str__(self) -> str:
        """Representación legible"""
        return (
            f"MediaInfo({self.file_path.name}): "
            f"{len(self.video_tracks)}V, "
            f"{len(self.audio_tracks)}A, "
            f"{len(self.subtitle_tracks)}S"
        )


@dataclass
class RemuxJob:
    """
    Trabajo de remuxeo.
    
    Mutable porque representa un proceso que cambia de estado.
    Contiene toda la información necesaria para ejecutar un remuxeo.
    """
    # Archivos
    video_file: Path
    output_file: Path
    
    # Pistas a incluir
    audio_tracks: List[Track] = field(default_factory=list)
    subtitle_tracks: List[Track] = field(default_factory=list)
    
    # Opciones
    overwrite_source_subtitles: bool = False
    include_original_audio: bool = True
    include_original_subtitles: bool = True
    
    # Estado
    status: JobStatus = JobStatus.PENDING
    progress: int = 0  # 0-100
    error_message: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __str__(self) -> str:
        """Representación legible"""
        return (
            f"RemuxJob({self.video_file.name} -> {self.output_file.name}): "
            f"{self.status.name} ({self.progress}%)"
        )
    
    @property
    def is_pending(self) -> bool:
        return self.status == JobStatus.PENDING
    
    @property
    def is_running(self) -> bool:
        return self.status == JobStatus.RUNNING
    
    @property
    def is_completed(self) -> bool:
        return self.status == JobStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        return self.status == JobStatus.FAILED
    
    def start(self) -> None:
        """Marca el job como iniciado"""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.now()
        self.progress = 0
    
    def complete(self) -> None:
        """Marca el job como completado"""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress = 100
    
    def fail(self, error_message: str) -> None:
        """Marca el job como fallido"""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
    
    def update_progress(self, progress: int) -> None:
        """Actualiza el progreso (0-100)"""
        self.progress = max(0, min(100, progress))


@dataclass
class RemuxResult:
    """
    Resultado de un remuxeo.
    
    Inmutable, representa el resultado final de una operación.
    """
    success: bool
    output_file: Optional[Path] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    
    # Estadísticas
    input_size_bytes: Optional[int] = None
    output_size_bytes: Optional[int] = None
    
    def __str__(self) -> str:
        """Representación legible"""
        if self.success:
            return f"RemuxResult: ✅ Success ({self.output_file})"
        else:
            return f"RemuxResult: ❌ Failed ({self.error_message})"


@dataclass
class DualVideoRemuxJob:
    """
    Trabajo de remuxeo para dos videos (ej: JP + LAT).
    
    Combina dos videos en uno solo, aplicando offsets de sincronización.
    Usado típicamente para anime dual audio (japonés + latino).
    """
    # Archivos de entrada
    video_primary: Path      # Video base (ej: japonés con subtítulos)
    video_secondary: Path    # Video a sincronizar (ej: latino)
    output_file: Path
    
    # Offsets de sincronización (en milisegundos)
    audio_offset_ms: int = 0        # Offset del audio del video secundario
    subtitle_offset_ms: int = 0     # Offset de subtítulos (si aplica)
    
    # Configuración de pistas
    include_primary_audio: bool = True      # Incluir audio del video primario
    include_secondary_audio: bool = True    # Incluir audio del video secundario
    include_primary_subtitles: bool = True  # Incluir subtítulos del video primario
    include_secondary_subtitles: bool = False  # Incluir subtítulos del video secundario
    
    # Metadatos de audio
    primary_audio_language: LanguageCode = LanguageCode.JAPANESE
    primary_audio_title: str = "Japonés"
    secondary_audio_language: LanguageCode = LanguageCode.SPANISH_LATIN
    secondary_audio_title: str = "Español Latino"
    
    # Pistas externas adicionales (opcional)
    external_audio_tracks: List[Track] = field(default_factory=list)
    external_subtitle_tracks: List[Track] = field(default_factory=list)
    
    # Estado
    status: JobStatus = JobStatus.PENDING
    progress: int = 0
    error_message: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def start(self) -> None:
        """Marca el job como iniciado"""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.now()
        self.progress = 0
    
    def complete(self) -> None:
        """Marca el job como completado"""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress = 100
    
    def fail(self, error_message: str) -> None:
        """Marca el job como fallido"""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
    
    def update_progress(self, progress: int) -> None:
        """Actualiza el progreso (0-100)"""
        self.progress = max(0, min(100, progress))
    
    def __str__(self) -> str:
        """Representación legible"""
        return (
            f"DualVideoRemuxJob({self.video_primary.name} + {self.video_secondary.name} "
            f"-> {self.output_file.name}): {self.status.name} ({self.progress}%)"
        )


@dataclass
class Episode:
    """
    Representa un episodio con sus archivos asociados.
    
    Usado para procesamiento por lotes.
    """
    number: int
    video_file: Optional[Path] = None
    audio_files: List[Path] = field(default_factory=list)
    subtitle_files: List[Path] = field(default_factory=list)
    forced_subtitle_files: List[Path] = field(default_factory=list)
    
    @property
    def is_complete(self) -> bool:
        """Verifica si el episodio tiene al menos video"""
        return self.video_file is not None
    
    @property
    def has_audio(self) -> bool:
        """Verifica si tiene archivos de audio"""
        return len(self.audio_files) > 0
    
    @property
    def has_subtitles(self) -> bool:
        """Verifica si tiene subtítulos"""
        return len(self.subtitle_files) > 0
    
    def __str__(self) -> str:
        """Representación legible"""
        status = "✅" if self.is_complete else "❌"
        return (
            f"Episode {self.number:02d} {status}: "
            f"V={self.video_file.name if self.video_file else 'None'}, "
            f"A={len(self.audio_files)}, "
            f"S={len(self.subtitle_files)}"
        )
