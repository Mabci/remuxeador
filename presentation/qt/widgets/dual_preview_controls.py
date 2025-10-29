"""
Dual Preview Controls - Controles centralizados para dual preview

Widget con controles de playback compartidos entre dos previews,
con labels de tiempo para ambos videos.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class DualPreviewControls(QWidget):
    """
    Widget de controles centralizados para dual preview.
    
    Características:
    - Labels de tiempo para JP y LAT
    - Botones de navegación (-10s, -1s, +1s, +10s)
    - Botones de playback (play/pause, stop)
    - Signals para comunicación con el tab
    
    Signals:
        play_clicked: Usuario presionó play/pause
        stop_clicked: Usuario presionó stop
        seek_requested(int): Usuario solicitó seek (segundos)
    """
    
    # Signals
    play_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    seek_requested = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_theme()
    
    def _setup_ui(self):
        """Configura la UI del widget"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # === LABELS DE TIEMPO ===
        time_layout = QHBoxLayout()
        time_layout.setSpacing(16)
        
        # Tiempo JP
        jp_time_layout = QVBoxLayout()
        jp_time_layout.setSpacing(2)
        
        jp_label = QLabel("🇯🇵 Japonés")
        jp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        jp_time_layout.addWidget(jp_label)
        
        self.time_label_jp = QLabel("00:00:00 / 00:00:00")
        self.time_label_jp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        jp_time_layout.addWidget(self.time_label_jp)
        
        time_layout.addLayout(jp_time_layout, stretch=1)
        
        # Tiempo LAT
        lat_time_layout = QVBoxLayout()
        lat_time_layout.setSpacing(2)
        
        lat_label = QLabel("🌎 Latino")
        lat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lat_time_layout.addWidget(lat_label)
        
        self.time_label_lat = QLabel("00:00:00 / 00:00:00")
        self.time_label_lat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lat_time_layout.addWidget(self.time_label_lat)
        
        time_layout.addLayout(lat_time_layout, stretch=1)
        
        main_layout.addLayout(time_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # === CONTROLES DE NAVEGACIÓN ===
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(4)
        
        # Botones de navegación
        self.nav_btn_minus10 = QPushButton("-10s")
        self.nav_btn_minus10.setMinimumWidth(60)
        self.nav_btn_minus10.clicked.connect(lambda: self.seek_requested.emit(-10))
        nav_layout.addWidget(self.nav_btn_minus10)
        
        self.nav_btn_minus1 = QPushButton("-1s")
        self.nav_btn_minus1.setMinimumWidth(50)
        self.nav_btn_minus1.clicked.connect(lambda: self.seek_requested.emit(-1))
        nav_layout.addWidget(self.nav_btn_minus1)
        
        nav_layout.addStretch()
        
        self.nav_btn_plus1 = QPushButton("+1s")
        self.nav_btn_plus1.setMinimumWidth(50)
        self.nav_btn_plus1.clicked.connect(lambda: self.seek_requested.emit(1))
        nav_layout.addWidget(self.nav_btn_plus1)
        
        self.nav_btn_plus10 = QPushButton("+10s")
        self.nav_btn_plus10.setMinimumWidth(60)
        self.nav_btn_plus10.clicked.connect(lambda: self.seek_requested.emit(10))
        nav_layout.addWidget(self.nav_btn_plus10)
        
        main_layout.addLayout(nav_layout)
        
        # === CONTROLES DE PLAYBACK ===
        playback_layout = QHBoxLayout()
        playback_layout.setSpacing(8)
        
        playback_layout.addStretch()
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setMinimumSize(80, 40)
        self.play_btn.clicked.connect(self.play_clicked.emit)
        playback_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setMinimumSize(80, 40)
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        playback_layout.addWidget(self.stop_btn)
        
        playback_layout.addStretch()
        
        main_layout.addLayout(playback_layout)
    
    def _apply_theme(self):
        """Aplica el tema visual"""
        try:
            from ..layouts.theme_manager import ThemeManager
            theme = ThemeManager()
            
            # Frame principal
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {theme.get_color('bg_secondary')};
                    border: 1px solid {theme.get_color('border')};
                    border-radius: {theme.RADIUS['md']}px;
                }}
            """)
            
            # Labels de tiempo
            self.time_label_jp.setFont(theme.get_font('mono'))
            self.time_label_lat.setFont(theme.get_font('mono'))
            
            self.time_label_jp.setStyleSheet(f"""
                QLabel {{
                    color: {theme.get_color('text_primary')};
                    background-color: {theme.get_color('bg_input')};
                    padding: {theme.get_spacing('sm')}px;
                    border: 1px solid {theme.get_color('border')};
                    border-radius: {theme.RADIUS['sm']}px;
                    font-weight: bold;
                }}
            """)
            
            self.time_label_lat.setStyleSheet(f"""
                QLabel {{
                    color: {theme.get_color('text_primary')};
                    background-color: {theme.get_color('bg_input')};
                    padding: {theme.get_spacing('sm')}px;
                    border: 1px solid {theme.get_color('border')};
                    border-radius: {theme.RADIUS['sm']}px;
                    font-weight: bold;
                }}
            """)
            
            # Botones de navegación
            nav_style = theme.get_button_style('secondary')
            self.nav_btn_minus10.setStyleSheet(nav_style)
            self.nav_btn_minus1.setStyleSheet(nav_style)
            self.nav_btn_plus1.setStyleSheet(nav_style)
            self.nav_btn_plus10.setStyleSheet(nav_style)
            
            # Botones de playback
            self.play_btn.setStyleSheet(theme.get_button_style('success'))
            self.stop_btn.setStyleSheet(theme.get_button_style('error'))
            
        except ImportError:
            pass
    
    def set_time_jp(self, current: str, total: str):
        """
        Actualiza el tiempo del video japonés.
        
        Args:
            current: Tiempo actual (formato HH:MM:SS)
            total: Tiempo total (formato HH:MM:SS)
        """
        self.time_label_jp.setText(f"{current} / {total}")
    
    def set_time_lat(self, current: str, total: str):
        """
        Actualiza el tiempo del video latino.
        
        Args:
            current: Tiempo actual (formato HH:MM:SS)
            total: Tiempo total (formato HH:MM:SS)
        """
        self.time_label_lat.setText(f"{current} / {total}")
    
    def set_play_text(self, text: str):
        """
        Actualiza el texto del botón de play.
        
        Args:
            text: Texto a mostrar (▶ o ⏸)
        """
        self.play_btn.setText(text)
