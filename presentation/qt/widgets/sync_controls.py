"""
Sync Controls Widget - PyQt6

Widget profesional para controles de sincronización de audio y subtítulos.
Usa layouts responsive y ThemeManager para estilos consistentes.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                              QLabel, QLineEdit, QPushButton, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class SyncControls(QWidget):
    """
    Widget de controles de sincronización.
    
    Proporciona controles para ajustar offsets de audio y subtítulos
    con botones de incremento/decremento y reset.
    
    Signals:
        offset_changed: Emitido cuando cambian los offsets (audio_ms, subtitle_ms)
    """
    
    # Signal emitido cuando cambian los offsets
    offset_changed = pyqtSignal(int, int)  # audio_offset_ms, subtitle_offset_ms
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_offset_ms = 0
        self.subtitle_offset_ms = 0
        self._build_ui()
        self._apply_theme()
    
    def _build_ui(self):
        """Construye la interfaz"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Audio (izquierda)
        audio_widget = self._create_sync_section(
            "Sincronización de Audio",
            self._adjust_audio
        )
        layout.addWidget(audio_widget, stretch=1)
        
        # Subtítulos (derecha)
        subtitle_widget = self._create_sync_section(
            "Sincronización de Subtítulos",
            self._adjust_subtitle
        )
        layout.addWidget(subtitle_widget, stretch=1)
    
    def _create_sync_section(self, title: str, callback):
        """Crea una sección de sincronización"""
        widget = QFrame()
        widget.setFrameShape(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        # Título
        title_label = QLabel(title)
        title_font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Offset actual
        offset_layout = QHBoxLayout()
        offset_layout.addWidget(QLabel("Offset:"))
        
        offset_entry = QLineEdit("0")
        offset_entry.setReadOnly(True)
        offset_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        offset_entry.setFixedWidth(90)
        offset_layout.addWidget(offset_entry)
        
        offset_layout.addWidget(QLabel("ms"))
        offset_layout.addStretch()
        layout.addLayout(offset_layout)
        
        # Guardar referencia al entry
        if title.startswith("Sincronización de Audio"):
            self.audio_entry = offset_entry
        else:
            self.subtitle_entry = offset_entry
        
        # Botones de ajuste (1 fila horizontal)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(4)
        
        adjustments = [
            ("-1s", -1000),
            ("-100ms", -100),
            ("-10ms", -10),
            ("Reset", 0),
            ("+10ms", 10),
            ("+100ms", 100),
            ("+1s", 1000)
        ]
        
        # Todos los botones en una sola fila
        for text, value in adjustments:
            btn = QPushButton(text)
            btn.setMinimumWidth(55)
            btn.setMaximumHeight(28)
            btn.setFont(QFont("Segoe UI", 8))
            btn.clicked.connect(lambda checked, v=value: callback(v))
            buttons_layout.addWidget(btn)
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def _adjust_audio(self, value: int):
        """Ajusta offset de audio"""
        if value == 0:
            self.audio_offset_ms = 0
        else:
            self.audio_offset_ms += value
        
        self.audio_entry.setText(str(self.audio_offset_ms))
        self.offset_changed.emit(self.audio_offset_ms, self.subtitle_offset_ms)
    
    def _adjust_subtitle(self, value: int):
        """Ajusta offset de subtítulos"""
        if value == 0:
            self.subtitle_offset_ms = 0
        else:
            self.subtitle_offset_ms += value
        
        self.subtitle_entry.setText(str(self.subtitle_offset_ms))
        self.offset_changed.emit(self.audio_offset_ms, self.subtitle_offset_ms)
    
    def get_audio_offset_ms(self) -> int:
        """Obtiene offset de audio en ms"""
        return self.audio_offset_ms
    
    def get_subtitle_offset_ms(self) -> int:
        """Obtiene offset de subtítulos en ms"""
        return self.subtitle_offset_ms
    
    def get_audio_offset_seconds(self) -> float:
        """Obtiene offset de audio en segundos"""
        return self.audio_offset_ms / 1000.0
    
    def get_subtitle_offset_seconds(self) -> float:
        """Obtiene offset de subtítulos en segundos"""
        return self.subtitle_offset_ms / 1000.0
    
    def _apply_theme(self):
        """Aplica el tema visual usando ThemeManager"""
        try:
            from ..layouts.theme_manager import ThemeManager
            theme = ThemeManager()
            
            # Aplicar estilo al widget principal
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {theme.get_color('bg_secondary')};
                    border: 1px solid {theme.get_color('border')};
                    border-radius: {theme.RADIUS['md']}px;
                }}
            """)
        except ImportError:
            # Si no está disponible ThemeManager, usar estilos básicos
            pass
