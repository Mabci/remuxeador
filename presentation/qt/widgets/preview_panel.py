"""
Preview Panel - Panel de preview con controles integrados

Widget especializado que encapsula un frame de preview con controles
de navegación y playback integrados, siguiendo principios de diseño profesional.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
                              QLabel, QPushButton, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from typing import Optional


class PreviewPanel(QWidget):
    """
    Panel de preview con controles integrados.
    
    Proporciona:
    - Frame para preview de video (MPV se incrusta aquí)
    - Label de tiempo
    - Botones de navegación (-10s, -1s, +1s, +10s)
    - Botones de playback (play/pause, stop)
    - Botones de mute (opcional)
    
    Signals:
        play_clicked: Emitido cuando se hace click en play/pause
        stop_clicked: Emitido cuando se hace click en stop
        seek_requested: Emitido cuando se solicita navegación (segundos)
        mute_clicked: Emitido cuando se hace click en mute
    """
    
    # Signals
    play_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    seek_requested = pyqtSignal(float)  # Segundos a navegar (+ o -)
    mute_clicked = pyqtSignal()
    
    def __init__(
        self,
        title: str = "Preview",
        show_mute: bool = False,
        min_width: int = 400,
        min_height: int = 300,
        parent: Optional[QWidget] = None
    ):
        """
        Inicializa el panel de preview.
        
        Args:
            title: Título del panel
            show_mute: Si True, muestra botón de mute
            min_width: Ancho mínimo del preview
            min_height: Alto mínimo del preview
            parent: Widget padre
        """
        super().__init__(parent)
        
        self.title = title
        self.show_mute = show_mute
        self.min_width = min_width
        self.min_height = min_height
        
        self._build_ui()
        self._connect_signals()
        self._apply_theme()
    
    def _build_ui(self):
        """Construye la interfaz del widget"""
        # Layout principal vertical
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        # Título
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        self.title_label = title_label
        
        # Frame de preview (aquí se incrustará MPV)
        self.preview_frame = QFrame()
        self.preview_frame.setMinimumSize(self.min_width, self.min_height)
        self.preview_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self.preview_frame)
        
        # Label de tiempo
        self.time_label = QLabel("00:00:00 / 00:00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.time_label)
        
        # Controles de navegación
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(4)
        
        self.btn_minus10 = QPushButton("◀◀ -10s")
        self.btn_minus1 = QPushButton("◀ -1s")
        self.btn_plus1 = QPushButton("+1s ▶")
        self.btn_plus10 = QPushButton("+10s ▶▶")
        
        nav_layout.addWidget(self.btn_minus10)
        nav_layout.addWidget(self.btn_minus1)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_plus1)
        nav_layout.addWidget(self.btn_plus10)
        
        main_layout.addLayout(nav_layout)
        
        # Controles de playback
        playback_layout = QHBoxLayout()
        playback_layout.setSpacing(8)
        
        self.btn_play = QPushButton("▶")
        self.btn_play.setFixedSize(60, 40)
        
        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setFixedSize(60, 40)
        
        playback_layout.addStretch()
        playback_layout.addWidget(self.btn_play)
        playback_layout.addWidget(self.btn_stop)
        
        # Botón de mute (opcional)
        if self.show_mute:
            self.btn_mute = QPushButton("🔊 Mute")
            self.btn_mute.setFixedWidth(80)
            playback_layout.addWidget(self.btn_mute)
        
        playback_layout.addStretch()
        
        main_layout.addLayout(playback_layout)
    
    def _connect_signals(self):
        """Conecta los signals internos"""
        # Navegación
        self.btn_minus10.clicked.connect(lambda: self.seek_requested.emit(-10))
        self.btn_minus1.clicked.connect(lambda: self.seek_requested.emit(-1))
        self.btn_plus1.clicked.connect(lambda: self.seek_requested.emit(1))
        self.btn_plus10.clicked.connect(lambda: self.seek_requested.emit(10))
        
        # Playback
        self.btn_play.clicked.connect(self.play_clicked.emit)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)
        
        # Mute
        if self.show_mute:
            self.btn_mute.clicked.connect(self.mute_clicked.emit)
    
    def _apply_theme(self):
        """Aplica el tema visual"""
        from ..layouts.theme_manager import ThemeManager
        theme = ThemeManager()
        
        # Título
        self.title_label.setFont(theme.get_font('subtitle'))
        self.title_label.setStyleSheet(theme.get_label_style('primary'))
        
        # Frame de preview (negro para video)
        self.preview_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border: 2px solid {theme.get_color('border')};
                border-radius: {theme.RADIUS['md']}px;
            }}
        """)
        
        # Label de tiempo
        self.time_label.setFont(theme.get_font('mono'))
        self.time_label.setStyleSheet(theme.get_label_style('secondary'))
        
        # Botones de navegación
        nav_button_style = theme.get_button_style('secondary')
        self.btn_minus10.setStyleSheet(nav_button_style)
        self.btn_minus1.setStyleSheet(nav_button_style)
        self.btn_plus1.setStyleSheet(nav_button_style)
        self.btn_plus10.setStyleSheet(nav_button_style)
        
        # Botón play (verde)
        self.btn_play.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.get_color('success')};
                color: {theme.get_color('text_primary')};
                border: 1px solid {theme.get_color('border')};
                border-radius: {theme.RADIUS['md']}px;
                font-size: 18pt;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('success_hover')};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('success')};
            }}
        """)
        
        # Botón stop (rojo)
        self.btn_stop.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.get_color('error')};
                color: {theme.get_color('text_primary')};
                border: 1px solid {theme.get_color('border')};
                border-radius: {theme.RADIUS['md']}px;
                font-size: 18pt;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('error_hover')};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('error')};
            }}
        """)
        
        # Botón mute
        if self.show_mute:
            self.btn_mute.setStyleSheet(theme.get_button_style('secondary'))
    
    # === API PÚBLICA ===
    
    def get_preview_frame(self) -> QFrame:
        """
        Obtiene el frame de preview para incrustar MPV.
        
        Returns:
            QFrame donde se puede incrustar el player
        """
        return self.preview_frame
    
    def set_time(self, current: str, total: str):
        """
        Actualiza el label de tiempo.
        
        Args:
            current: Tiempo actual (formato: "HH:MM:SS")
            total: Tiempo total (formato: "HH:MM:SS")
        """
        self.time_label.setText(f"{current} / {total}")
    
    def set_play_text(self, text: str):
        """
        Actualiza el texto del botón play.
        
        Args:
            text: Texto a mostrar (ej: "▶" o "⏸")
        """
        self.btn_play.setText(text)
    
    def set_mute_text(self, text: str):
        """
        Actualiza el texto del botón mute.
        
        Args:
            text: Texto a mostrar (ej: "🔊 Mute" o "🔇 Unmute")
        """
        if self.show_mute:
            self.btn_mute.setText(text)
    
    def set_controls_enabled(self, enabled: bool):
        """
        Habilita/deshabilita todos los controles.
        
        Args:
            enabled: True para habilitar
        """
        self.btn_minus10.setEnabled(enabled)
        self.btn_minus1.setEnabled(enabled)
        self.btn_plus1.setEnabled(enabled)
        self.btn_plus10.setEnabled(enabled)
        self.btn_play.setEnabled(enabled)
        self.btn_stop.setEnabled(enabled)
        if self.show_mute:
            self.btn_mute.setEnabled(enabled)
