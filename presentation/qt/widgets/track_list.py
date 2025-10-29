"""
Track List Widget - Lista de tracks (audios/subtitulos)

Widget para mostrar y gestionar lista de tracks cargados.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                              QListWidgetItem, QPushButton, QLabel)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from pathlib import Path


class TrackListWidget(QWidget):
    """
    Widget para mostrar lista de tracks (audios o subtitulos).
    
    Permite:
    - Ver tracks cargados
    - Eliminar tracks
    - Reordenar tracks
    - Seleccionar track activo
    """
    
    # Signals
    track_selected = pyqtSignal(int)  # Index del track seleccionado
    track_removed = pyqtSignal(int)  # Index del track eliminado
    tracks_reordered = pyqtSignal()  # Tracks reordenados
    
    def __init__(self, track_type: str, parent=None):
        """
        Args:
            track_type: 'audio' o 'subtitle'
        """
        super().__init__(parent)
        
        self.track_type = track_type
        self.tracks = []
        
        self._build_ui()
    
    def _build_ui(self):
        """Construye la UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Titulo
        icon = "🎵" if self.track_type == "audio" else "📝"
        title_text = f"{icon} {self.track_type.capitalize()}s"
        
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Lista
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #0071bc;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
        """)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)
        
        self.remove_btn = QPushButton("❌ Eliminar")
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.remove_btn.clicked.connect(self._on_remove_clicked)
        self.remove_btn.setEnabled(False)
        btn_layout.addWidget(self.remove_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def add_track(self, file_path: str, offset_ms: int = 0):
        """
        Agrega un track a la lista.
        
        Args:
            file_path: Ruta al archivo
            offset_ms: Offset en milisegundos
        """
        track_info = {
            'path': file_path,
            'offset_ms': offset_ms,
            'name': Path(file_path).name
        }
        
        self.tracks.append(track_info)
        
        # Crear item
        offset_text = f" (offset: {offset_ms}ms)" if offset_ms != 0 else ""
        item_text = f"{len(self.tracks)}. {track_info['name']}{offset_text}"
        
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, len(self.tracks) - 1)  # Guardar index
        self.list_widget.addItem(item)
    
    def remove_selected(self):
        """Elimina el track seleccionado"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.list_widget.takeItem(current_row)
            del self.tracks[current_row]
            self.track_removed.emit(current_row)
            
            # Actualizar numeros
            self._update_item_numbers()
    
    def clear_all(self):
        """Elimina todos los tracks"""
        self.list_widget.clear()
        self.tracks.clear()
    
    def get_tracks(self):
        """Retorna lista de tracks"""
        return self.tracks.copy()
    
    def get_track_count(self):
        """Retorna cantidad de tracks"""
        return len(self.tracks)
    
    def _on_item_clicked(self, item):
        """Callback cuando se hace click en un item"""
        index = item.data(Qt.ItemDataRole.UserRole)
        self.track_selected.emit(index)
        self.remove_btn.setEnabled(True)
    
    def _on_remove_clicked(self):
        """Callback del boton eliminar"""
        self.remove_selected()
        
        if self.list_widget.count() == 0:
            self.remove_btn.setEnabled(False)
    
    def _update_item_numbers(self):
        """Actualiza los numeros de los items"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            track = self.tracks[i]
            
            offset_text = f" (offset: {track['offset_ms']}ms)" if track['offset_ms'] != 0 else ""
            item_text = f"{i + 1}. {track['name']}{offset_text}"
            item.setText(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
