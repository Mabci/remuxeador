"""
Assembler ViewModel - ViewModel para Assembler Tab

Maneja la lógica de ensamblado de video con pistas externas.
"""
from pathlib import Path
from typing import Optional

from .base_viewmodel import BaseViewModel
from ..workers import RemuxWorker
from core.domain.models import RemuxJob, Track
from core.domain.enums import TrackType, LanguageCode


class AssemblerViewModel(BaseViewModel):
    """
    ViewModel para el tab Assembler.
    
    Maneja la lógica de ensamblado de video con pistas externas
    (audio, subtítulos y letreros en español latino).
    """
    
    def __init__(self, remux_service):
        super().__init__(remux_service)
        self.current_worker: Optional[RemuxWorker] = None
    
    def start_remux(
        self,
        video_path: str,
        audio_path: str,
        subtitle_path: str,
        forced_path: str,
        output_path: str,
        audio_offset_ms: int = 0,
        subtitle_offset_ms: int = 0
    ):
        """
        Inicia el remuxeo de un episodio (Assembler).
        
        Args:
            video_path: Ruta al video
            audio_path: Ruta al audio externo (puede estar vacío)
            subtitle_path: Ruta a subtítulos externos (puede estar vacío)
            forced_path: Ruta a letreros/forced subtitles (puede estar vacío)
            output_path: Ruta de salida
            audio_offset_ms: Offset de audio en ms
            subtitle_offset_ms: Offset de subtítulos en ms
        """
        # Validar
        if not video_path or not output_path:
            self.emit_error("Faltan archivos requeridos (video y salida)")
            return
        
        if self.is_busy:
            self.emit_error("Ya hay un remuxeo en progreso")
            return
        
        try:
            # Crear tracks
            audio_tracks = []
            if audio_path:
                audio_track = Track(
                    id=0,
                    type=TrackType.AUDIO,
                    codec="copy",
                    language=LanguageCode.SPANISH_LATIN,
                    title="Español Latino",  # Título descriptivo
                    file_path=Path(audio_path),  # Ruta del archivo
                    offset_ms=audio_offset_ms,
                    is_default=True
                )
                audio_tracks.append(audio_track)
            
            subtitle_tracks = []
            if subtitle_path:
                subtitle_track = Track(
                    id=0,
                    type=TrackType.SUBTITLE,
                    codec="copy",
                    language=LanguageCode.SPANISH_LATIN,
                    title="Español Latino",  # Título descriptivo
                    file_path=Path(subtitle_path),  # Ruta del archivo
                    offset_ms=subtitle_offset_ms,
                    is_default=True
                )
                subtitle_tracks.append(subtitle_track)
            
            # Agregar letreros (forced subtitles) si existen
            if forced_path:
                forced_track = Track(
                    id=len(subtitle_tracks),
                    type=TrackType.SUBTITLE,
                    codec="copy",
                    language=LanguageCode.SPANISH_LATIN,
                    title="Letreros",  # Título descriptivo para forzados
                    file_path=Path(forced_path),  # Ruta del archivo
                    offset_ms=subtitle_offset_ms,
                    is_forced=True,
                    is_default=False  # Los letreros no son default
                )
                subtitle_tracks.append(forced_track)
            
            # Crear job
            job = RemuxJob(
                video_file=Path(video_path),
                output_file=Path(output_path),
                audio_tracks=audio_tracks,
                subtitle_tracks=subtitle_tracks,
                include_original_audio=True,
                include_original_subtitles=True
            )
            
            # Crear y configurar worker
            self.current_worker = RemuxWorker(job, self.remux_service)
            
            # Conectar signals
            self.current_worker.progress.connect(self.emit_progress)
            self.current_worker.status.connect(self.emit_status)
            self.current_worker.log.connect(self.log)
            self.current_worker.finished.connect(self._on_remux_finished)
            
            # Iniciar
            self._set_busy(True)
            self.log("🎬 Iniciando remuxeo...", "info")
            self.current_worker.start()
        
        except Exception as e:
            self.emit_error(f"Error iniciando remuxeo: {str(e)}")
            self._set_busy(False)
    
    def start_batch_remux(
        self,
        episodes: dict,
        output_directory: Path,
        audio_offset_ms: int = 0,
        subtitle_offset_ms: int = 0
    ):
        """
        Inicia el remuxeo por lotes de múltiples episodios.
        
        Args:
            episodes: Diccionario de episodios {ep_num: episode_data}
            output_directory: Directorio de salida
            audio_offset_ms: Offset de audio en ms
            subtitle_offset_ms: Offset de subtítulos en ms
        """
        if self.is_busy:
            self.emit_error("Ya hay un remuxeo en progreso")
            return
        
        try:
            from core.services.batch_service import BatchService
            from core.domain.models import Episode
            
            # Convertir el diccionario de episodios al formato Episode
            episode_objects = {}
            for ep_num, ep_data in episodes.items():
                episode = Episode(
                    number=ep_num,
                    video_file=Path(ep_data['video']) if ep_data.get('video') else None,
                    audio_files=[Path(ep_data['audio'])] if ep_data.get('audio') else [],
                    subtitle_files=[Path(ep_data['subtitle'])] if ep_data.get('subtitle') else [],
                    forced_subtitle_files=[Path(ep_data['forced'])] if ep_data.get('forced') else []
                )
                episode_objects[ep_num] = episode
            
            # Crear BatchService
            batch_service = BatchService(self.remux_service)
            
            # Callback de progreso por episodio
            def episode_progress(ep_num: int, progress: int, message: str):
                overall_message = f"Episodio {ep_num}: {message}"
                self.emit_progress(progress, overall_message)
                self.log(overall_message, "info")
            
            self._set_busy(True)
            self.log("🎬 Iniciando remuxeo por lotes...", "info")
            
            # Procesar episodios
            result = batch_service.process_episodes(
                episodes=episode_objects,
                output_directory=output_directory,
                output_pattern="Episode_{ep:02d}_REMUX.mkv",
                audio_offset_ms=audio_offset_ms,
                subtitle_offset_ms=subtitle_offset_ms,
                progress_callback=episode_progress
            )
            
            # Reportar resultados
            self._set_busy(False)
            
            if result.successful > 0:
                self.log(f"✅ {result.successful}/{result.total_episodes} episodios completados", "success")
                self.emit_completed(True)
            
            if result.failed > 0:
                self.log(f"❌ {result.failed} episodios fallaron", "error")
                if result.successful == 0:
                    self.emit_completed(False)
        
        except Exception as e:
            self.emit_error(f"Error en remuxeo por lotes: {str(e)}")
            self._set_busy(False)
    
    def cancel_remux(self):
        """Cancela el remuxeo actual"""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
            self.log("⏹️ Cancelando remuxeo...", "warning")
    
    def _on_remux_finished(self, success: bool, message: str):
        """
        Callback cuando termina el remuxeo.
        
        Args:
            success: True si fue exitoso
            message: Mensaje de resultado o error
        """
        self._set_busy(False)
        
        if success:
            self.log(f"✅ Remuxeo completado: {message}", "success")
            self.emit_completed(True)
        else:
            self.log(f"❌ Remuxeo fallido: {message}", "error")
            self.emit_completed(False)
        
        self.current_worker = None
