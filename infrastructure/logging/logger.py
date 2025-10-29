"""
Logger - Sistema de logging centralizado

Sistema de logging usando el módulo logging de Python.
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Formatter con colores para consola"""
    
    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Formatea el registro con colores"""
        # Agregar color al nivel
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )
        
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_dir: Optional[Path] = None
) -> None:
    """
    Configura el sistema de logging.
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Si True, guarda logs en archivo
        log_to_console: Si True, muestra logs en consola
        log_dir: Directorio para archivos de log
    """
    # Obtener logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Formato de log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Handler de consola
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Usar formatter con colores
        console_formatter = ColoredFormatter(log_format, date_format)
        console_handler.setFormatter(console_formatter)
        
        root_logger.addHandler(console_handler)
    
    # Handler de archivo
    if log_to_file:
        if log_dir is None:
            log_dir = Path("logs")
        
        log_dir.mkdir(exist_ok=True)
        
        # Nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"remuxeador_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Archivo guarda todo
        
        # Formatter sin colores para archivo
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        
        root_logger.addHandler(file_handler)
        
        # Log inicial
        root_logger.info(f"Logging iniciado - Archivo: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con el nombre especificado.
    
    Args:
        name: Nombre del logger (usualmente __name__)
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


# Configuración por defecto al importar
def _auto_setup():
    """Configuración automática si no se ha configurado"""
    root_logger = logging.getLogger()
    
    # Solo configurar si no hay handlers
    if not root_logger.handlers:
        setup_logging(
            log_level="INFO",
            log_to_file=True,
            log_to_console=True
        )


# Auto-configurar al importar
_auto_setup()
