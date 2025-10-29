"""
Dual Preview Widget - PyQt6 con MPV

Widget FUNCIONAL copiado del original.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
import platform
import sys


class DualPreview(QWidget):
    """Widget de dual preview con MPV"""
    
    # Signal para log
    log_signal = pyqtSignal(str, str)  # message, level
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Estado
        self.mpv_jp = None
        self.mpv_lat = None
        self.current_video_jp = None
        self.current_video_lat = None
        self.is_playing = False
        
        # Timer para actualizar timestamps
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timestamps)
        
        self._build_ui()
    
    def _build_ui(self):
        """Construye la interfaz"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Preview izquierdo (JP)
        left_widget = self._create_preview_widget("Video 1 (JP)")
        layout.addWidget(left_widget, stretch=1)
        
        # Controles centrales
        center_widget = self._create_controls()
        layout.addWidget(center_widget)
        
        # Preview derecho (ES)
        right_widget = self._create_preview_widget("Video 2 (ES)")
        layout.addWidget(right_widget, stretch=1)
    
    def _create_preview_widget(self, title: str):
        """Crea un widget de preview - 16:9 aspect ratio"""
        widget = QFrame()
        widget.setFrameShape(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        # Stretch arriba para centrar
        layout.addStretch()
        
        # Título pequeño
        title_label = QLabel(title)
        title_font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Frame de video - 16:9 aspect ratio (560x315)
        video_frame = QFrame()
        video_frame.setFixedSize(560, 315)
        video_frame.setStyleSheet("background-color: black;")
        layout.addWidget(video_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Stretch abajo para centrar
        layout.addStretch()
        
        # Placeholder
        placeholder = QLabel("📺\nCarga archivos")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: gray;")
        
        # Colocar placeholder en el centro del video_frame
        placeholder_layout = QVBoxLayout(video_frame)
        placeholder_layout.addWidget(placeholder)
        
        # Guardar referencias
        if "JP" in title:
            self.video_frame_jp = video_frame
            self.placeholder_jp = placeholder
        else:
            self.video_frame_lat = video_frame
            self.placeholder_lat = placeholder
        
        return widget
    
    def _create_controls(self):
        """Crea controles centrales - Según diseño exacto"""
        widget = QFrame()
        widget.setFrameShape(QFrame.Shape.StyledPanel)
        widget.setStyleSheet("background-color: #505050;")
        widget.setFixedWidth(160)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Botón Cargar Preview
        self.load_btn = QPushButton("Cargar Preview")
        self.load_btn.setFixedHeight(28)
        self.load_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        layout.addWidget(self.load_btn)
        
        layout.addSpacing(8)
        
        # --- Video 1 ---
        video1_label = QLabel("Video 1")
        video1_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        video1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(video1_label)
        
        self.time_label_jp = QLabel("Time: 0:12:23/0:24:34")
        self.time_label_jp.setFont(QFont("Consolas", 8))
        self.time_label_jp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label_jp)
        
        self.mute_jp_btn = QPushButton("Mute")
        self.mute_jp_btn.setFixedHeight(26)
        self.mute_jp_btn.clicked.connect(self.toggle_mute_jp)
        layout.addWidget(self.mute_jp_btn)
        
        layout.addSpacing(8)
        
        # --- Video 2 ---
        video2_label = QLabel("Video 2")
        video2_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        video2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(video2_label)
        
        self.time_label_lat = QLabel("Time: 0:12:35/0:25:34")
        self.time_label_lat.setFont(QFont("Consolas", 8))
        self.time_label_lat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label_lat)
        
        self.mute_lat_btn = QPushButton("Mute")
        self.mute_lat_btn.setFixedHeight(26)
        self.mute_lat_btn.clicked.connect(self.toggle_mute_lat)
        layout.addWidget(self.mute_lat_btn)
        
        layout.addSpacing(10)
        
        # --- Controles de Navegación (1 fila, 4 botones) ---
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(1)
        
        nav_buttons = [
            ("◀◀-10s", -10),
            ("◀-1s", -1),
            ("+1s▶", 1),
            ("+10s▶▶", 10)
        ]
        
        for text, seconds in nav_buttons:
            btn = QPushButton(text)
            btn.setFixedSize(38, 24)
            btn.setFont(QFont("Segoe UI", 6))
            btn.clicked.connect(lambda checked, s=seconds: self.seek(s))
            nav_layout.addWidget(btn)
        
        layout.addLayout(nav_layout)
        
        layout.addSpacing(6)
        
        # --- Play/Stop ---
        playback_layout = QHBoxLayout()
        playback_layout.setSpacing(3)
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(75, 36)
        self.play_btn.setStyleSheet("background-color: #28a745; font-size: 16pt;")
        self.play_btn.clicked.connect(self.toggle_play)
        playback_layout.addWidget(self.play_btn)
        
        stop_btn = QPushButton("⏹")
        stop_btn.setFixedSize(75, 36)
        stop_btn.setStyleSheet("background-color: #dc3545; font-size: 16pt;")
        stop_btn.clicked.connect(self.stop)
        playback_layout.addWidget(stop_btn)
        
        layout.addLayout(playback_layout)
        
        layout.addStretch()
        
        return widget
    
    def load_videos(self, video_jp_path: str, video_lat_path: str):
        """Carga ambos videos"""
        try:
            self.log_signal.emit(f"Cargando Video 1: {video_jp_path}", "info")
            self.log_signal.emit(f"Cargando Video 2: {video_lat_path}", "info")
            
            # Inicializar MPV si es necesario
            if not self.mpv_jp:
                self._init_mpv_jp()
            if not self.mpv_lat:
                self._init_mpv_lat()
            
            # Ocultar placeholders
            self.placeholder_jp.hide()
            self.placeholder_lat.hide()
            
            # Cargar videos
            self.mpv_jp.play(video_jp_path)
            self.mpv_jp.pause = True
            
            self.mpv_lat.play(video_lat_path)
            self.mpv_lat.pause = True
            
            # Por defecto: JP muted, LAT audible
            self.mpv_jp.mute = True
            self.mpv_lat.mute = False
            self.mute_jp_btn.setText("🔇 Unmute")
            self.mute_lat_btn.setText("🔊 Mute")
            
            self.current_video_jp = video_jp_path
            self.current_video_lat = video_lat_path
            
            # Iniciar timer de timestamps
            self.timer.start(500)  # Actualizar cada 0.5s
            
            self.log_signal.emit("✅ Previews cargados", "success")
            
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}", "error")
            raise
    
    def _init_mpv_jp(self):
        """Inicializa MPV para video japonés"""
        try:
            import mpv
            
            if platform.system() == 'Linux':
                self.mpv_jp = mpv.MPV(keep_open='yes', idle=True)
            else:
                # Windows - embedding
                wid = int(self.video_frame_jp.winId())
                self.mpv_jp = mpv.MPV(wid=str(wid), keep_open='yes', idle=True)
        except Exception as e:
            print(f"❌ Error inicializando MPV JP: {e}")
            raise
    
    def _init_mpv_lat(self):
        """Inicializa MPV para video español"""
        try:
            import mpv
            
            if platform.system() == 'Linux':
                self.mpv_lat = mpv.MPV(keep_open='yes', idle=True)
            else:
                # Windows - embedding
                wid = int(self.video_frame_lat.winId())
                self.mpv_lat = mpv.MPV(wid=str(wid), keep_open='yes', idle=True)
        except Exception as e:
            print(f"❌ Error inicializando MPV LAT: {e}")
            raise
    
    def _update_timestamps(self):
        """Actualiza timestamps"""
        try:
            if self.mpv_jp and self.current_video_jp:
                pos_jp = self.mpv_jp.time_pos or 0
                dur_jp = self.mpv_jp.duration or 0
                time_str_jp = f"Time: {self._format_time(pos_jp)}/{self._format_time(dur_jp)}"
                self.time_label_jp.setText(time_str_jp)
            
            if self.mpv_lat and self.current_video_lat:
                pos_lat = self.mpv_lat.time_pos or 0
                dur_lat = self.mpv_lat.duration or 0
                time_str_lat = f"Time: {self._format_time(pos_lat)}/{self._format_time(dur_lat)}"
                self.time_label_lat.setText(time_str_lat)
        except:
            pass
    
    def _format_time(self, seconds: float) -> str:
        """Formatea segundos a H:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}:{minutes:02d}:{secs:02d}"
    
    def toggle_play(self):
        """Toggle play/pause"""
        if not self.mpv_jp or not self.mpv_lat:
            return
        
        self.is_playing = not self.is_playing
        self.mpv_jp.pause = not self.is_playing
        self.mpv_lat.pause = not self.is_playing
        
        self.play_btn.setText("⏸️" if self.is_playing else "▶️")
    
    def stop(self):
        """Detiene y reinicia"""
        if not self.mpv_jp or not self.mpv_lat:
            return
        
        self.mpv_jp.seek(0, reference='absolute')
        self.mpv_lat.seek(0, reference='absolute')
        self.mpv_jp.pause = True
        self.mpv_lat.pause = True
        self.is_playing = False
        self.play_btn.setText("▶️")
    
    def seek(self, seconds: int):
        """Navega en ambos videos"""
        if not self.mpv_jp or not self.mpv_lat:
            return
        
        self.mpv_jp.seek(seconds, reference='relative')
        self.mpv_lat.seek(seconds, reference='relative')
    
    def toggle_mute_jp(self):
        """Toggle mute JP"""
        if not self.mpv_jp:
            return
        
        self.mpv_jp.mute = not self.mpv_jp.mute
        self.mute_jp_btn.setText("🔇 Unmute" if self.mpv_jp.mute else "🔊 Mute")
    
    def toggle_mute_lat(self):
        """Toggle mute LAT"""
        if not self.mpv_lat:
            return
        
        self.mpv_lat.mute = not self.mpv_lat.mute
        self.mute_lat_btn.setText("🔇 Unmute" if self.mpv_lat.mute else "🔊 Mute")
    
    def cleanup(self):
        """Limpia recursos"""
        self.timer.stop()
        if self.mpv_jp:
            try:
                self.mpv_jp.terminate()
            except:
                pass
        if self.mpv_lat:
            try:
                self.mpv_lat.terminate()
            except:
                pass
