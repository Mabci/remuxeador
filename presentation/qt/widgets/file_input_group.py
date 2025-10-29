"""
File Input Group - Widget para selección de archivos/carpetas

Widget reutilizable que combina label, input y botones de selección
en un componente cohesivo siguiendo principios de diseño profesional.
"""
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QLineEdit, 
                              QPushButton, QFileDialog, QSizePolicy)
from PyQt6.QtCore import pyqtSignal
from pathlib import Path
from typing import Optional


class FileInputGroup(QWidget):
    """
    Widget para selección de archivos o carpetas.
    
    Proporciona:
    - Label descriptivo
    - Input de texto editable
    - Botón para seleccionar archivo
    - Botón para seleccionar carpeta
    
    Signals:
        file_selected: Emitido cuando se selecciona un archivo
        folder_selected: Emitido cuando se selecciona una carpeta
        path_changed: Emitido cuando cambia la ruta (manual o por selección)
    """
    
    # Signals
    file_selected = pyqtSignal(str)      # Ruta del archivo seleccionado
    folder_selected = pyqtSignal(str)    # Ruta de la carpeta seleccionada
    path_changed = pyqtSignal(str)       # Ruta cambiada (cualquier forma)
    
    def __init__(
        self,
        label_text: str,
        file_filter: str = "Todos (*.*)",
        placeholder: str = "",
        show_file_button: bool = True,
        show_folder_button: bool = True,
        is_save_dialog: bool = False,
        parent: Optional[QWidget] = None
    ):
        """
        Inicializa el widget.
        
        Args:
            label_text: Texto del label
            file_filter: Filtro para el diálogo de archivos
            placeholder: Texto placeholder para el input
            show_file_button: Si True, muestra botón de archivo
            show_folder_button: Si True, muestra botón de carpeta
            is_save_dialog: Si True, usa diálogo de guardar en vez de abrir
            parent: Widget padre
        """
        super().__init__(parent)
        
        self.file_filter = file_filter
        self.placeholder = placeholder
        self.show_file_button = show_file_button
        self.show_folder_button = show_folder_button
        self.is_save_dialog = is_save_dialog
        
        self._build_ui(label_text)
        self._connect_signals()
        self._apply_theme()
    
    def _build_ui(self, label_text: str):
        """Construye la interfaz del widget"""
        # Layout principal horizontal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Label
        self.label = QLabel(label_text)
        self.label.setMinimumWidth(80)
        layout.addWidget(self.label)
        
        # Input de texto
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(self.placeholder)
        self.line_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        layout.addWidget(self.line_edit)
        
        # Botón de archivo
        if self.show_file_button:
            self.file_button = QPushButton("📄 Archivo")
            self.file_button.setFixedWidth(90)
            layout.addWidget(self.file_button)
        
        # Botón de carpeta
        if self.show_folder_button:
            self.folder_button = QPushButton("📁 Carpeta")
            self.folder_button.setFixedWidth(90)
            layout.addWidget(self.folder_button)
    
    def _connect_signals(self):
        """Conecta los signals internos"""
        # Conectar cambios en el input
        self.line_edit.textChanged.connect(self.path_changed.emit)
        
        # Conectar botones
        if self.show_file_button:
            self.file_button.clicked.connect(self._on_file_button_clicked)
        
        if self.show_folder_button:
            self.folder_button.clicked.connect(self._on_folder_button_clicked)
    
    def _apply_theme(self):
        """Aplica el tema visual"""
        from ..layouts.theme_manager import ThemeManager
        theme = ThemeManager()
        
        # Estilo del label
        self.label.setStyleSheet(theme.get_label_style('primary'))
        self.label.setFont(theme.get_font('body'))
        
        # Estilo del input
        self.line_edit.setStyleSheet(theme.get_input_style())
        
        # Estilo de los botones
        button_style = theme.get_button_style('primary')
        if self.show_file_button:
            self.file_button.setStyleSheet(button_style)
        if self.show_folder_button:
            self.folder_button.setStyleSheet(button_style)
    
    def _on_file_button_clicked(self):
        """Callback del botón de archivo"""
        if self.is_save_dialog:
            # Diálogo de guardar archivo
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Guardar {self.label.text()}",
                "",
                self.file_filter
            )
        else:
            # Diálogo de abrir archivo
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                f"Seleccionar {self.label.text()}",
                "",
                self.file_filter
            )
        
        if file_path:
            self.set_path(file_path)
            self.file_selected.emit(file_path)
    
    def _on_folder_button_clicked(self):
        """Callback del botón de carpeta"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            f"Seleccionar Carpeta - {self.label.text()}"
        )
        
        if folder_path:
            self.set_path(folder_path)
            self.folder_selected.emit(folder_path)
    
    # === API PÚBLICA ===
    
    def get_path(self) -> str:
        """
        Obtiene la ruta actual.
        
        Returns:
            Ruta como string
        """
        return self.line_edit.text()
    
    def set_path(self, path: str):
        """
        Establece la ruta.
        
        Args:
            path: Ruta a establecer
        """
        self.line_edit.setText(path)
    
    def clear(self):
        """Limpia el input"""
        self.line_edit.clear()
    
    def is_empty(self) -> bool:
        """
        Verifica si el input está vacío.
        
        Returns:
            True si está vacío
        """
        return not self.line_edit.text().strip()
    
    def is_file(self) -> bool:
        """
        Verifica si la ruta es un archivo existente.
        
        Returns:
            True si es un archivo
        """
        path = Path(self.get_path())
        return path.is_file()
    
    def is_folder(self) -> bool:
        """
        Verifica si la ruta es una carpeta existente.
        
        Returns:
            True si es una carpeta
        """
        path = Path(self.get_path())
        return path.is_dir()
    
    def exists(self) -> bool:
        """
        Verifica si la ruta existe.
        
        Returns:
            True si existe
        """
        if self.is_empty():
            return False
        path = Path(self.get_path())
        return path.exists()
    
    def set_enabled(self, enabled: bool):
        """
        Habilita/deshabilita el widget.
        
        Args:
            enabled: True para habilitar
        """
        self.line_edit.setEnabled(enabled)
        if self.show_file_button:
            self.file_button.setEnabled(enabled)
        if self.show_folder_button:
            self.folder_button.setEnabled(enabled)
    
    def set_read_only(self, read_only: bool):
        """
        Establece el input como solo lectura.
        
        Args:
            read_only: True para solo lectura
        """
        self.line_edit.setReadOnly(read_only)
