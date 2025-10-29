"""
Base ViewModel - Clase base para todos los ViewModels

Implementa el patrón MVVM separando completamente la lógica de la UI.
"""
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Optional

from core.services import RemuxService


class BaseViewModel(QObject):
    """
    Clase base para todos los ViewModels.
    
    Proporciona signals comunes y funcionalidad compartida.
    Sigue el patrón MVVM: separa lógica de presentación de la UI.
    """
    
    # Signals comunes que todas las Views pueden usar
    progress_changed = pyqtSignal(int)  # Progreso 0-100
    status_changed = pyqtSignal(str)  # Mensaje de estado
    error_occurred = pyqtSignal(str)  # Mensaje de error
    completed = pyqtSignal(bool)  # True si exitoso, False si falló
    log_message = pyqtSignal(str, str)  # (mensaje, nivel: info/success/error/warning)
    
    def __init__(self, remux_service: RemuxService):
        """
        Inicializa el ViewModel base.
        
        Args:
            remux_service: Servicio de remuxeo del core
        """
        super().__init__()
        self.remux_service = remux_service
        self._is_busy = False
    
    @property
    def is_busy(self) -> bool:
        """Indica si el ViewModel está ocupado procesando"""
        return self._is_busy
    
    def _set_busy(self, busy: bool):
        """Establece el estado de ocupado"""
        self._is_busy = busy
    
    def emit_progress(self, value: int):
        """
        Emite cambio de progreso.
        
        Args:
            value: Progreso 0-100
        """
        self.progress_changed.emit(max(0, min(100, value)))
    
    def emit_status(self, message: str):
        """
        Emite cambio de estado.
        
        Args:
            message: Mensaje de estado
        """
        self.status_changed.emit(message)
    
    def emit_error(self, error: str):
        """
        Emite un error.
        
        Args:
            error: Mensaje de error
        """
        self.error_occurred.emit(error)
        self.log(error, "error")
    
    def emit_completed(self, success: bool):
        """
        Emite señal de completado.
        
        Args:
            success: True si fue exitoso
        """
        self.completed.emit(success)
        self._set_busy(False)
    
    def log(self, message: str, level: str = "info"):
        """
        Emite un mensaje de log.
        
        Args:
            message: Mensaje a loguear
            level: Nivel (info, success, error, warning)
        """
        self.log_message.emit(message, level)
    
    def reset(self):
        """Resetea el estado del ViewModel"""
        self._set_busy(False)
        self.emit_progress(0)
        self.emit_status("")
    
    def __str__(self) -> str:
        """Representación legible"""
        return f"{self.__class__.__name__}(busy={self.is_busy})"
