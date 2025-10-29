"""
Simple Preview Panel - Panel de preview sin controles

Widget simplificado solo con el frame de preview y botón de mute,
para usar en dual preview donde los controles están centralizados.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QFont


class SimplePreviewPanel(QWidget):
    """
    Panel de preview simplificado sin controles de playback.
    
    Características:
    - Frame para incrustar MPV
    - Título del preview
    - Botón de mute
    - Sin controles de navegación/playback (están centralizados)
    
    Signals:
        mute_clicked: Usuario presionó mute
    """
    
    # Signals
    mute_clicked = pyqtSignal()
    
    def __init__(self, title: str = "Preview", min_width: int = 400, min_height: int = 300, parent=None):
        super().__init__(parent)
        self.title = title
        self.min_width = min_width
        self.min_height = min_height
        self._setup_ui()
        self._apply_theme()
    
    def _setup_ui(self):
        """Configura la UI del widget"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        # === HEADER ===
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Título
        self.title_label = QLabel(self.title)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Botón de mute
        self.mute_btn = QPushButton("🔊 Mute")
        self.mute_btn.setMinimumSize(80, 30)
        self.mute_btn.clicked.connect(self.mute_clicked.emit)
        header_layout.addWidget(self.mute_btn)
        
        main_layout.addLayout(header_layout)
        
        # === PREVIEW FRAME ===
        self.preview_frame = QFrame()
        self.preview_frame.setMinimumSize(self.min_width, self.min_height)
        self.preview_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_frame.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(self.preview_frame, stretch=1)
    
    def _apply_theme(self):
        """Aplica el tema visual"""
        try:
            from ..layouts.theme_manager import ThemeManager
            theme = ThemeManager()
            
            # Título
            self.title_label.setFont(theme.get_font('subtitle'))
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme.get_color('text_primary')};
                    padding: {theme.get_spacing('sm')}px;
                    font-weight: bold;
                }}
            """)
            
            # Preview frame (negro para video)
            self.preview_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: #000000;
                    border: 2px solid {theme.get_color('border')};
                    border-radius: {theme.RADIUS['md']}px;
                }}
            """)
            
            # Botón de mute
            self.mute_btn.setStyleSheet(theme.get_button_style('secondary'))
            
        except ImportError:
            pass
    
    def get_preview_frame(self) -> QFrame:
        """
        Retorna el frame de preview para incrustar MPV.
        
        Returns:
            QFrame donde se puede incrustar el reproductor
        """
        return self.preview_frame
    
    def set_mute_text(self, text: str):
        """
        Actualiza el texto del botón de mute.
        
        Args:
            text: Texto a mostrar (🔊 Mute o 🔇 Unmute)
        """
        self.mute_btn.setText(text)
