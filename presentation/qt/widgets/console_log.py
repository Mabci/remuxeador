"""
Console Log Widget - PyQt6

Widget profesional de consola para mostrar logs con formato,
timestamps automáticos e iconos por nivel de severidad.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime


class ConsoleLog(QWidget):
    """
    Widget de consola para logs.
    
    Proporciona:
    - Logs con timestamps automáticos
    - Iconos por nivel de severidad
    - Auto-scroll
    - Formato consistente
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._apply_theme()
    
    def _build_ui(self):
        """Construye la interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Título
        title = QLabel("📋 Consola")
        title_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Área de texto
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 9))
        layout.addWidget(self.text_edit)
        
        # Log inicial
        self.log("✅ Consola lista", "info")
    
    def log(self, message: str, level: str = "info"):
        """
        Agrega un mensaje al log
        
        Args:
            message: Mensaje a mostrar
            level: Nivel (info, success, error, warning)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }
        icon = icons.get(level, "ℹ️")
        
        formatted = f"[{timestamp}] {icon} {message}"
        self.text_edit.append(formatted)
        
        # Auto-scroll
        scrollbar = self.text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear(self):
        """Limpia la consola"""
        self.text_edit.clear()
        self.log("✅ Consola limpiada", "info")
    
    def _apply_theme(self):
        """Aplica el tema visual usando ThemeManager"""
        try:
            from ..layouts.theme_manager import ThemeManager
            theme = ThemeManager()
            
            # Aplicar estilo al text edit
            self.text_edit.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {theme.get_color('bg_input')};
                    color: {theme.get_color('text_primary')};
                    border: 1px solid {theme.get_color('border')};
                    border-radius: {theme.RADIUS['sm']}px;
                    font-family: 'Consolas';
                    font-size: 9pt;
                }}
            """)
            
            # Configurar size policy para que sea responsive
            self.text_edit.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )
            self.text_edit.setMaximumHeight(200)  # Altura máxima
            
        except ImportError:
            # Si no está disponible ThemeManager, usar estilos básicos
            pass
