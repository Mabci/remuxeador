"""
DualSync UI Builder - Construcción de UI separada

Construye toda la interfaz del DualSync tab con geometría absoluta.
Separa la construcción de UI de la lógica del tab.
"""
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QFrame, 
                              QTextEdit, QProgressBar, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from dataclasses import dataclass
from ..widgets import SyncControls, ConsoleLog


@dataclass
class DualSyncWidgets:
    """Contenedor de todos los widgets del DualSync tab"""
    # Selectores
    jp_entry: QLineEdit
    jp_file_btn: QPushButton
    jp_folder_btn: QPushButton
    es_entry: QLineEdit
    es_file_btn: QPushButton
    es_folder_btn: QPushButton
    output_entry: QLineEdit
    output_file_btn: QPushButton
    output_folder_btn: QPushButton
    
    # Escaneo y episodios
    scan_btn: QPushButton
    ep_label: QLabel
    episode_combo: QComboBox
    
    # Frames de preview
    preview_jp_frame: QFrame
    preview_lat_frame: QFrame
    
    # Botón cargar preview
    load_preview_btn: QPushButton
    
    # Labels de tiempo
    time_label_jp: QLabel
    time_label_lat: QLabel
    
    # Botones de mute
    mute_jp_btn: QPushButton
    mute_lat_btn: QPushButton
    
    # Navegación
    nav_btn_minus10: QPushButton
    nav_btn_minus1: QPushButton
    nav_btn_plus1: QPushButton
    nav_btn_plus10: QPushButton
    
    # Play/Stop
    play_btn: QPushButton
    stop_btn: QPushButton
    
    # Widgets reutilizables
    sync_controls: SyncControls
    console: ConsoleLog
    
    # Botón procesar
    batch_btn: QPushButton
    
    # Progress
    progress_bar: QProgressBar
    progress_label: QLabel


class DualSyncUIBuilder:
    """
    Constructor de UI para DualSync Tab.
    
    Separa la construcción de la interfaz de la lógica del tab.
    """
    
    def __init__(self, parent: QWidget):
        """
        Inicializa el builder.
        
        Args:
            parent: Widget padre donde se construirá la UI
        """
        self.parent = parent
        self.y_offset = -80  # Offset vertical para ajustar posiciones
    
    def build(self) -> DualSyncWidgets:
        """
        Construye toda la UI y retorna los widgets.
        
        Returns:
            DualSyncWidgets con referencias a todos los widgets
        """
        self.parent.setMinimumSize(1920, 1080)
        
        # Construir secciones
        selectors = self._build_file_selectors()
        scan_widgets = self._build_scan_section()
        preview_frames = self._build_preview_frames()
        central_panel = self._build_central_panel()
        
        # Crear widgets reutilizables
        sync_controls_widget = self._build_sync_controls_widget()
        console_widget = self._build_console_widget()
        
        process_controls = self._build_process_controls()
        
        # Retornar todos los widgets
        return DualSyncWidgets(
            **selectors,
            **scan_widgets,
            **preview_frames,
            **central_panel,
            sync_controls=sync_controls_widget,
            console=console_widget,
            **process_controls
        )
    
    def _build_file_selectors(self) -> dict:
        """Construye selectores de archivos JP, ES y Salida"""
        # === SELECTORES DUALES JP ===
        QLabel("JP", self.parent).setGeometry(180, 132 + self.y_offset, 40, 28)
        jp_entry = QLineEdit(self.parent)
        jp_entry.setGeometry(230, 132 + self.y_offset, 340, 27)
        
        jp_file_btn = QPushButton("📄 Archivo", self.parent)
        jp_file_btn.setGeometry(580, 132 + self.y_offset, 80, 27)
        jp_file_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        jp_folder_btn = QPushButton("📁 Carpeta", self.parent)
        jp_folder_btn.setGeometry(670, 132 + self.y_offset, 80, 27)
        jp_folder_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        # === SELECTORES DUALES ES ===
        QLabel("ES", self.parent).setGeometry(790, 132 + self.y_offset, 40, 28)
        es_entry = QLineEdit(self.parent)
        es_entry.setGeometry(840, 132 + self.y_offset, 340, 27)
        
        es_file_btn = QPushButton("📄 Archivo", self.parent)
        es_file_btn.setGeometry(1190, 132 + self.y_offset, 80, 27)
        es_file_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        es_folder_btn = QPushButton("📁 Carpeta", self.parent)
        es_folder_btn.setGeometry(1280, 132 + self.y_offset, 80, 27)
        es_folder_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        # === SELECTOR DE SALIDA ===
        QLabel("Salida", self.parent).setGeometry(1400, 132 + self.y_offset, 60, 28)
        output_entry = QLineEdit(self.parent)
        output_entry.setGeometry(1470, 132 + self.y_offset, 280, 27)
        
        output_file_btn = QPushButton("📄", self.parent)
        output_file_btn.setGeometry(1760, 132 + self.y_offset, 40, 27)
        output_file_btn.setStyleSheet("background-color: #0071bc; color: white;")
        output_file_btn.setToolTip("Guardar como archivo")
        
        output_folder_btn = QPushButton("📁", self.parent)
        output_folder_btn.setGeometry(1810, 132 + self.y_offset, 40, 27)
        output_folder_btn.setStyleSheet("background-color: #0071bc; color: white;")
        output_folder_btn.setToolTip("Seleccionar carpeta")
        
        return {
            'jp_entry': jp_entry,
            'jp_file_btn': jp_file_btn,
            'jp_folder_btn': jp_folder_btn,
            'es_entry': es_entry,
            'es_file_btn': es_file_btn,
            'es_folder_btn': es_folder_btn,
            'output_entry': output_entry,
            'output_file_btn': output_file_btn,
            'output_folder_btn': output_folder_btn,
        }
    
    def _build_scan_section(self) -> dict:
        """Construye sección de escaneo y selector de episodio"""
        scan_btn = QPushButton("🔍 Escanear", self.parent)
        scan_btn.setGeometry(700, 170 + self.y_offset, 150, 35)
        scan_btn.setStyleSheet("background-color: #0071bc; color: white; font-size: 12pt;")
        scan_btn.hide()
        
        ep_label = QLabel("Episodio:", self.parent)
        ep_label.setGeometry(920, 170 + self.y_offset, 100, 35)
        ep_label.setStyleSheet("color: white; font-size: 11pt;")
        ep_label.hide()
        
        episode_combo = QComboBox(self.parent)
        episode_combo.setGeometry(1020, 175 + self.y_offset, 120, 27)
        episode_combo.hide()
        
        return {
            'scan_btn': scan_btn,
            'ep_label': ep_label,
            'episode_combo': episode_combo,
        }
    
    def _build_preview_frames(self) -> dict:
        """Construye frames de preview"""
        preview_jp_frame = QFrame(self.parent)
        preview_jp_frame.setGeometry(42, 206 + self.y_offset, 766, 431)
        preview_jp_frame.setStyleSheet("background-color: black;")
        
        preview_lat_frame = QFrame(self.parent)
        preview_lat_frame.setGeometry(1113, 206 + self.y_offset, 766, 431)
        preview_lat_frame.setStyleSheet("background-color: black;")
        
        return {
            'preview_jp_frame': preview_jp_frame,
            'preview_lat_frame': preview_lat_frame,
        }
    
    def _build_central_panel(self) -> dict:
        """Construye panel central con controles de video"""
        # Botón cargar preview
        load_preview_btn = QPushButton("Cargar Preview", self.parent)
        load_preview_btn.setGeometry(834, 210 + self.y_offset, 253, 43)
        load_preview_btn.setStyleSheet("background-color: #0071bc; color: white; font-size: 14pt;")
        
        # Panel Video 1
        panel_video1 = QFrame(self.parent)
        panel_video1.setGeometry(833, 264 + self.y_offset, 254, 127)
        panel_video1.setStyleSheet("background-color: #666;")
        
        label_video1 = QLabel("Video 1", self.parent)
        label_video1.setGeometry(833, 280 + self.y_offset, 254, 30)
        label_video1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_video1.setStyleSheet("color: white; font-size: 16pt; background: transparent;")
        
        time_label_jp = QLabel("Time: 0:00:00/0:00:00", self.parent)
        time_label_jp.setGeometry(846, 318 + self.y_offset, 228, 30)
        time_label_jp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_label_jp.setStyleSheet("color: white; font-size: 13pt; background: transparent;")
        time_label_jp.setFont(QFont("Consolas", 11))
        
        mute_jp_btn = QPushButton("Mute", self.parent)
        mute_jp_btn.setGeometry(922, 347 + self.y_offset, 81, 32)
        mute_jp_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        # Panel Video 2
        panel_video2 = QFrame(self.parent)
        panel_video2.setGeometry(833, 399 + self.y_offset, 254, 128)
        panel_video2.setStyleSheet("background-color: #666;")
        
        label_video2 = QLabel("Video 2", self.parent)
        label_video2.setGeometry(833, 415 + self.y_offset, 254, 30)
        label_video2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_video2.setStyleSheet("color: white; font-size: 16pt; background: transparent;")
        
        time_label_lat = QLabel("Time: 0:00:00/0:00:00", self.parent)
        time_label_lat.setGeometry(846, 453 + self.y_offset, 228, 30)
        time_label_lat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_label_lat.setStyleSheet("color: white; font-size: 13pt; background: transparent;")
        time_label_lat.setFont(QFont("Consolas", 11))
        
        mute_lat_btn = QPushButton("Mute", self.parent)
        mute_lat_btn.setGeometry(919, 484 + self.y_offset, 81, 32)
        mute_lat_btn.setStyleSheet("background-color: #0071bc; color: white;")
        
        # Navegación
        nav_btn_minus10 = QPushButton("◀◀ -10s", self.parent)
        nav_btn_minus10.setGeometry(819, 549 + self.y_offset, 60, 39)
        nav_btn_minus10.setStyleSheet("background-color: #0071bc; color: white; font-size: 9pt;")
        
        nav_btn_minus1 = QPushButton("◀ -1s", self.parent)
        nav_btn_minus1.setGeometry(890, 549 + self.y_offset, 65, 39)
        nav_btn_minus1.setStyleSheet("background-color: #0071bc; color: white; font-size: 9pt;")
        
        nav_btn_plus1 = QPushButton("+1s ▶", self.parent)
        nav_btn_plus1.setGeometry(965, 549 + self.y_offset, 60, 39)
        nav_btn_plus1.setStyleSheet("background-color: #0071bc; color: white; font-size: 9pt;")
        
        nav_btn_plus10 = QPushButton("+10s ▶▶", self.parent)
        nav_btn_plus10.setGeometry(1036, 550 + self.y_offset, 65, 39)
        nav_btn_plus10.setStyleSheet("background-color: #0071bc; color: white; font-size: 9pt;")
        
        # Play/Stop
        play_btn = QPushButton("▶", self.parent)
        play_btn.setGeometry(841, 596 + self.y_offset, 94, 41)
        play_btn.setStyleSheet("background-color: #22b573; color: white; font-size: 20pt;")
        
        stop_btn = QPushButton("⏹", self.parent)
        stop_btn.setGeometry(985, 596 + self.y_offset, 94, 41)
        stop_btn.setStyleSheet("background-color: red; color: white; font-size: 20pt;")
        
        return {
            'load_preview_btn': load_preview_btn,
            'time_label_jp': time_label_jp,
            'time_label_lat': time_label_lat,
            'mute_jp_btn': mute_jp_btn,
            'mute_lat_btn': mute_lat_btn,
            'nav_btn_minus10': nav_btn_minus10,
            'nav_btn_minus1': nav_btn_minus1,
            'nav_btn_plus1': nav_btn_plus1,
            'nav_btn_plus10': nav_btn_plus10,
            'play_btn': play_btn,
            'stop_btn': stop_btn,
        }
    
    def _build_sync_controls_widget(self) -> SyncControls:
        """Crea el widget SyncControls"""
        sync_controls = SyncControls(self.parent)
        sync_controls.setGeometry(30, 678 + self.y_offset, 1848, 99)
        return sync_controls
    
    def _build_console_widget(self) -> ConsoleLog:
        """Crea el widget ConsoleLog"""
        console = ConsoleLog(self.parent)
        console.setGeometry(807, 842 + self.y_offset, 1071, 180)
        return console
    
    def _build_process_controls(self) -> dict:
        """Construye botón de procesamiento y barra de progreso"""
        batch_btn = QPushButton("Remuxear", self.parent)
        batch_btn.setGeometry(245, 879 + self.y_offset, 342, 60)
        batch_btn.setStyleSheet("background-color: #22b573; color: white; font-size: 24pt; font-weight: bold;")
        
        progress_bar = QProgressBar(self.parent)
        progress_bar.setGeometry(47, 1003 + self.y_offset, 738, 16)
        progress_bar.setValue(0)
        
        progress_label = QLabel("0%", self.parent)
        progress_label.setGeometry(389, 1024 + self.y_offset, 100, 40)
        progress_label.setFont(QFont("Segoe UI", 18))
        progress_label.setStyleSheet("color: white;")
        progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        return {
            'batch_btn': batch_btn,
            'progress_bar': progress_bar,
            'progress_label': progress_label,
        }
