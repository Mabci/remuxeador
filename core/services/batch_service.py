"""
Batch Service - Procesamiento por lotes

Servicio que maneja el procesamiento de múltiples episodios en lote.
Coordina RemuxService y EpisodeMatcher.
"""
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from ..domain.models import RemuxJob, RemuxResult, Episode, Track
from ..domain.enums import JobStatus, TrackType, LanguageCode
from .remux_service import RemuxService
from .episode_matcher import EpisodeMatcher
from ..utils.file_utils import generate_output_filename


@dataclass
class BatchResult:
    """Resultado de un procesamiento por lotes"""
    total_episodes: int
    successful: int
    failed: int
    skipped: int
    results: List[Dict]
    duration_seconds: float
    
    @property
    def success_rate(self) -> float:
        """Tasa de éxito (0-1)"""
        if self.total_episodes == 0:
            return 0.0
        return self.successful / self.total_episodes
    
    def __str__(self) -> str:
        """Representación legible"""
        return (
            f"BatchResult: {self.successful}/{self.total_episodes} exitosos "
            f"({self.success_rate*100:.1f}%), {self.failed} fallidos, "
            f"{self.skipped} omitidos"
        )


class BatchService:
    """
    Servicio para procesamiento por lotes de episodios.
    
    Responsabilidades:
    - Coordinar procesamiento de múltiples episodios
    - Generar nombres de salida
    - Reportar progreso global
    - Manejar errores por episodio
    """
    
    def __init__(
        self,
        remux_service: Optional[RemuxService] = None,
        episode_matcher: Optional[EpisodeMatcher] = None
    ):
        """
        Inicializa el servicio de batch.
        
        Args:
            remux_service: Servicio de remuxeo (se crea si es None)
            episode_matcher: Matcher de episodios (se crea si es None)
        """
        self.remux_service = remux_service or RemuxService()
        self.episode_matcher = episode_matcher or EpisodeMatcher()
    
    def process_directory(
        self,
        directory: Path,
        output_directory: Path,
        output_pattern: str = "Episode_{ep:02d}_REMUX.mkv",
        audio_offset_ms: int = 0,
        subtitle_offset_ms: int = 0,
        include_audio_tracks: Optional[List[int]] = None,
        include_subtitle_tracks: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> BatchResult:
        """
        Procesa todos los episodios en un directorio.
        
        Args:
            directory: Directorio con archivos
            output_directory: Directorio de salida
            output_pattern: Patrón para nombres de salida ({ep} = número)
            audio_offset_ms: Offset de audio en milisegundos
            subtitle_offset_ms: Offset de subtítulos en milisegundos
            include_audio_tracks: IDs de pistas de audio a incluir
            include_subtitle_tracks: Tipos de subtítulos a incluir
            progress_callback: Callback(episodio_num, progreso_0_100, mensaje)
            
        Returns:
            BatchResult con resultados
        """
        start_time = datetime.now()
        
        # 1. Escanear directorio
        print(f"\n📁 Escaneando directorio: {directory}")
        episodes = self.episode_matcher.scan_directory(directory)
        
        if not episodes:
            print("❌ No se encontraron episodios")
            return BatchResult(
                total_episodes=0,
                successful=0,
                failed=0,
                skipped=0,
                results=[],
                duration_seconds=0
            )
        
        # 2. Filtrar solo episodios completos
        complete_episodes = self.episode_matcher.filter_complete_episodes(episodes)
        
        print(f"✅ Encontrados {len(complete_episodes)} episodios completos")
        print(self.episode_matcher.get_summary(complete_episodes))
        
        # 3. Crear directorio de salida
        output_directory.mkdir(parents=True, exist_ok=True)
        
        # 4. Procesar cada episodio
        results = []
        successful = 0
        failed = 0
        skipped = 0
        
        for i, (ep_num, episode) in enumerate(sorted(complete_episodes.items())):
            print(f"\n{'='*70}")
            print(f"Procesando episodio {ep_num} ({i+1}/{len(complete_episodes)})")
            print(f"{'='*70}")
            
            # Callback de progreso global
            if progress_callback:
                progress_callback(ep_num, 0, f"Iniciando episodio {ep_num}")
            
            # Crear job
            job = self._create_job_from_episode(
                episode,
                output_directory,
                output_pattern,
                audio_offset_ms,
                subtitle_offset_ms
            )
            
            if job is None:
                print(f"⚠️ Episodio {ep_num} omitido (sin video)")
                skipped += 1
                results.append({
                    'episode': ep_num,
                    'success': False,
                    'skipped': True,
                    'error': 'Sin archivo de video'
                })
                continue
            
            # Callback de progreso por episodio
            def episode_progress(progress: int):
                if progress_callback:
                    progress_callback(ep_num, progress, f"Remuxeando... {progress}%")
            
            # Ejecutar remuxeo
            result = self.remux_service.remux(job, episode_progress)
            
            # Registrar resultado
            if result.success:
                successful += 1
                print(f"✅ Episodio {ep_num} completado: {result.output_file}")
                results.append({
                    'episode': ep_num,
                    'success': True,
                    'output': str(result.output_file),
                    'duration': result.duration_seconds
                })
            else:
                failed += 1
                print(f"❌ Episodio {ep_num} falló: {result.error_message}")
                results.append({
                    'episode': ep_num,
                    'success': False,
                    'error': result.error_message
                })
            
            # Callback final
            if progress_callback:
                status = "✅ Completado" if result.success else "❌ Fallido"
                progress_callback(ep_num, 100, status)
        
        # 5. Calcular duración total
        duration = (datetime.now() - start_time).total_seconds()
        
        # 6. Crear resultado
        batch_result = BatchResult(
            total_episodes=len(complete_episodes),
            successful=successful,
            failed=failed,
            skipped=skipped,
            results=results,
            duration_seconds=duration
        )
        
        # 7. Imprimir resumen
        print(f"\n{'='*70}")
        print("RESUMEN DEL LOTE")
        print(f"{'='*70}")
        print(f"Total: {batch_result.total_episodes}")
        print(f"✅ Exitosos: {batch_result.successful}")
        print(f"❌ Fallidos: {batch_result.failed}")
        print(f"⏭️ Omitidos: {batch_result.skipped}")
        print(f"⏱️ Duración: {duration:.1f}s")
        print(f"📊 Tasa de éxito: {batch_result.success_rate*100:.1f}%")
        print(f"{'='*70}\n")
        
        return batch_result
    
    def _create_job_from_episode(
        self,
        episode: Episode,
        output_directory: Path,
        output_pattern: str,
        audio_offset_ms: int,
        subtitle_offset_ms: int
    ) -> Optional[RemuxJob]:
        """
        Crea un RemuxJob a partir de un Episode.
        
        Args:
            episode: Episodio con archivos
            output_directory: Directorio de salida
            output_pattern: Patrón para nombre de salida
            audio_offset_ms: Offset de audio
            subtitle_offset_ms: Offset de subtítulos
            
        Returns:
            RemuxJob o None si no se puede crear
        """
        if not episode.video_file:
            return None
        
        # Generar nombre de salida
        output_name = output_pattern.format(ep=episode.number)
        output_file = output_directory / output_name
        
        # Crear tracks de audio
        audio_tracks = []
        for i, audio_file in enumerate(episode.audio_files):
            track = Track(
                id=i,
                type=TrackType.AUDIO,
                codec="copy",
                language=LanguageCode.SPANISH_LATIN,  # Español latino por defecto
                title="Español Latino",  # Título descriptivo
                file_path=audio_file,  # Ruta del archivo
                offset_ms=audio_offset_ms,
                is_default=(i == 0)  # Primer audio como default
            )
            audio_tracks.append(track)
        
        # Crear tracks de subtítulos
        subtitle_tracks = []
        for i, subtitle_file in enumerate(episode.subtitle_files):
            track = Track(
                id=i,
                type=TrackType.SUBTITLE,
                codec="copy",
                language=LanguageCode.SPANISH_LATIN,
                title="Español Latino",  # Título descriptivo
                file_path=subtitle_file,  # Ruta del archivo
                offset_ms=subtitle_offset_ms,
                is_default=(i == 0)
            )
            subtitle_tracks.append(track)
        
        # Agregar subtítulos forzados
        for i, forced_file in enumerate(episode.forced_subtitle_files):
            track = Track(
                id=len(subtitle_tracks) + i,
                type=TrackType.SUBTITLE,
                codec="copy",
                language=LanguageCode.SPANISH_LATIN,
                title="Letreros",  # Título descriptivo para forzados
                file_path=forced_file,  # Ruta del archivo
                offset_ms=subtitle_offset_ms,
                is_forced=True
            )
            subtitle_tracks.append(track)
        
        # Crear job
        job = RemuxJob(
            video_file=episode.video_file,
            output_file=output_file,
            audio_tracks=audio_tracks,
            subtitle_tracks=subtitle_tracks,
            include_original_audio=True,
            include_original_subtitles=True,
            overwrite_source_subtitles=False
        )
        
        return job
    
    def process_episodes(
        self,
        episodes: Dict[int, Episode],
        output_directory: Path,
        output_pattern: str = "Episode_{ep:02d}_REMUX.mkv",
        audio_offset_ms: int = 0,
        subtitle_offset_ms: int = 0,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> BatchResult:
        """
        Procesa una lista de episodios ya emparejados.
        
        Similar a process_directory pero recibe episodios ya preparados.
        
        Args:
            episodes: Diccionario de episodios
            output_directory: Directorio de salida
            output_pattern: Patrón para nombres
            audio_offset_ms: Offset de audio
            subtitle_offset_ms: Offset de subtítulos
            progress_callback: Callback de progreso
            
        Returns:
            BatchResult
        """
        # Implementación similar a process_directory
        # pero sin el escaneo inicial
        start_time = datetime.now()
        
        complete_episodes = self.episode_matcher.filter_complete_episodes(episodes)
        
        if not complete_episodes:
            return BatchResult(
                total_episodes=0,
                successful=0,
                failed=0,
                skipped=0,
                results=[],
                duration_seconds=0
            )
        
        output_directory.mkdir(parents=True, exist_ok=True)
        
        results = []
        successful = 0
        failed = 0
        
        for i, (ep_num, episode) in enumerate(sorted(complete_episodes.items())):
            job = self._create_job_from_episode(
                episode,
                output_directory,
                output_pattern,
                audio_offset_ms,
                subtitle_offset_ms
            )
            
            if job is None:
                continue
            
            def episode_progress(progress: int):
                if progress_callback:
                    progress_callback(ep_num, progress, f"Remuxeando... {progress}%")
            
            result = self.remux_service.remux(job, episode_progress)
            
            if result.success:
                successful += 1
                results.append({
                    'episode': ep_num,
                    'success': True,
                    'output': str(result.output_file)
                })
            else:
                failed += 1
                results.append({
                    'episode': ep_num,
                    'success': False,
                    'error': result.error_message
                })
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return BatchResult(
            total_episodes=len(complete_episodes),
            successful=successful,
            failed=failed,
            skipped=0,
            results=results,
            duration_seconds=duration
        )
    
    def __str__(self) -> str:
        """Representación legible"""
        return f"BatchService({self.remux_service})"
