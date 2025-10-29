"""
Progress Panel - Panel de progreso con barra y label

Widget especializado que combina barra de progreso, label de porcentaje
y botón de acción en un componente cohesivo.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QProgressBar,
                              QLabel, QPushButton, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import Optional


class ProgressPanel(QWidget):
    """
    Panel de progreso con barra, label y botón de acción.
    
    Proporciona:
    - Barra de progreso visual
    - Label de porcentaje
    - Label de mensaje/status
    - Botón de acción principal
    
    Signals:
        action_clicked: Emitido cuando se hace click en el botón de acción
    """
    
    # Signals
    action_clicked = pyqtSignal()
    
    def __init__(
        self,
        button_text: str = "Procesar",
        button_variant: str = "success",
        show_percentage: bool = True,
        parent: Optional[QWidget] = None
    ):
        """
        Inicializa el panel de progreso.
        
        Args:
            button_text: Texto del botón de acción
            button_variant: Variante del botón ('primary', 'success', 'error')
            show_percentage: Si True, muestra label de porcentaje
            parent: Widget padre
        """
        super().__init__(parent)
        
        self.button_text = button_text
        self.button_variant = button_variant
        self.show_percentage = show_percentage
        
        self._build_ui()
        self._connect_signals()
        self._apply_theme()
    
    def _build_ui(self):
        """Construye la interfaz del widget"""
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)
        
        # Sección izquierda: Progreso
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(4)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)  # Usamos label personalizado
        self.progress_bar.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        progress_layout.addWidget(self.progress_bar)
        
        # Label de mensaje/status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        progress_layout.addWidget(self.status_label)
        
        main_layout.addLayout(progress_layout, stretch=1)
        
        # Sección central: Porcentaje (opcional)
        if self.show_percentage:
            self.percentage_label = QLabel("0%")
            self.percentage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.percentage_label.setMinimumWidth(60)
            main_layout.addWidget(self.percentage_label)
        
        # Sección derecha: Botón de acción
        self.action_button = QPushButton(self.button_text)
        self.action_button.setMinimumSize(120, 50)
        self.action_button.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self.action_button)
    
    def _connect_signals(self):
        """Conecta los signals internos"""
        self.action_button.clicked.connect(self.action_clicked.emit)
    
    def _apply_theme(self):
        """Aplica el tema visual"""
        from ..layouts.theme_manager import ThemeManager
        theme = ThemeManager()
        
        # Barra de progreso
        self.progress_bar.setStyleSheet(theme.get_progress_bar_style())
        self.progress_bar.setMinimumHeight(20)
        
        # Label de status
        self.status_label.setFont(theme.get_font('small'))
        self.status_label.setStyleSheet(theme.get_label_style('secondary'))
        
        # Label de porcentaje
        if self.show_percentage:
            self.percentage_label.setFont(theme.get_font('title'))
            self.percentage_label.setStyleSheet(theme.get_label_style('primary'))
        
        # Botón de acción
        button_style = theme.get_button_style(self.button_variant)
        # Personalizar para botón grande
        button_style += f"""
            QPushButton {{
                font-size: 16pt;
                font-weight: bold;
            }}
        """
        self.action_button.setStyleSheet(button_style)
    
    # === API PÚBLICA ===
    
    def set_progress(self, value: int, message: str = ""):
        """
        Actualiza el progreso.
        
        Args:
            value: Valor de progreso (0-100)
            message: Mensaje de status opcional
        """
        self.progress_bar.setValue(value)
        
        if self.show_percentage:
            self.percentage_label.setText(f"{value}%")
        
        if message:
            self.status_label.setText(message)
    
    def set_status(self, message: str):
        """
        Actualiza solo el mensaje de status.
        
        Args:
            message: Mensaje a mostrar
        """
        self.status_label.setText(message)
    
    def reset(self):
        """Resetea el progreso a 0"""
        self.progress_bar.setValue(0)
        if self.show_percentage:
            self.percentage_label.setText("0%")
        self.status_label.setText("")
    
    def set_button_text(self, text: str):
        """
        Actualiza el texto del botón.
        
        Args:
            text: Nuevo texto del botón
        """
        self.action_button.setText(text)
    
    def set_button_enabled(self, enabled: bool):
        """
        Habilita/deshabilita el botón de acción.
        
        Args:
            enabled: True para habilitar
        """
        self.action_button.setEnabled(enabled)
    
    def is_button_enabled(self) -> bool:
        """
        Verifica si el botón está habilitado.
        
        Returns:
            True si está habilitado
        """
        return self.action_button.isEnabled()
    
    def get_progress(self) -> int:
        """
        Obtiene el valor actual de progreso.
        
        Returns:
            Valor de progreso (0-100)
        """
        return self.progress_bar.value()
    
    def set_indeterminate(self, indeterminate: bool):
        """
        Establece modo indeterminado (animación continua).
        
        Args:
            indeterminate: True para modo indeterminado
        """
        if indeterminate:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)  # Modo indeterminado
        else:
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)
