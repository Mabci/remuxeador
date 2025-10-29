"""
Remux Worker - Worker para remuxeo individual

Ejecuta remuxeo en thread separado sin bloquear la UI.
"""
from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path

from core.services import RemuxService
from core.domain.models import RemuxJob


class RemuxWorker(QThread):
    """
    Worker para ejecutar remuxeo en thread separado.
    
    Sigue el patrón Worker de PyQt6 para threading limpio.
    """
    
    # Signals
    progress = pyqtSignal(int)  # Progreso 0-100
    status = pyqtSignal(str)  # Mensaje de estado
    finished = pyqtSignal(bool, str)  # (success, message/error)
    log = pyqtSignal(str, str)  # (mensaje, nivel)
    
    def __init__(self, job: RemuxJob, remux_service: RemuxService):
        """
        Inicializa el worker.
        
        Args:
            job: Trabajo de remuxeo a ejecutar
            remux_service: Servicio de remuxeo
        """
        super().__init__()
        self.job = job
        self.remux_service = remux_service
        self._is_cancelled = False
    
    def run(self):
        """Ejecuta el remuxeo en el thread"""
        try:
            self.log.emit("🚀 Iniciando remuxeo...", "info")
            self.status.emit("Remuxeando...")
            
            # Callback de progreso
            def progress_callback(progress_value: int):
                if not self._is_cancelled:
                    self.progress.emit(progress_value)
            
            # Ejecutar remuxeo
            result = self.remux_service.remux(self.job, progress_callback)
            
            # Verificar si fue cancelado
            if self._is_cancelled:
                self.log.emit("⚠️ Remuxeo cancelado", "warning")
                self.finished.emit(False, "Cancelado por el usuario")
                return
            
            # Emitir resultado
            if result.success:
                self.log.emit(f"✅ Remuxeo completado: {result.output_file}", "success")
                self.finished.emit(True, str(result.output_file))
            else:
                self.log.emit(f"❌ Error: {result.error_message}", "error")
                self.finished.emit(False, result.error_message or "Error desconocido")
        
        except Exception as e:
            self.log.emit(f"❌ Excepción: {str(e)}", "error")
            self.finished.emit(False, str(e))
    
    def cancel(self):
        """Cancela el remuxeo"""
        self._is_cancelled = True
        self.log.emit("⏹️ Cancelando...", "warning")
