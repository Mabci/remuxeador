"""
Advanced Worker - Worker para remuxeo avanzado individual

Maneja remuxeo de archivos individuales con audios y subtitulos externos.
Usa RemuxJob del core.
"""
from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
from typing import Optional
from core.domain.models import RemuxJob
from core.services import RemuxService


class AdvancedWorker(QThread):
    """
    Worker para remuxeo individual avanzado.
    Ejecuta remuxeo usando RemuxService del core.
    """
    
    # Signals
    progress = pyqtSignal(int, str)  # (progreso_0_100, mensaje)
    finished = pyqtSignal(bool, str)  # (success, output_path_o_error)
    log = pyqtSignal(str, str)  # (mensaje, nivel)
    
    def __init__(self, job: RemuxJob, remux_service: RemuxService):
        super().__init__()
        self.job = job
        self.remux_service = remux_service
        self._is_cancelled = False
    
    def run(self):
        """Ejecuta el remuxeo individual"""
        try:
            self.log.emit("🎬 Iniciando remuxeo avanzado...", "info")
            
            # Validar job
            if not self.job.video_file.exists():
                self.log.emit(f"❌ Video no encontrado: {self.job.video_file}", "error")
                self.finished.emit(False, "Video no encontrado")
                return
            
            # Ejecutar remuxeo
            self.log.emit(f"📹 Video: {self.job.video_file.name}", "info")
            self.log.emit(f"🎵 Audios externos: {len(self.job.audio_tracks)}", "info")
            self.log.emit(f"📝 Subtítulos externos: {len(self.job.subtitle_tracks)}", "info")
            
            self.progress.emit(10, "Preparando remuxeo...")
            
            # Ejecutar usando el servicio
            success = self._execute_remux()
            
            if self._is_cancelled:
                self.log.emit("⚠️ Remuxeo cancelado", "warning")
                self.finished.emit(False, "Cancelado por el usuario")
                return
            
            if success:
                self.log.emit(f"✅ Remuxeo completado: {self.job.output_file}", "success")
                self.finished.emit(True, str(self.job.output_file))
            else:
                self.log.emit("❌ Remuxeo falló", "error")
                self.finished.emit(False, "El remuxeo falló")
        
        except Exception as e:
            self.log.emit(f"❌ Excepción: {str(e)}", "error")
            self.finished.emit(False, str(e))
    
    def _execute_remux(self) -> bool:
        """
        Ejecuta el remuxeo usando RemuxService.
        
        Returns:
            True si fue exitoso
        """
        try:
            self.progress.emit(30, "Ejecutando FFmpeg...")
            
            # Usar el servicio de remuxeo
            result = self.remux_service.remux_episode(self.job)
            
            if self._is_cancelled:
                return False
            
            self.progress.emit(90, "Finalizando...")
            
            if result.success:
                self.progress.emit(100, "Completado")
                return True
            else:
                self.log.emit(f"❌ Error: {result.error}", "error")
                return False
        
        except Exception as e:
            self.log.emit(f"❌ Error ejecutando remuxeo: {str(e)}", "error")
            return False
    
    def cancel(self):
        """Cancela el remuxeo"""
        self._is_cancelled = True
