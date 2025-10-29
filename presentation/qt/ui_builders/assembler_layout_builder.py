"""
Assembler Layout Builder - Constructor de layouts para AssemblerTab

Usa layouts profesionales, widgets reutilizables y principios de diseño
para crear una UI responsive y de nivel profesional.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from dataclasses import dataclass

from ..layouts.base_layout_builder import BaseLayoutBuilder
from ..layouts.layout_factory import LayoutFactory
from ..widgets import FileInputGroup, PreviewPanel, SyncControls, ConsoleLog, ProgressPanel


@dataclass
class AssemblerWidgets:
    """Contenedor de widgets del AssemblerTab"""
    # Selectores de archivos
    video_input: FileInputGroup
    audio_input: FileInputGroup
    subtitle_input: FileInputGroup
    forced_input: FileInputGroup
    output_input: FileInputGroup
    
    # Escaneo (modo carpetas)
    scan_btn: QPushButton
    episode_combo: QComboBox
    
    # Preview
    preview_panel: PreviewPanel
    load_preview_btn: QPushButton
    
    # Selectores de pistas
    audio_track_combo: QComboBox
    subtitle_track_combo: QComboBox
    
    # Widgets reutilizables
    sync_controls: SyncControls
    console: ConsoleLog
    progress_panel: ProgressPanel


class AssemblerLayoutBuilder(BaseLayoutBuilder):
    """
    Constructor de layouts para AssemblerTab.
    
    Estructura:
    - Header: Selectores de archivos (video, audio, subtítulos, forced, output)
    - Main: Preview + Controles + Track Lists
    - Footer: SyncControls + Console + Progress
    """
    
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.widgets = None
    
    def build_widgets(self) -> AssemblerWidgets:
        """
        Construye todos los widgets y retorna el contenedor.
        
        Returns:
            AssemblerWidgets con referencias a todos los widgets
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
        
        # Primera fila: Video y Output
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(self.theme.get_spacing('lg'))
        
        self.video_input = FileInputGroup(
            label_text="Video:",
            file_filter="Videos (*.mkv *.mp4 *.avi);;Todos (*.*)",
            placeholder="Selecciona el video base..."
        )
        row1_layout.addWidget(self.video_input, stretch=1)
        
        self.output_input = FileInputGroup(
            label_text="Salida:",
            file_filter="Matroska (*.mkv);;Todos (*.*)",
            placeholder="Archivo de salida...",
            is_save_dialog=True
        )
        row1_layout.addWidget(self.output_input, stretch=1)
        
        header_layout.addLayout(row1_layout)
        
        # Segunda fila: Pistas externas
        # Crear widgets primero
        self.audio_input = FileInputGroup(
            label_text="Audio:",
            file_filter="Audio (*.aac *.ac3 *.eac3 *.flac *.opus *.mka);;Todos (*.*)",
            placeholder="Audio externo en español latino (opcional)..."
        )
        
        self.subtitle_input = FileInputGroup(
            label_text="Subtítulos:",
            file_filter="Subtítulos (*.srt *.ass *.ssa);;Todos (*.*)",
            placeholder="Subtítulos externos en español latino (opcional)..."
        )
        
        self.forced_input = FileInputGroup(
            label_text="Letreros:",
            file_filter="Subtítulos (*.srt *.ass *.ssa);;Todos (*.*)",
            placeholder="Letreros/Forced subtitles (opcional)..."
        )
        
        # Crear group box con widgets
        external_group = self.factory.create_group_box(
            "Pistas Externas (Opcionales)",
            widgets=[self.audio_input, self.subtitle_input, self.forced_input]
        )
        header_layout.addWidget(external_group)
        
        # Tercera fila: Escaneo de episodios (modo carpetas)
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
        """Crea la sección principal con preview y controles"""
        main_widget = QWidget()
        
        # Usar splitter para áreas redimensionables
        splitter = self.factory.create_splitter(
            widgets=[
                self._create_left_panel(),
                self._create_right_panel()
            ],
            orientation=Qt.Orientation.Horizontal,
            stretch_factors=[3, 2]  # 60% / 40%
        )
        
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(splitter)
        
        return main_widget
    
    def _create_left_panel(self) -> QWidget:
        """Crea el panel izquierdo con preview"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(self.theme.get_spacing('md'))
        
        # Botón de cargar preview
        self.load_preview_btn = QPushButton("📺 Cargar Preview")
        self.load_preview_btn.setStyleSheet(self.theme.get_button_style('primary'))
        self.load_preview_btn.setMinimumHeight(35)
        left_layout.addWidget(self.load_preview_btn)
        
        # Preview panel
        self.preview_panel = PreviewPanel(
            title="Preview del Video",
            show_mute=False,
            min_width=500,
            min_height=350
        )
        left_layout.addWidget(self.preview_panel, stretch=1)
        
        return left_widget
    
    def _create_right_panel(self) -> QWidget:
        """Crea el panel derecho con selectores de pistas"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(self.theme.get_spacing('md'))
        
        # Grupo de pistas de audio
        from PyQt6.QtWidgets import QLabel
        audio_label = QLabel("Seleccionar pista para preview:")
        audio_label.setStyleSheet(self.theme.get_label_style('secondary'))
        
        self.audio_track_combo = QComboBox()
        self.audio_track_combo.setStyleSheet(self.theme.get_combo_box_style())
        self.audio_track_combo.addItem("Sin audio")
        
        audio_group = self.factory.create_group_box(
            "🎵 Pista de Audio",
            widgets=[audio_label, self.audio_track_combo]
        )
        right_layout.addWidget(audio_group)
        
        # Grupo de pistas de subtítulos
        subtitle_label = QLabel("Seleccionar pista para preview:")
        subtitle_label.setStyleSheet(self.theme.get_label_style('secondary'))
        
        self.subtitle_track_combo = QComboBox()
        self.subtitle_track_combo.setStyleSheet(self.theme.get_combo_box_style())
        self.subtitle_track_combo.addItem("Sin subtítulos")
        
        subtitle_group = self.factory.create_group_box(
            "📝 Pista de Subtítulos",
            widgets=[subtitle_label, self.subtitle_track_combo]
        )
        right_layout.addWidget(subtitle_group)
        
        # Agregar stretch para empujar hacia arriba
        right_layout.addStretch()
        
        return right_widget
    
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
        self.widgets = AssemblerWidgets(
            video_input=self.video_input,
            audio_input=self.audio_input,
            subtitle_input=self.subtitle_input,
            forced_input=self.forced_input,
            output_input=self.output_input,
            scan_btn=self.scan_btn,
            episode_combo=self.episode_combo,
            preview_panel=self.preview_panel,
            load_preview_btn=self.load_preview_btn,
            audio_track_combo=self.audio_track_combo,
            subtitle_track_combo=self.subtitle_track_combo,
            sync_controls=self.sync_controls,
            console=self.console,
            progress_panel=self.progress_panel
        )
