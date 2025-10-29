"""
Progress Bar Widget - PyQt6
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import Qt


class ProgressBar(QWidget):
    """Widget de barra de progreso"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        """Construye la interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Label de texto
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
    
    def set_progress(self, value: int, text: str = ""):
        """Establece el progreso"""
        self.progress_bar.setValue(value)
        if text:
            self.label.setText(text)
    
    def set_text(self, text: str):
        """Establece solo el texto"""
        self.label.setText(text)
    
    def reset(self):
        """Resetea la barra"""
        self.progress_bar.setValue(0)
        self.label.setText("")
