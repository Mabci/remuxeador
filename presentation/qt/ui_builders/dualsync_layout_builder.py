"""
DualSync Layout Builder - Constructor de layouts para DualSyncTab

Usa layouts profesionales con dual preview (JP y LAT lado a lado)
para sincronización de audio y subtítulos.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from dataclasses import dataclass

from ..layouts.base_layout_builder import BaseLayoutBuilder
from ..layouts.layout_factory import LayoutFactory
from ..widgets import FileInputGroup, SyncControls, ConsoleLog, ProgressPanel, DualPreviewControls
from ..widgets.simple_preview_panel import SimplePreviewPanel


@dataclass
class DualSyncWidgets:
    """Contenedor de widgets del DualSyncTab"""
    # Selectores de archivos
    jp_input: FileInputGroup
    lat_input: FileInputGroup
    output_input: FileInputGroup
    
    # Escaneo (modo carpetas)
    scan_btn: QPushButton
    episode_combo: QComboBox
    
    # Preview panels (sin controles individuales)
    preview_jp: SimplePreviewPanel
    preview_lat: SimplePreviewPanel
    load_preview_btn: QPushButton
    
    # Controles centralizados
    dual_controls: DualPreviewControls
    
    # Widgets reutilizables
    sync_controls: SyncControls
    console: ConsoleLog
    progress_panel: ProgressPanel


class DualSyncLayoutBuilder(BaseLayoutBuilder):
    """
    Constructor de layouts para DualSyncTab.
    
    Estructura:
    - Header: Selectores de archivos (JP, LAT, Output)
    - Main: Dual Preview (JP | LAT) con controles centrales
    - Footer: SyncControls + Console + Progress
    """
    
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.widgets = None
    
    def build_widgets(self) -> DualSyncWidgets:
        """
        Construye todos los widgets y retorna el contenedor.
        
        Returns:
            DualSyncWidgets con referencias a todos los widgets
        """
        # Construir el layout principal
        self.build()
        
        # Retornar widgets
        return self.widgets
    
    def create_header_section(self) -> QWidget:
        """Crea la sección de header con selectores de archivos"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(self.theme.get_spacing('md'))
        
        # Primera fila: Selectores JP, LAT y Output
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(self.theme.get_spacing('lg'))
        
        self.jp_input = FileInputGroup(
            label_text="JP:",
            file_filter="Videos (*.mkv *.mp4 *.avi);;Todos (*.*)",
            placeholder="Video japonés..."
        )
        row1_layout.addWidget(self.jp_input, stretch=1)
        
        self.lat_input = FileInputGroup(
            label_text="LAT:",
            file_filter="Videos (*.mkv *.mp4 *.avi);;Todos (*.*)",
            placeholder="Video latino..."
        )
        row1_layout.addWidget(self.lat_input, stretch=1)
        
        self.output_input = FileInputGroup(
            label_text="Salida:",
            file_filter="Matroska (*.mkv);;Todos (*.*)",
            placeholder="Archivo/Carpeta de salida...",
            is_save_dialog=True
        )
        row1_layout.addWidget(self.output_input, stretch=1)
        
        header_layout.addLayout(row1_layout)
        
        # Segunda fila: Escaneo de episodios (modo carpetas)
        scan_layout = QHBoxLayout()
        scan_layout.setSpacing(self.theme.get_spacing('md'))
        
        self.scan_btn = QPushButton("🔍 Escanear Carpetas")
        self.scan_btn.setStyleSheet(self.theme.get_button_style('primary'))
        self.scan_btn.setMinimumHeight(35)
        scan_layout.addWidget(self.scan_btn)
        
        from PyQt6.QtWidgets import QLabel
        ep_label = QLabel("Episodio:")
        ep_label.setStyleSheet(self.theme.get_label_style('primary'))
        scan_layout.addWidget(ep_label)
        
        self.episode_combo = QComboBox()
        self.episode_combo.setStyleSheet(self.theme.get_combo_box_style())
        self.episode_combo.setMinimumWidth(200)
        self.episode_combo.setMinimumHeight(35)
        scan_layout.addWidget(self.episode_combo)
        
        scan_layout.addStretch()
        
        header_layout.addLayout(scan_layout)
        
        return header_widget
    
    def create_main_section(self) -> QWidget:
        """Crea la sección principal con dual preview y controles centrales"""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(self.theme.get_spacing('md'))
        
        # Botón de cargar preview
        self.load_preview_btn = QPushButton("📺 Cargar Preview")
        self.load_preview_btn.setStyleSheet(self.theme.get_button_style('primary'))
        self.load_preview_btn.setMinimumHeight(35)
        main_layout.addWidget(self.load_preview_btn)
        
        # Dual preview (lado a lado)
        preview_layout = QHBoxLayout()
        preview_layout.setSpacing(self.theme.get_spacing('md'))
        
        # Preview JP (sin controles)
        self.preview_jp = SimplePreviewPanel(
            title="🇯🇵 Preview Japonés",
            min_width=400,
            min_height=300
        )
        preview_layout.addWidget(self.preview_jp, stretch=1)
        
        # Preview LAT (sin controles)
        self.preview_lat = SimplePreviewPanel(
            title="🌎 Preview Latino",
            min_width=400,
            min_height=300
        )
        preview_layout.addWidget(self.preview_lat, stretch=1)
        
        main_layout.addLayout(preview_layout, stretch=1)
        
        # Controles centralizados (en medio)
        self.dual_controls = DualPreviewControls()
        main_layout.addWidget(self.dual_controls)
        
        return main_widget
    
    
    def create_footer_section(self) -> QWidget:
        """Crea la sección de footer con sync, console y progreso"""
        footer_widget = QWidget()
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(self.theme.get_spacing('md'))
        
        # SyncControls
        self.sync_controls = SyncControls()
        footer_layout.addWidget(self.sync_controls)
        
        # Console
        self.console = ConsoleLog()
        footer_layout.addWidget(self.console)
        
        # Progress panel
        self.progress_panel = ProgressPanel(
            button_text="🎬 Remuxear",
            button_variant="success"
        )
        footer_layout.addWidget(self.progress_panel)
        
        return footer_widget
    
    def build(self):
        """Override del método build para guardar widgets"""
        # Llamar al build del padre
        super().build()
        
        # Crear el contenedor de widgets
        self.widgets = DualSyncWidgets(
            jp_input=self.jp_input,
            lat_input=self.lat_input,
            output_input=self.output_input,
            scan_btn=self.scan_btn,
            episode_combo=self.episode_combo,
            preview_jp=self.preview_jp,
            preview_lat=self.preview_lat,
            load_preview_btn=self.load_preview_btn,
            dual_controls=self.dual_controls,
            sync_controls=self.sync_controls,
            console=self.console,
            progress_panel=self.progress_panel
        )
