"""
Batch Worker - Worker para procesamiento por lotes

Ejecuta procesamiento de múltiples episodios en thread separado.
"""
from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
from typing import Dict

from core.services import BatchService
from core.domain.models import Episode


class BatchWorker(QThread):
    """
    Worker para ejecutar procesamiento por lotes en thread separado.
    
    Procesa múltiples episodios sin bloquear la UI.
    """
    
    # Signals
    progress = pyqtSignal(int, int, str)  # (episodio_num, progreso_0_100, mensaje)
    episode_completed = pyqtSignal(int, bool, str)  # (episodio_num, success, output/error)
    finished = pyqtSignal(int, int, int)  # (total, exitosos, fallidos)
    log = pyqtSignal(str, str)  # (mensaje, nivel)
    
    def __init__(
        self,
        batch_service: BatchService,
        directory: Path,
        output_directory: Path,
        audio_offset_ms: int = 0,
        subtitle_offset_ms: int = 0
    ):
        """
        Inicializa el worker de batch.
        
        Args:
            batch_service: Servicio de procesamiento por lotes
            directory: Directorio con archivos
            output_directory: Directorio de salida
            audio_offset_ms: Offset de audio
            subtitle_offset_ms: Offset de subtítulos
        """
        super().__init__()
        self.batch_service = batch_service
        self.directory = directory
        self.output_directory = output_directory
        self.audio_offset_ms = audio_offset_ms
        self.subtitle_offset_ms = subtitle_offset_ms
        self._is_cancelled = False
    
    def run(self):
        """Ejecuta el procesamiento por lotes"""
        try:
            self.log.emit("🚀 Iniciando procesamiento por lotes...", "info")
            
            # Callback de progreso
            def progress_callback(ep_num: int, progress_value: int, message: str):
                if not self._is_cancelled:
                    self.progress.emit(ep_num, progress_value, message)
            
            # Ejecutar batch
            result = self.batch_service.process_directory(
                directory=self.directory,
                output_directory=self.output_directory,
                audio_offset_ms=self.audio_offset_ms,
                subtitle_offset_ms=self.subtitle_offset_ms,
                progress_callback=progress_callback
            )
            
            # Verificar si fue cancelado
            if self._is_cancelled:
                self.log.emit("⚠️ Procesamiento cancelado", "warning")
                return
            
            # Emitir resultados individuales
            for ep_result in result.results:
                ep_num = ep_result.get('episode', 0)
                success = ep_result.get('success', False)
                output_or_error = ep_result.get('output') if success else ep_result.get('error', 'Error desconocido')
                self.episode_completed.emit(ep_num, success, output_or_error)
            
            # Emitir resultado final
            self.log.emit(
                f"✅ Procesamiento completado: {result.successful}/{result.total_episodes} exitosos",
                "success" if result.successful > 0 else "warning"
            )
            self.finished.emit(result.total_episodes, result.successful, result.failed)
        
        except Exception as e:
            self.log.emit(f"❌ Excepción: {str(e)}", "error")
            self.finished.emit(0, 0, 1)
    
    def cancel(self):
        """Cancela el procesamiento"""
        self._is_cancelled = True
        self.log.emit("⏹️ Cancelando procesamiento...", "warning")
