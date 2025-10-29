"""
Assembler UI Builder - Construcción de UI para AssemblerTab

Estilo similar a DualSync pero con un solo preview y gestión de tracks externos.
"""
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QFrame,
                              QTextEdit, QProgressBar, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from dataclasses import dataclass
from ..widgets import SyncControls, ConsoleLog


@dataclass
class AssemblerWidgets:
    """Contenedor de widgets del AssemblerTab"""
    # Selectores de archivos
    video_entry: QLineEdit
    video_file_btn: QPushButton
    video_folder_btn: QPushButton
    
    # Pistas externas
    audio_entry: QLineEdit
    audio_file_btn: QPushButton
    audio_folder_btn: QPushButton
    subtitle_entry: QLineEdit
    subtitle_file_btn: QPushButton
    subtitle_folder_btn: QPushButton
    forced_entry: QLineEdit
    forced_file_btn: QPushButton
    forced_folder_btn: QPushButton
    
    output_entry: QLineEdit
    output_file_btn: QPushButton
    output_folder_btn: QPushButton
    
    # Escaneo (modo carpetas)
    scan_btn: QPushButton
    episode_combo: QComboBox
    
    # Preview
    preview_frame: QFrame
    load_preview_btn: QPushButton
    
    # Label de tiempo
    time_label: QLabel
    
    # Navegación
    nav_btn_minus10: QPushButton
    nav_btn_minus1: QPushButton
    nav_btn_plus1: QPushButton
    nav_btn_plus10: QPushButton
    
    # Play/Stop
    play_btn: QPushButton
    stop_btn: QPushButton
    
    # Selectores de pistas
    audio_track_combo: QComboBox
    subtitle_track_combo: QComboBox
    
    # Widgets reutilizables
    sync_controls: SyncControls
    console: ConsoleLog
    
    # Progreso
    progress_bar: QProgressBar
    progress_label: QLabel
    process_btn: QPushButton


class AssemblerUIBuilder:
    """Constructor de UI para AssemblerTab - Estilo DualSync"""
    
    def __init__(self, parent: QWidget):
        self.parent = parent
        self.y_offset = 0  # Sin offset - todo debe ser visible desde arriba
    
    def build(self) -> AssemblerWidgets:
        """Construye toda la UI y retorna los widgets"""
        self.parent.setMinimumSize(1920, 1080)
        
        # Construir secciones
        selectors = self._build_file_selectors()
        preview_section = self._build_preview_section()
        central_panel = self._build_central_panel()
        track_lists = self._build_track_lists()
        
        # Crear widgets reutilizables
        sync_controls_widget = self._build_sync_controls_widget()
        console_widget = self._build_console_widget()
        
        process_controls = self._build_process_controls()
        
        # Retornar todos los widgets
        return AssemblerWidgets(
            **selectors,
            **preview_section,
            **central_panel,
            **track_lists,
            sync_controls=sync_controls_widget,
            console=console_widget,
            **process_controls
        )
    
    def _build_file_selectors(self) -> dict:
        """Construye selectores de archivos - Layout reorganizado"""
        
        # === COLUMNA IZQUIERDA: VIDEO Y SALIDA ===
        
        # VIDEO
        video_label = QLabel("Video:", self.parent)
        video_label.setGeometry(30, 52 + self.y_offset, 80, 28)
        video_label.setStyleSheet("color: white; font-size: 12pt;")
        
        video_entry = QLineEdit(self.parent)
        video_entry.setGeometry(120, 52 + self.y_offset, 350, 27)
        
        video_file_btn = QPushButton("📄 Archivo", self.parent)
        video_file_btn.setGeometry(480, 52 + self.y_offset, 90, 27)
        video_file_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        video_folder_btn = QPushButton("📁 Carpeta", self.parent)
        video_folder_btn.setGeometry(580, 52 + self.y_offset, 90, 27)
        video_folder_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        # SALIDA
        output_label = QLabel("Salida:", self.parent)
        output_label.setGeometry(30, 92 + self.y_offset, 80, 28)
        output_label.setStyleSheet("color: white; font-size: 12pt;")
        
        output_entry = QLineEdit(self.parent)
        output_entry.setGeometry(120, 92 + self.y_offset, 350, 27)
        
        output_file_btn = QPushButton("📄 Archivo", self.parent)
        output_file_btn.setGeometry(480, 92 + self.y_offset, 90, 27)
        output_file_btn.setStyleSheet("background-color: #0071bc; color: white;")
        output_file_btn.setToolTip("Guardar como archivo")
        
        output_folder_btn = QPushButton("📁 Carpeta", self.parent)
        output_folder_btn.setGeometry(580, 92 + self.y_offset, 90, 27)
        output_folder_btn.setStyleSheet("background-color: #0071bc; color: white;")
        output_folder_btn.setToolTip("Seleccionar carpeta de salida")
        
        # === COLUMNA DERECHA: PISTAS EXTERNAS ===
        
        # AUDIO EXTERNO
        audio_label = QLabel("Audio:", self.parent)
        audio_label.setGeometry(720, 52 + self.y_offset, 100, 28)
        audio_label.setStyleSheet("color: white; font-size: 12pt;")
        
        audio_entry = QLineEdit(self.parent)
        audio_entry.setGeometry(830, 52 + self.y_offset, 350, 27)
        audio_entry.setPlaceholderText("Opcional - Audio externo en español latino")
        
        audio_file_btn = QPushButton("📄 Archivo", self.parent)
        audio_file_btn.setGeometry(1190, 52 + self.y_offset, 90, 27)
        audio_file_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        audio_folder_btn = QPushButton("📁 Carpeta", self.parent)
        audio_folder_btn.setGeometry(1290, 52 + self.y_offset, 90, 27)
        audio_folder_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        # SUBTÍTULOS EXTERNOS
        subtitle_label = QLabel("Subtítulos:", self.parent)
        subtitle_label.setGeometry(720, 92 + self.y_offset, 100, 28)
        subtitle_label.setStyleSheet("color: white; font-size: 12pt;")
        
        subtitle_entry = QLineEdit(self.parent)
        subtitle_entry.setGeometry(830, 92 + self.y_offset, 350, 27)
        subtitle_entry.setPlaceholderText("Opcional - Subtítulos externos en español latino")
        
        subtitle_file_btn = QPushButton("📄 Archivo", self.parent)
        subtitle_file_btn.setGeometry(1190, 92 + self.y_offset, 90, 27)
        subtitle_file_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        subtitle_folder_btn = QPushButton("📁 Carpeta", self.parent)
        subtitle_folder_btn.setGeometry(1290, 92 + self.y_offset, 90, 27)
        subtitle_folder_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        # LETREROS (FORCED) EXTERNOS
        forced_label = QLabel("Letreros:", self.parent)
        forced_label.setGeometry(720, 132 + self.y_offset, 100, 28)
        forced_label.setStyleSheet("color: white; font-size: 12pt;")
        
        forced_entry = QLineEdit(self.parent)
        forced_entry.setGeometry(830, 132 + self.y_offset, 350, 27)
        forced_entry.setPlaceholderText("Opcional - Letreros/Forced subtitles")
        
        forced_file_btn = QPushButton("📄 Archivo", self.parent)
        forced_file_btn.setGeometry(1190, 132 + self.y_offset, 90, 27)
        forced_file_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        forced_folder_btn = QPushButton("📁 Carpeta", self.parent)
        forced_folder_btn.setGeometry(1290, 132 + self.y_offset, 90, 27)
        forced_folder_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        # === ESCANEO Y SELECTOR DE EPISODIO (siempre visible) ===
        # Reubicado en el espacio vacío a la derecha
        scan_btn = QPushButton("🔍 Escanear Carpetas", self.parent)
        scan_btn.setGeometry(1400, 52 + self.y_offset, 180, 35)
        scan_btn.setStyleSheet("background-color: #0071bc; color: white; font-size: 11pt;")
        
        episode_label = QLabel("Episodio:", self.parent)
        episode_label.setGeometry(1400, 97 + self.y_offset, 80, 28)
        episode_label.setStyleSheet("color: white; font-size: 11pt;")
        
        episode_combo = QComboBox(self.parent)
        episode_combo.setGeometry(1490, 97 + self.y_offset, 90, 27)
        episode_combo.setStyleSheet("background-color: #3c3c3c; color: white; font-size: 11pt;")
        
        return {
            'video_entry': video_entry,
            'video_file_btn': video_file_btn,
            'video_folder_btn': video_folder_btn,
            'audio_entry': audio_entry,
            'audio_file_btn': audio_file_btn,
            'audio_folder_btn': audio_folder_btn,
            'subtitle_entry': subtitle_entry,
            'subtitle_file_btn': subtitle_file_btn,
            'subtitle_folder_btn': subtitle_folder_btn,
            'forced_entry': forced_entry,
            'forced_file_btn': forced_file_btn,
            'forced_folder_btn': forced_folder_btn,
            'output_entry': output_entry,
            'output_file_btn': output_file_btn,
            'output_folder_btn': output_folder_btn,
            'scan_btn': scan_btn,
            'episode_combo': episode_combo,
        }
    
    def _build_preview_section(self) -> dict:
        """Construye frame de preview"""
        preview_frame = QFrame(self.parent)
        preview_frame.setGeometry(30, 180 + self.y_offset, 766, 431)
        preview_frame.setStyleSheet("background-color: black; border: 2px solid #555;")
        
        return {
            'preview_frame': preview_frame,
        }
    
    def _build_central_panel(self) -> dict:
        """Construye panel central con controles de video"""
        # Botón cargar preview
        load_preview_btn = QPushButton("▶ Cargar Preview", self.parent)
        load_preview_btn.setGeometry(822, 180 + self.y_offset, 253, 43)
        load_preview_btn.setStyleSheet("background-color: #0071bc; color: white; font-size: 14pt;")
        
        # Panel de control de video
        panel_video = QFrame(self.parent)
        panel_video.setGeometry(821, 234 + self.y_offset, 254, 100)
        panel_video.setStyleSheet("background-color: #666; border-radius: 5px;")
        
        label_video = QLabel("Preview", self.parent)
        label_video.setGeometry(821, 245 + self.y_offset, 254, 30)
        label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_video.setStyleSheet("color: white; font-size: 16pt; background: transparent;")
        
        time_label = QLabel("Time: 0:00:00/0:00:00", self.parent)
        time_label.setGeometry(834, 283 + self.y_offset, 228, 30)
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_label.setStyleSheet("color: white; font-size: 13pt; background: transparent;")
        time_label.setFont(QFont("Consolas", 11))
        
        # Navegación
        nav_btn_minus10 = QPushButton("◀◀ -10s", self.parent)
        nav_btn_minus10.setGeometry(807, 350 + self.y_offset, 60, 39)
        nav_btn_minus10.setStyleSheet("background-color: #0071bc; color: white; font-size: 9pt;")
        
        nav_btn_minus1 = QPushButton("◀ -1s", self.parent)
        nav_btn_minus1.setGeometry(878, 350 + self.y_offset, 65, 39)
        nav_btn_minus1.setStyleSheet("background-color: #0071bc; color: white; font-size: 9pt;")
        
        nav_btn_plus1 = QPushButton("+1s ▶", self.parent)
        nav_btn_plus1.setGeometry(953, 350 + self.y_offset, 60, 39)
        nav_btn_plus1.setStyleSheet("background-color: #0071bc; color: white; font-size: 9pt;")
        
        nav_btn_plus10 = QPushButton("+10s ▶▶", self.parent)
        nav_btn_plus10.setGeometry(1024, 350 + self.y_offset, 65, 39)
        nav_btn_plus10.setStyleSheet("background-color: #0071bc; color: white; font-size: 9pt;")
        
        # Play/Stop
        play_btn = QPushButton("▶", self.parent)
        play_btn.setGeometry(829, 400 + self.y_offset, 94, 41)
        play_btn.setStyleSheet("background-color: #22b573; color: white; font-size: 20pt;")
        
        stop_btn = QPushButton("⏹", self.parent)
        stop_btn.setGeometry(973, 400 + self.y_offset, 94, 41)
        stop_btn.setStyleSheet("background-color: red; color: white; font-size: 20pt;")
        
        return {
            'load_preview_btn': load_preview_btn,
            'time_label': time_label,
            'nav_btn_minus10': nav_btn_minus10,
            'nav_btn_minus1': nav_btn_minus1,
            'nav_btn_plus1': nav_btn_plus1,
            'nav_btn_plus10': nav_btn_plus10,
            'play_btn': play_btn,
            'stop_btn': stop_btn,
        }
    
    def _build_track_lists(self) -> dict:
        """Construye selectores de pistas"""
        # === SELECTOR DE AUDIO ===
        audio_frame = QFrame(self.parent)
        audio_frame.setGeometry(822, 455 + self.y_offset, 253, 156)
        audio_frame.setStyleSheet("background-color: #2b2b2b; border: 2px solid #555; border-radius: 5px;")
        
        audio_title = QLabel("🎵 Pista de Audio", self.parent)
        audio_title.setGeometry(822, 465 + self.y_offset, 253, 30)
        audio_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        audio_title.setStyleSheet("color: white; font-size: 13pt; background: transparent; border: none;")
        
        audio_track_label = QLabel("Seleccionar pista:", self.parent)
        audio_track_label.setGeometry(832, 505 + self.y_offset, 233, 25)
        audio_track_label.setStyleSheet("color: white; font-size: 11pt; background: transparent;")
        
        audio_track_combo = QComboBox(self.parent)
        audio_track_combo.setGeometry(832, 535 + self.y_offset, 233, 30)
        audio_track_combo.setStyleSheet("background-color: white; color: black; font-size: 11pt;")
        audio_track_combo.addItem("Sin audio")
        
        # === SELECTOR DE SUBTÍTULOS ===
        subtitle_frame = QFrame(self.parent)
        subtitle_frame.setGeometry(1101, 180 + self.y_offset, 766, 431)
        subtitle_frame.setStyleSheet("background-color: #2b2b2b; border: 2px solid #555; border-radius: 5px;")
        
        subtitle_title = QLabel("📝 Pista de Subtítulos", self.parent)
        subtitle_title.setGeometry(1101, 195 + self.y_offset, 766, 35)
        subtitle_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_title.setStyleSheet("color: white; font-size: 16pt; background: transparent; border: none;")
        
        subtitle_track_label = QLabel("Seleccionar pista para preview:", self.parent)
        subtitle_track_label.setGeometry(1121, 250 + self.y_offset, 726, 30)
        subtitle_track_label.setStyleSheet("color: white; font-size: 13pt; background: transparent;")
        
        subtitle_track_combo = QComboBox(self.parent)
        subtitle_track_combo.setGeometry(1121, 290 + self.y_offset, 726, 35)
        subtitle_track_combo.setStyleSheet("background-color: white; color: black; font-size: 12pt;")
        subtitle_track_combo.addItem("Sin subtítulos")
        
        return {
            'audio_track_combo': audio_track_combo,
            'subtitle_track_combo': subtitle_track_combo,
        }
    
    def _build_sync_controls_widget(self) -> SyncControls:
        """Crea el widget SyncControls"""
        sync_controls = SyncControls(self.parent)
        sync_controls.setGeometry(30, 598 + self.y_offset, 1848, 99)
        return sync_controls
    
    def _build_console_widget(self) -> ConsoleLog:
        """Crea el widget ConsoleLog"""
        console = ConsoleLog(self.parent)
        console.setGeometry(807, 762 + self.y_offset, 1071, 160)
        return console
    
    def _build_process_controls(self) -> dict:
        """Construye botón de procesamiento y barra de progreso"""
        process_btn = QPushButton("🎬 Remuxear", self.parent)
        process_btn.setGeometry(245, 799 + self.y_offset, 342, 60)
        process_btn.setStyleSheet("background-color: #22b573; color: white; font-size: 24pt; font-weight: bold;")
        
        progress_bar = QProgressBar(self.parent)
        progress_bar.setGeometry(47, 923 + self.y_offset, 738, 16)
        progress_bar.setValue(0)
        
        progress_label = QLabel("0%", self.parent)
        progress_label.setGeometry(389, 944 + self.y_offset, 100, 40)
        progress_label.setFont(QFont("Segoe UI", 18))
        progress_label.setStyleSheet("color: white;")
        progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return {
            'process_btn': process_btn,
            'progress_bar': progress_bar,
            'progress_label': progress_label,
        }
