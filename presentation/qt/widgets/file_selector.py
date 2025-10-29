"""
File Selector Widget - PyQt6
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog
from PyQt6.QtCore import Qt


class FileSelector(QWidget):
    """Widget para seleccionar archivos"""
    
    def __init__(self, label_text: str, file_type: str = "Video", parent=None):
        super().__init__(parent)
        self.file_type = file_type
        self._build_ui(label_text)
    
    def _build_ui(self, label_text: str):
        """Construye la interfaz"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Label
        if label_text:
            label = QLabel(label_text)
            layout.addWidget(label)
        
        # Entry
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(f"Selecciona {self.file_type}...")
        layout.addWidget(self.line_edit, stretch=1)
        
        # Botón
        btn = QPushButton("Buscar")
        btn.setFixedWidth(70)
        btn.clicked.connect(self._browse)
        layout.addWidget(btn)
    
    def _browse(self):
        """Abre diálogo de archivo"""
        if self.file_type == "Video":
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar Video",
                "",
                "Videos (*.mkv *.mp4);;Todos los archivos (*.*)"
            )
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                f"Seleccionar {self.file_type}",
                "",
                "Todos los archivos (*.*)"
            )
        
        if file_path:
            self.line_edit.setText(file_path)
    
    def get_path(self) -> str:
        """Obtiene la ruta seleccionada"""
        return self.line_edit.text()
    
    def set_path(self, path: str):
        """Establece la ruta"""
        self.line_edit.setText(path)


class FolderSelector(QWidget):
    """Widget para seleccionar carpetas"""
    
    def __init__(self, label_text: str, parent=None):
        super().__init__(parent)
        self._build_ui(label_text)
    
    def _build_ui(self, label_text: str):
        """Construye la interfaz"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Label
        if label_text:
            label = QLabel(label_text)
            layout.addWidget(label)
        
        # Entry
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Selecciona carpeta...")
        layout.addWidget(self.line_edit, stretch=1)
        
        # Botón
        btn = QPushButton("Buscar")
        btn.setFixedWidth(70)
        btn.clicked.connect(self._browse)
        layout.addWidget(btn)
    
    def _browse(self):
        """Abre diálogo de carpeta"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar Carpeta",
            ""
        )
        
        if folder_path:
            self.line_edit.setText(folder_path)
    
    def get_path(self) -> str:
        """Obtiene la ruta seleccionada"""
        return self.line_edit.text()
    
    def set_path(self, path: str):
        """Establece la ruta"""
        self.line_edit.setText(path)


class OutputSelector(QWidget):
    """Widget para seleccionar archivo de salida"""
    
    def __init__(self, label_text: str, parent=None):
        super().__init__(parent)
        self._build_ui(label_text)
    
    def _build_ui(self, label_text: str):
        """Construye la interfaz"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Label
        if label_text:
            label = QLabel(label_text)
            layout.addWidget(label)
        
        # Entry
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Selecciona salida...")
        layout.addWidget(self.line_edit, stretch=1)
        
        # Botón
        btn = QPushButton("Guardar")
        btn.setFixedWidth(70)
        btn.clicked.connect(self._browse)
        layout.addWidget(btn)
    
    def _browse(self):
        """Abre diálogo de guardar"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Como",
            "",
            "MKV (*.mkv);;Todos los archivos (*.*)"
        )
        
        if file_path:
            self.line_edit.setText(file_path)
    
    def get_path(self) -> str:
        """Obtiene la ruta seleccionada"""
        return self.line_edit.text()
    
    def set_path(self, path: str):
        """Establece la ruta"""
        self.line_edit.setText(path)
