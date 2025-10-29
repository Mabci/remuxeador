"""
MKVMerge Engine - Ejecución de comandos MKVMerge

Engine especializado en MKVMerge, que SÍ soporta offsets de audio/subtítulos.
Solo construye y ejecuta comandos, sin lógica de negocio.
"""
import re
import shutil
from pathlib import Path
from typing import List, Optional

from .base_engine import BaseEngine
from ..domain.models import RemuxJob, Track
from ..domain.enums import TrackType


class MKVMergeEngine(BaseEngine):
    """
    Engine para ejecutar comandos MKVMerge.
    
    Ventaja sobre FFmpeg: Soporta offsets de audio y subtítulos sin re-encodear.
    """
    
    def __init__(self, mkvmerge_path: Optional[str] = None):
        """
        Inicializa el engine de MKVMerge.
        
        Args:
            mkvmerge_path: Ruta al ejecutable. Si es None, busca en PATH.
        """
        if mkvmerge_path is None:
            mkvmerge_path = self._find_mkvmerge()
        
        super().__init__(mkvmerge_path)
    
    def _get_default_executable(self) -> str:
        """Retorna el nombre del ejecutable por defecto"""
        return "mkvmerge"
    
    def _find_mkvmerge(self) -> str:
        """
        Busca mkvmerge en el sistema.
        
        Returns:
            Ruta a mkvmerge o "mkvmerge" si no se encuentra
        """
        # Buscar en PATH
        mkvmerge = shutil.which("mkvmerge")
        if mkvmerge:
            return mkvmerge
        
        # Buscar en ubicaciones comunes de Windows
        common_paths = [
            r"C:\Program Files\MKVToolNix\mkvmerge.exe",
            r"C:\Program Files (x86)\MKVToolNix\mkvmerge.exe",
        ]
        
        for path in common_paths:
            if Path(path).exists():
                return path
        
        return "mkvmerge"
    
    def build_command(self, job: RemuxJob) -> List[str]:
        """
        Construye el comando MKVMerge para un trabajo de remuxeo.
        
        MKVMerge SOPORTA offsets de audio y subtítulos sin re-encodear.
        
        Args:
            job: Trabajo de remuxeo
            
        Returns:
            Lista con el comando y argumentos
        """
        cmd = [self.executable_path]
        
        # Output
        cmd.extend(["-o", str(job.output_file)])
        
        # Input principal: video
        self._add_video_input(cmd, job)
        
        # Inputs: audios externos con offsets
        for track in job.audio_tracks:
            self._add_audio_track(cmd, track)
        
        # Inputs: subtítulos externos con offsets
        for track in job.subtitle_tracks:
            self._add_subtitle_track(cmd, track)
        
        return cmd
    
    def _add_video_input(self, cmd: List[str], job: RemuxJob) -> None:
        """
        Agrega el input de video al comando.
        
        Args:
            cmd: Comando en construcción
            job: Trabajo de remuxeo
        """
        # Determinar qué pistas incluir del video original
        audio_tracks = "all" if job.include_original_audio else "none"
        subtitle_tracks = "all" if job.include_original_subtitles and not job.overwrite_source_subtitles else "none"
        
        cmd.extend(["--audio-tracks", audio_tracks])
        cmd.extend(["--subtitle-tracks", subtitle_tracks])
        cmd.append(str(job.video_file))
    
    def _add_audio_track(self, cmd: List[str], track: Track) -> None:
        """
        Agrega una pista de audio con offset al comando.
        
        Args:
            cmd: Comando en construcción
            track: Pista de audio
        """
        audio_file = self._get_track_file(track)
        if not audio_file:
            return
        
        # Offset (en milisegundos)
        if track.offset_ms != 0:
            cmd.extend(["--sync", f"0:{track.offset_ms}"])
        
        # Idioma
        if track.language:
            cmd.extend(["--language", f"0:{track.language.value}"])
        
        # Título
        if track.title:
            cmd.extend(["--track-name", f"0:{track.title}"])
        
        # Default
        if track.is_default:
            cmd.extend(["--default-track", "0:yes"])
        
        # Archivo
        cmd.append(str(audio_file))
    
    def _add_subtitle_track(self, cmd: List[str], track: Track) -> None:
        """
        Agrega una pista de subtítulos con offset al comando.
        
        Args:
            cmd: Comando en construcción
            track: Pista de subtítulos
        """
        subtitle_file = self._get_track_file(track)
        if not subtitle_file:
            return
        
        # Offset (en milisegundos)
        if track.offset_ms != 0:
            cmd.extend(["--sync", f"0:{track.offset_ms}"])
        
        # Idioma
        if track.language:
            cmd.extend(["--language", f"0:{track.language.value}"])
        
        # Título
        if track.title:
            cmd.extend(["--track-name", f"0:{track.title}"])
        
        # Forced (letreros)
        if track.is_forced:
            cmd.extend(["--forced-display-flag", "0:1"])
        
        # Default
        if track.is_default:
            cmd.extend(["--default-track", "0:yes"])
        
        # Archivo
        cmd.append(str(subtitle_file))
    
    def _get_track_file(self, track: Track) -> Optional[Path]:
        """
        Obtiene el archivo asociado a una pista.
        
        Args:
            track: Pista
            
        Returns:
            Path del archivo o None
        """
        # Usar file_path si está disponible
        if track.file_path:
            return track.file_path if isinstance(track.file_path, Path) else Path(track.file_path)
        
        # Fallback: intentar con title (para compatibilidad con código antiguo)
        if track.title and Path(track.title).exists():
            return Path(track.title)
        
        return None
    
    def _parse_progress(self, line: str) -> Optional[int]:
        """
        Parsea una línea de MKVMerge para extraer el progreso.
        
        MKVMerge reporta: Progress: XX%
        
        Args:
            line: Línea de salida de MKVMerge
            
        Returns:
            Progreso (0-100) o None
        """
        match = re.search(r'Progress:\s+(\d+)%', line)
        if match:
            return int(match.group(1))
        return None
    
    def _parse_version(self, version_output: str) -> Optional[str]:
        """
        Parsea la versión de MKVMerge.
        
        Args:
            version_output: Salida de mkvmerge --version
            
        Returns:
            String con la versión
        """
        # Parsear: mkvmerge v70.0.0
        match = re.search(r'mkvmerge v(\d+\.\d+\.\d+)', version_output)
        if match:
            return match.group(1)
        return None
    
    def supports_audio_offset(self) -> bool:
        """
        Verifica si MKVMerge soporta offsets de audio.
        
        Returns:
            True - MKVMerge SÍ soporta offsets de audio
        """
        return True
    
    def supports_subtitle_offset(self) -> bool:
        """
        Verifica si MKVMerge soporta offsets de subtítulos.
        
        Returns:
            True - MKVMerge SÍ soporta offsets de subtítulos
        """
        return True
    
    def __str__(self) -> str:
        """Representación legible"""
        version = self.get_version()
        return f"MKVMergeEngine(v{version})" if version else "MKVMergeEngine"
