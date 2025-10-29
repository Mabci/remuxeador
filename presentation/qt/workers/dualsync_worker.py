"""
DualSync Worker - Worker para remuxeo dual (JP + LAT)

Maneja remuxeo individual y por lotes en thread separado.
Usa DualVideoService con MKVMerge (arquitectura SOLID).
"""
from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
from typing import Dict, Optional
import config

from core.services import DualVideoService
from core.domain import DualVideoRemuxJob, LanguageCode


class DualSyncSingleWorker(QThread):
    """
    Worker para remuxeo individual de un video dual.
    Usa DualVideoService con arquitectura SOLID.
    """
    
    # Signals
    progress = pyqtSignal(int, str)  # (progreso_0_100, mensaje)
    finished = pyqtSignal(bool, str)  # (success, output_path_o_error)
    log = pyqtSignal(str, str)  # (mensaje, nivel)
    
    def __init__(self, dual_video_service: DualVideoService, video_jp: str, video_lat: str, 
                 output: str, audio_offset_ms: int, subtitle_offset_ms: int):
        super().__init__()
        self.dual_video_service = dual_video_service
        self.video_jp = Path(video_jp)
        self.video_lat = Path(video_lat)
        self.output = Path(output)
        self.audio_offset_ms = audio_offset_ms
        self.subtitle_offset_ms = subtitle_offset_ms
        self._is_cancelled = False
    
    def run(self):
        """Ejecuta el remuxeo individual"""
        try:
            self.log.emit("🎬 Iniciando remuxeo dual...", "info")
            
            # Crear job de remuxeo dual
            job = DualVideoRemuxJob(
                video_primary=self.video_jp,
                video_secondary=self.video_lat,
                output_file=self.output,
                audio_offset_ms=self.audio_offset_ms,
                subtitle_offset_ms=self.subtitle_offset_ms,
                primary_audio_language=LanguageCode.JAPANESE,
                primary_audio_title=config.DEFAULT_AUDIO_JP_TITLE,
                secondary_audio_language=LanguageCode.SPANISH_LATIN,
                secondary_audio_title=config.DEFAULT_AUDIO_LAT_TITLE
            )
            
            self.log.emit(f"📹 Video JP: {self.video_jp.name}", "info")
            self.log.emit(f"📹 Video LAT: {self.video_lat.name}", "info")
            if self.audio_offset_ms != 0:
                self.log.emit(f"⏱️ Offset de audio: {self.audio_offset_ms}ms", "info")
            
            # Ejecutar remuxeo con callback de progreso
            result = self.dual_video_service.remux_dual(
                job,
                progress_callback=self._on_progress
            )
            
            if self._is_cancelled:
                self.log.emit("⚠️ Remuxeo cancelado", "warning")
                self.finished.emit(False, "Cancelado por el usuario")
                return
            
            if result.success:
                self.log.emit(f"✅ Remuxeo completado: {self.output.name}", "success")
                self.finished.emit(True, str(self.output))
            else:
                error_msg = result.error_message or "El remuxeo falló"
                self.log.emit(f"❌ Remuxeo falló: {error_msg}", "error")
                self.finished.emit(False, error_msg)
        
        except Exception as e:
            self.log.emit(f"❌ Excepción: {str(e)}", "error")
            self.finished.emit(False, str(e))
    
    def _on_progress(self, progress: int):
        """Callback de progreso"""
        if not self._is_cancelled:
            self.progress.emit(progress, f"Procesando... {progress}%")
    
    def cancel(self):
        """Cancela el remuxeo"""
        self._is_cancelled = True


class DualSyncBatchWorker(QThread):
    """
    Worker para procesamiento por lotes de videos duales.
    Usa DualVideoService con arquitectura SOLID.
    """
    
    # Signals
    progress = pyqtSignal(int, str)  # (progreso_0_100, mensaje)
    episode_completed = pyqtSignal(int, bool, str)  # (ep_num, success, output/error)
    finished = pyqtSignal(list)  # Lista de resultados
    log = pyqtSignal(str, str)  # (mensaje, nivel)
    
    def __init__(self, dual_video_service: DualVideoService, episodes: Dict[int, Dict[str, str]], 
                 output_folder: str, audio_offset_ms: int, subtitle_offset_ms: int):
        super().__init__()
        self.dual_video_service = dual_video_service
        self.episodes = episodes
        self.output_folder = Path(output_folder)
        self.audio_offset_ms = audio_offset_ms
        self.subtitle_offset_ms = subtitle_offset_ms
        self._is_cancelled = False
    
    def run(self):
        """Ejecuta el procesamiento por lotes"""
        results = []
        total = len(self.episodes)
        
        self.log.emit(f"🚀 Iniciando procesamiento de {total} episodios...", "info")
        
        for idx, (ep_num, ep_data) in enumerate(sorted(self.episodes.items()), 1):
            if self._is_cancelled:
                self.log.emit("⚠️ Procesamiento cancelado", "warning")
                break
            
            video_jp = ep_data.get('jp')
            video_lat = ep_data.get('lat')
            
            if not video_jp or not video_lat:
                self.log.emit(f"⚠️ Episodio {ep_num}: Faltan archivos", "warning")
                results.append({'episode': ep_num, 'success': False, 'error': 'Faltan archivos'})
                self.episode_completed.emit(ep_num, False, 'Faltan archivos')
                continue
            
            output_path = self.output_folder / f"Episode_{ep_num:02d}_REMUX.mkv"
            
            self.log.emit(f"📺 Procesando Episodio {ep_num:02d}...", "info")
            
            # Calcular progreso general
            overall_progress = int((idx - 1) / total * 100)
            self.progress.emit(overall_progress, f"Episodio {ep_num:02d}/{total}")
            
            try:
                # Crear job de remuxeo dual
                job = DualVideoRemuxJob(
                    video_primary=Path(video_jp),
                    video_secondary=Path(video_lat),
                    output_file=output_path,
                    audio_offset_ms=self.audio_offset_ms,
                    subtitle_offset_ms=self.subtitle_offset_ms,
                    primary_audio_language=LanguageCode.JAPANESE,
                    primary_audio_title=config.DEFAULT_AUDIO_JP_TITLE,
                    secondary_audio_language=LanguageCode.SPANISH,
                    secondary_audio_title=config.DEFAULT_AUDIO_LAT_TITLE
                )
                
                # Ejecutar remuxeo
                result = self.dual_video_service.remux_dual(job)
                
                if result.success:
                    self.log.emit(f"✅ Episodio {ep_num:02d} completado", "success")
                    results.append({'episode': ep_num, 'success': True, 'file': output_path.name})
                    self.episode_completed.emit(ep_num, True, str(output_path))
                else:
                    error_msg = result.error_message or 'Remuxeo falló'
                    self.log.emit(f"❌ Episodio {ep_num:02d} falló: {error_msg}", "error")
                    results.append({'episode': ep_num, 'success': False, 'error': error_msg})
                    self.episode_completed.emit(ep_num, False, error_msg)
            
            except Exception as e:
                self.log.emit(f"❌ Episodio {ep_num:02d}: {str(e)}", "error")
                results.append({'episode': ep_num, 'success': False, 'error': str(e)})
                self.episode_completed.emit(ep_num, False, str(e))
        
        self.finished.emit(results)
        
        success_count = sum(1 for r in results if r.get('success'))
        self.log.emit(f"✅ Completado: {success_count}/{total} exitosos", "success")
    
    def cancel(self):
        """Cancela el procesamiento"""
        self._is_cancelled = True
