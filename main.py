"""
Punto de entrada principal - Remuxeador FFmpeg v2.0

Usa la nueva arquitectura refactorizada:
- core/ para lógica de negocio
- infrastructure/ para configuración
- presentation/ para UI (PyQt6)

REQUISITO OBLIGATORIO: MKVMerge debe estar instalado.
"""
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

# Configurar infraestructura
from infrastructure.config import get_settings
from infrastructure.logging import setup_logging

# Importar ventana principal (nueva estructura)
from presentation.qt import MainWindow

# Validación de herramientas
from core.engines import MKVMergeEngine


def validate_dependencies():
    """
    Valida que todas las dependencias obligatorias estén instaladas.
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    # Validar MKVMerge (OBLIGATORIO)
    try:
        mkvmerge = MKVMergeEngine()
        version = mkvmerge.get_version()
        print(f"✅ MKVMerge encontrado: v{version}")
        return True, ""
    except RuntimeError as e:
        error_msg = (
            "❌ MKVMerge NO está instalado\n\n"
            "Esta aplicación REQUIERE MKVMerge para funcionar.\n\n"
            "Por favor instala MKVMerge desde:\n"
            "https://mkvtoolnix.download/downloads.html\n\n"
            "Después de instalar, reinicia la aplicación."
        )
        return False, error_msg


def main():
    """Función principal"""
    # 1. Cargar configuración
    settings = get_settings()
    print(f"📁 Base dir: {settings.paths.base_dir}")
    
    # 2. Configurar logging
    setup_logging(
        log_level=settings.log_level,
        log_to_file=settings.log_to_file,
        log_to_console=settings.log_to_console,
        log_dir=settings.paths.logs_dir
    )
    
    # 3. Crear aplicación Qt (necesaria para mostrar mensajes)
    app = QApplication(sys.argv)
    app.setApplicationName("Remuxeador FFmpeg v2.0")
    app.setOrganizationName("Remuxeador")
    
    # 4. VALIDAR DEPENDENCIAS OBLIGATORIAS
    success, error_msg = validate_dependencies()
    if not success:
        print(error_msg)
        QMessageBox.critical(
            None,
            "Error: MKVMerge no encontrado",
            error_msg
        )
        sys.exit(1)
    
    # 5. Crear y mostrar ventana principal
    # MainWindow ahora crea sus propios servicios (Dependency Injection)
    window = MainWindow()
    window.show()
    
    # 6. Ejecutar aplicación
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
