"""
Main Window - PyQt6

Ventana principal de la aplicación.
Refactorizada para usar el nuevo core y estructura limpia.
"""
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PyQt6.QtGui import QFont
from pathlib import Path

# Importar servicios del core
from core.services import RemuxService, EpisodeMatcher

# Importar tabs
from .tabs.assembler_tab import AssemblerTab
from .tabs.dual_sync_tab import DualSyncTab


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación.
    
    Usa el nuevo core refactorizado y sigue el patrón de separación de capas.
    """
    
    def __init__(self):
        super().__init__()
        
        # Crear servicios del core (Dependency Injection)
        self.remux_service = RemuxService()
        self.matcher = EpisodeMatcher()
        
        self._setup_window()
        self._load_stylesheet()
        self._build_ui()
    
    def _setup_window(self):
        """Configura la ventana"""
        self.setWindowTitle("Remuxeador FFmpeg v2.0 - DualSync & Advanced")
        self.setMinimumSize(1920, 1080)
        self.resize(1920, 1080)
    
    def _load_stylesheet(self):
        """Carga el tema oscuro"""
        try:
            qss_path = Path(__file__).parent / "styles" / "dark_theme.qss"
            if qss_path.exists():
                with open(qss_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            else:
                print(f"⚠️ Stylesheet no encontrado: {qss_path}")
        except Exception as e:
            print(f"⚠️ No se pudo cargar stylesheet: {e}")
    
    def _build_ui(self):
        """Construye la interfaz"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # TabWidget
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.tab_widget)
        
        # Crear tabs
        self._create_tabs()
    
    def _create_tabs(self):
        """Crea las pestañas"""
        # DualSync (modo dual JP + LAT) - Usa ViewModel
        from presentation.qt.viewmodels import DualSyncViewModel
        dualsync_viewmodel = DualSyncViewModel(self.remux_service, self.matcher)
        self.dual_sync_tab = DualSyncTab(dualsync_viewmodel)
        self.tab_widget.addTab(self.dual_sync_tab, "🔀 DualSync")
        
        # Assembler (ensamblar video con pistas externas) - Usa ViewModel
        from presentation.qt.viewmodels import AssemblerViewModel
        assembler_viewmodel = AssemblerViewModel(self.remux_service)
        self.assembler_tab = AssemblerTab(assembler_viewmodel)
        self.tab_widget.addTab(self.assembler_tab, "🔧 Assembler")
    
    def get_remux_service(self):
        """Obtiene el servicio de remuxeo"""
        return self.remux_service
    
    def get_matcher(self):
        """Obtiene el matcher de episodios"""
        return self.matcher
