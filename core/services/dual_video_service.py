"""
DualVideo Service - Servicio para remuxeo de videos duales

Maneja la combinación de dos videos (ej: JP + LAT) con offsets de sincronización.
Usa MKVMerge para aplicar offsets nativamente sin re-encodear.
"""
from pathlib import Path
from typing import Optional, Callable
import time

from ..domain.models import DualVideoRemuxJob, RemuxResult
from ..engines.mkvmerge_engine import MKVMergeEngine
from ..utils.validators import ValidationError


class DualVideoService:
    """
    Servicio para remuxeo de videos duales.
    
    Responsabilidades:
    - Validar trabajos de remuxeo dual
    - Construir comandos MKVMerge para dos videos
    - Aplicar offsets de audio/subtítulos
    - Coordinar el flujo completo
    """
    
    def __init__(self, mkvmerge_engine: Optional[MKVMergeEngine] = None):
        """
        Inicializa el servicio de remuxeo dual.
        
        Args:
            mkvmerge_engine: Engine de MKVMerge (se crea si es None)
        """
        self.mkvmerge = mkvmerge_engine or MKVMergeEngine()
    
    def remux_dual(
        self,
        job: DualVideoRemuxJob,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> RemuxResult:
        """
        Ejecuta un remuxeo de dos videos.
        
        Args:
            job: Trabajo de remuxeo dual
            progress_callback: Callback para reportar progreso (0-100)
            
        Returns:
            Resultado del remuxeo
        """
        start_time = time.time()
        
        try:
            # 1. Validar job
            self._validate_job(job)
            
            # 2. Marcar como iniciado
            job.start()
            
            # 3. Construir comando MKVMerge
            cmd = self._build_mkvmerge_command(job)
            
            # 4. Ejecutar remuxeo
            print(f"\n🔧 Remuxeando videos duales con MKVMerge")
            print(f"   Primary: {job.video_primary.name}")
            print(f"   Secondary: {job.video_secondary.name}")
            if job.audio_offset_ms != 0:
                print(f"   Audio offset: {job.audio_offset_ms}ms")
            
            result = self.mkvmerge.execute_command(cmd, progress_callback)
            
            # 5. Actualizar estado del job
            if result.success:
                job.complete()
            else:
                job.fail(result.error_message or "Error desconocido")
            
            # 6. Calcular duración
            duration = time.time() - start_time
            result.duration_seconds = duration
            
            return result
        
        except ValidationError as e:
            job.fail(f"Error de validación: {str(e)}")
            return RemuxResult(
                success=False,
                error_message=str(e)
            )
        
        except Exception as e:
            job.fail(f"Error inesperado: {str(e)}")
            return RemuxResult(
                success=False,
                error_message=str(e)
            )
    
    def _validate_job(self, job: DualVideoRemuxJob) -> None:
        """
        Valida un trabajo de remuxeo dual.
        
        Args:
            job: Trabajo a validar
            
        Raises:
            ValidationError: Si el job no es válido
        """
        # Validar archivos de entrada
        if not job.video_primary.exists():
            raise ValidationError(f"Video primario no existe: {job.video_primary}")
        
        if not job.video_secondary.exists():
            raise ValidationError(f"Video secundario no existe: {job.video_secondary}")
        
        # Validar que no sean el mismo archivo
        if job.video_primary.resolve() == job.video_secondary.resolve():
            raise ValidationError("Los videos primario y secundario no pueden ser el mismo archivo")
        
        # Validar directorio de salida
        output_dir = job.output_file.parent
        if not output_dir.exists():
            raise ValidationError(f"Directorio de salida no existe: {output_dir}")
    
    def _build_mkvmerge_command(self, job: DualVideoRemuxJob) -> list:
        """
        Construye el comando MKVMerge para remuxeo dual.
        
        Args:
            job: Trabajo de remuxeo dual
            
        Returns:
            Lista con el comando y argumentos
        """
        cmd = [self.mkvmerge.executable_path]
        
        # Output
        cmd.extend(["-o", str(job.output_file)])
        
        # === VIDEO PRIMARIO (base) ===
        # Configurar qué pistas incluir del video primario
        if job.include_primary_audio:
            cmd.extend(["--audio-tracks", "all"])
        else:
            cmd.extend(["--audio-tracks", "none"])
        
        if job.include_primary_subtitles:
            cmd.extend(["--subtitle-tracks", "all"])
        else:
            cmd.extend(["--subtitle-tracks", "none"])
        
        # Metadatos del audio primario (si se incluye)
        if job.include_primary_audio:
            cmd.extend(["--language", f"0:{job.primary_audio_language.value}"])
            cmd.extend(["--track-name", f"0:{job.primary_audio_title}"])
            cmd.extend(["--default-track", "0:yes"])
        
        # Metadatos de subtítulos primarios (marcar como default)
        # Los subtítulos del video primario (JP) suelen ser español latino
        if job.include_primary_subtitles:
            # Marcar el primer subtítulo como default
            cmd.extend(["--default-track", "0:yes"])
        
        # Archivo primario
        cmd.append(str(job.video_primary))
        
        # === VIDEO SECUNDARIO (con offset) ===
        # Solo extraer audio del video secundario
        cmd.extend(["--no-video"])
        
        if not job.include_secondary_audio:
            cmd.extend(["--no-audio"])
        
        if not job.include_secondary_subtitles:
            cmd.extend(["--no-subtitles"])
        
        # Aplicar offset de audio (en milisegundos)
        if job.audio_offset_ms != 0 and job.include_secondary_audio:
            cmd.extend(["--sync", f"0:{job.audio_offset_ms}"])
        
        # Metadatos del audio secundario
        if job.include_secondary_audio:
            cmd.extend(["--language", f"0:{job.secondary_audio_language.value}"])
            cmd.extend(["--track-name", f"0:{job.secondary_audio_title}"])
            # No marcar como default (el primario ya lo es)
        
        # Archivo secundario
        cmd.append(str(job.video_secondary))
        
        # === PISTAS EXTERNAS ADICIONALES ===
        # Audios externos
        for track in job.external_audio_tracks:
            audio_file = self._get_track_file_from_title(track.title)
            if audio_file:
                if track.offset_ms != 0:
                    cmd.extend(["--sync", f"0:{track.offset_ms}"])
                if track.language:
                    cmd.extend(["--language", f"0:{track.language.value}"])
                if track.title:
                    cmd.extend(["--track-name", f"0:{track.title}"])
                if track.is_default:
                    cmd.extend(["--default-track", "0:yes"])
                cmd.append(str(audio_file))
        
        # Subtítulos externos
        for track in job.external_subtitle_tracks:
            subtitle_file = self._get_track_file_from_title(track.title)
            if subtitle_file:
                if track.offset_ms != 0:
                    cmd.extend(["--sync", f"0:{track.offset_ms}"])
                if track.language:
                    cmd.extend(["--language", f"0:{track.language.value}"])
                if track.title:
                    cmd.extend(["--track-name", f"0:{track.title}"])
                if track.is_forced:
                    cmd.extend(["--forced-display-flag", "0:1"])
                if track.is_default:
                    cmd.extend(["--default-track", "0:yes"])
                cmd.append(str(subtitle_file))
        
        return cmd
    
    def _get_track_file_from_title(self, title: Optional[str]) -> Optional[Path]:
        """
        Obtiene el archivo de una pista desde su título.
        
        Args:
            title: Título que contiene la ruta del archivo
            
        Returns:
            Path del archivo o None
        """
        if title and Path(title).exists():
            return Path(title)
        return None
    
    def is_available(self) -> bool:
        """
        Verifica si el servicio está disponible (MKVMerge instalado).
        
        Returns:
            True si MKVMerge está disponible
        """
        return self.mkvmerge is not None
    
    def __str__(self) -> str:
        """Representación legible"""
        return f"DualVideoService(MKVMerge: {self.mkvmerge.get_version()})"
