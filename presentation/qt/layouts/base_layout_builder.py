"""
Base Layout Builder - Clase base abstracta para constructores de layouts

Proporciona una estructura común para construir layouts de tabs,
siguiendo el patrón Template Method y principios SOLID.
"""
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from .theme_manager import ThemeManager
from .layout_factory import LayoutFactory


class BaseLayoutBuilder(ABC):
    """
    Clase base abstracta para constructores de layouts.
    
    Define la estructura común para construir layouts de tabs:
    - Header (selectores de archivos)
    - Main area (preview, controles, etc.)
    - Footer (console, progreso, botones)
    
    Subclases deben implementar métodos abstractos para personalizar
    cada sección según las necesidades del tab.
    """
    
    def __init__(self, parent: QWidget):
        """
        Inicializa el builder.
        
        Args:
            parent: Widget padre donde se construirá el layout
        """
        self.parent = parent
        self.theme = ThemeManager()
        self.factory = LayoutFactory()
    
    def build(self) -> QVBoxLayout:
        """
        Construye el layout completo del tab.
        
        Template Method que define el flujo de construcción:
        1. Crear layout principal
        2. Construir header
        3. Construir main area
        4. Construir footer
        5. Aplicar tema
        
        Returns:
            QVBoxLayout con toda la UI construida
        """
        # Crear layout principal
        main_layout = QVBoxLayout(self.parent)
        main_layout.setSpacing(self.theme.get_spacing('md'))
        main_layout.setContentsMargins(*self.theme.get_margins('md'))
        
        # Construir secciones
        header = self.create_header_section()
        main_area = self.create_main_section()
        footer = self.create_footer_section()
        
        # Agregar secciones al layout principal
        if header:
            main_layout.addWidget(header)
        
        if main_area:
            main_layout.addWidget(main_area, stretch=1)  # Main area toma espacio disponible
        
        if footer:
            main_layout.addWidget(footer)
        
        # Aplicar tema
        self.apply_theme()
        
        return main_layout
    
    @abstractmethod
    def create_header_section(self) -> QWidget:
        """
        Crea la sección de header (selectores de archivos, etc.).
        
        Debe ser implementado por subclases.
        
        Returns:
            QWidget con el header construido
        """
        pass
    
    @abstractmethod
    def create_main_section(self) -> QWidget:
        """
        Crea la sección principal (preview, controles, etc.).
        
        Debe ser implementado por subclases.
        
        Returns:
            QWidget con la sección principal construida
        """
        pass
    
    @abstractmethod
    def create_footer_section(self) -> QWidget:
        """
        Crea la sección de footer (console, progreso, botones).
        
        Debe ser implementado por subclases.
        
        Returns:
            QWidget con el footer construido
        """
        pass
    
    def apply_theme(self):
        """
        Aplica el tema visual al parent widget.
        
        Puede ser sobrescrito por subclases para personalización adicional.
        """
        # Aplicar estilo base al parent
        self.parent.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme.get_color('bg_primary')};
                color: {self.theme.get_color('text_primary')};
            }}
        """)
    
    # === MÉTODOS HELPER COMUNES ===
    
    def create_section_title(self, title: str) -> QWidget:
        """
        Crea un título de sección con estilo consistente.
        
        Args:
            title: Texto del título
            
        Returns:
            QLabel con el título estilizado
        """
        from PyQt6.QtWidgets import QLabel
        
        label = QLabel(title)
        label.setFont(self.theme.get_font('subtitle'))
        label.setStyleSheet(self.theme.get_label_style('primary'))
        
        return label
    
    def create_horizontal_separator(self) -> QWidget:
        """
        Crea un separador horizontal.
        
        Returns:
            QFrame configurado como separador
        """
        from PyQt6.QtWidgets import QFrame
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"""
            QFrame {{
                color: {self.theme.get_color('border')};
                background-color: {self.theme.get_color('border')};
                max-height: 1px;
            }}
        """)
        
        return separator
    
    def create_vertical_separator(self) -> QWidget:
        """
        Crea un separador vertical.
        
        Returns:
            QFrame configurado como separador
        """
        from PyQt6.QtWidgets import QFrame
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"""
            QFrame {{
                color: {self.theme.get_color('border')};
                background-color: {self.theme.get_color('border')};
                max-width: 1px;
            }}
        """)
        
        return separator
