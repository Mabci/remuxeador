"""
Theme Manager - Gestión centralizada de estilos y temas

Proporciona una paleta de colores, fuentes y estilos consistentes
para toda la aplicación, siguiendo principios de diseño profesional
inspirados en Blender, DaVinci Resolve y Adobe Premiere.
"""
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtWidgets import QApplication
from typing import Dict, Tuple


class ThemeManager:
    """
    Singleton para gestionar temas y estilos de la aplicación.
    
    Proporciona:
    - Paleta de colores consistente
    - Fuentes tipográficas
    - Espaciado y márgenes
    - Estilos CSS reutilizables
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._setup_theme()
    
    def _setup_theme(self):
        """Configura el tema de la aplicación"""
        # Paleta de colores (estilo profesional oscuro)
        self.COLORS = {
            # Backgrounds
            'bg_primary': '#1e1e1e',      # Fondo principal
            'bg_secondary': '#2b2b2b',    # Paneles
            'bg_tertiary': '#3c3c3c',     # Elementos elevados
            'bg_input': '#252525',        # Inputs
            
            # Surfaces
            'surface': '#252525',
            'surface_variant': '#2f2f2f',
            'surface_hover': '#3a3a3a',
            
            # Accents
            'primary': '#0071bc',         # Azul (acciones principales)
            'primary_hover': '#0088dd',
            'primary_pressed': '#005a99',
            'success': '#28a745',         # Verde (éxito)
            'success_hover': '#34ce57',
            'error': '#dc3545',           # Rojo (errores)
            'error_hover': '#e74c5c',
            'warning': '#ffc107',         # Amarillo (advertencias)
            'warning_hover': '#ffcd39',
            
            # Text
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'text_disabled': '#666666',
            'text_hint': '#808080',
            
            # Borders
            'border': '#555555',
            'border_light': '#666666',
            'border_focus': '#0071bc',
            'border_error': '#dc3545',
            
            # Special
            'selection': '#0071bc',
            'selection_bg': 'rgba(0, 113, 188, 0.3)',
            'overlay': 'rgba(0, 0, 0, 0.5)',
        }
        
        # Espaciado (siguiendo sistema de 4px)
        self.SPACING = {
            'xs': 2,      # Extra small
            'sm': 4,      # Small
            'md': 8,      # Medium
            'lg': 12,     # Large
            'xl': 16,     # Extra large
            'xxl': 24,    # Extra extra large
        }
        
        # Márgenes (top, right, bottom, left)
        self.MARGINS = {
            'none': (0, 0, 0, 0),
            'xs': (2, 2, 2, 2),
            'sm': (4, 4, 4, 4),
            'md': (8, 8, 8, 8),
            'lg': (12, 12, 12, 12),
            'xl': (16, 16, 16, 16),
        }
        
        # Fuentes
        self.FONTS = {
            'title': QFont('Segoe UI', 14, QFont.Weight.Bold),
            'subtitle': QFont('Segoe UI', 12, QFont.Weight.Bold),
            'body': QFont('Segoe UI', 10),
            'body_bold': QFont('Segoe UI', 10, QFont.Weight.Bold),
            'small': QFont('Segoe UI', 9),
            'mono': QFont('Consolas', 9),
            'mono_small': QFont('Consolas', 8),
        }
        
        # Tamaños de widgets
        self.SIZES = {
            'button_height': 32,
            'input_height': 28,
            'icon_small': 16,
            'icon_medium': 24,
            'icon_large': 32,
            'preview_min_width': 400,
            'preview_min_height': 300,
            'console_max_height': 200,
        }
        
        # Border radius
        self.RADIUS = {
            'none': 0,
            'sm': 2,
            'md': 4,
            'lg': 6,
            'xl': 8,
        }
    
    def get_color(self, color_name: str) -> str:
        """
        Obtiene un color por nombre.
        
        Args:
            color_name: Nombre del color (ej: 'primary', 'bg_secondary')
            
        Returns:
            Código de color hexadecimal
        """
        return self.COLORS.get(color_name, '#ffffff')
    
    def get_spacing(self, size: str = 'md') -> int:
        """
        Obtiene un valor de espaciado.
        
        Args:
            size: Tamaño del espaciado ('xs', 'sm', 'md', 'lg', 'xl', 'xxl')
            
        Returns:
            Valor en píxeles
        """
        return self.SPACING.get(size, 8)
    
    def get_margins(self, size: str = 'md') -> Tuple[int, int, int, int]:
        """
        Obtiene valores de márgenes.
        
        Args:
            size: Tamaño de los márgenes ('none', 'xs', 'sm', 'md', 'lg', 'xl')
            
        Returns:
            Tupla (top, right, bottom, left)
        """
        return self.MARGINS.get(size, (8, 8, 8, 8))
    
    def get_font(self, font_type: str = 'body') -> QFont:
        """
        Obtiene una fuente por tipo.
        
        Args:
            font_type: Tipo de fuente ('title', 'subtitle', 'body', etc.)
            
        Returns:
            QFont configurado
        """
        return self.FONTS.get(font_type, self.FONTS['body'])
    
    # === ESTILOS CSS REUTILIZABLES ===
    
    def get_button_style(self, variant: str = 'primary') -> str:
        """
        Genera estilo CSS para botones.
        
        Args:
            variant: Variante del botón ('primary', 'success', 'error', 'secondary')
            
        Returns:
            String CSS
        """
        color_map = {
            'primary': ('primary', 'primary_hover', 'primary_pressed'),
            'success': ('success', 'success_hover', 'success'),
            'error': ('error', 'error_hover', 'error'),
            'secondary': ('bg_tertiary', 'surface_hover', 'bg_secondary'),
        }
        
        bg, hover, pressed = color_map.get(variant, color_map['primary'])
        
        return f"""
            QPushButton {{
                background-color: {self.get_color(bg)};
                color: {self.get_color('text_primary')};
                border: 1px solid {self.get_color('border')};
                border-radius: {self.RADIUS['md']}px;
                padding: 6px 12px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {self.get_color(hover)};
                border-color: {self.get_color('border_light')};
            }}
            QPushButton:pressed {{
                background-color: {self.get_color(pressed)};
            }}
            QPushButton:disabled {{
                background-color: {self.get_color('bg_secondary')};
                color: {self.get_color('text_disabled')};
                border-color: {self.get_color('border')};
            }}
        """
    
    def get_input_style(self) -> str:
        """Genera estilo CSS para inputs (QLineEdit)"""
        return f"""
            QLineEdit {{
                background-color: {self.get_color('bg_input')};
                color: {self.get_color('text_primary')};
                border: 1px solid {self.get_color('border')};
                border-radius: {self.RADIUS['sm']}px;
                padding: 4px 8px;
                selection-background-color: {self.get_color('selection')};
            }}
            QLineEdit:focus {{
                border-color: {self.get_color('border_focus')};
            }}
            QLineEdit:disabled {{
                background-color: {self.get_color('bg_secondary')};
                color: {self.get_color('text_disabled')};
            }}
        """
    
    def get_groupbox_style(self) -> str:
        """Genera estilo CSS para QGroupBox"""
        return f"""
            QGroupBox {{
                background-color: {self.get_color('bg_secondary')};
                border: 1px solid {self.get_color('border')};
                border-radius: {self.RADIUS['md']}px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: bold;
                color: {self.get_color('text_primary')};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                background-color: transparent;
            }}
        """
    
    def get_frame_style(self, elevated: bool = False) -> str:
        """
        Genera estilo CSS para QFrame.
        
        Args:
            elevated: Si True, usa color más claro para efecto elevado
        """
        bg = 'bg_tertiary' if elevated else 'bg_secondary'
        return f"""
            QFrame {{
                background-color: {self.get_color(bg)};
                border: 1px solid {self.get_color('border')};
                border-radius: {self.RADIUS['md']}px;
            }}
        """
    
    def get_label_style(self, variant: str = 'primary') -> str:
        """
        Genera estilo CSS para QLabel.
        
        Args:
            variant: Variante del label ('primary', 'secondary', 'hint')
        """
        color_map = {
            'primary': 'text_primary',
            'secondary': 'text_secondary',
            'hint': 'text_hint',
        }
        
        color = color_map.get(variant, 'text_primary')
        
        return f"""
            QLabel {{
                color: {self.get_color(color)};
                background-color: transparent;
            }}
        """
    
    def get_progress_bar_style(self) -> str:
        """Genera estilo CSS para QProgressBar"""
        return f"""
            QProgressBar {{
                background-color: {self.get_color('bg_secondary')};
                border: 1px solid {self.get_color('border')};
                border-radius: {self.RADIUS['sm']}px;
                text-align: center;
                color: {self.get_color('text_primary')};
            }}
            QProgressBar::chunk {{
                background-color: {self.get_color('primary')};
                border-radius: {self.RADIUS['sm']}px;
            }}
        """
    
    def get_combo_box_style(self) -> str:
        """Genera estilo CSS para QComboBox"""
        return f"""
            QComboBox {{
                background-color: {self.get_color('bg_input')};
                color: {self.get_color('text_primary')};
                border: 1px solid {self.get_color('border')};
                border-radius: {self.RADIUS['sm']}px;
                padding: 4px 8px;
            }}
            QComboBox:hover {{
                border-color: {self.get_color('border_light')};
            }}
            QComboBox:focus {{
                border-color: {self.get_color('border_focus')};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.get_color('bg_tertiary')};
                color: {self.get_color('text_primary')};
                selection-background-color: {self.get_color('selection')};
                border: 1px solid {self.get_color('border')};
            }}
        """
    
    def apply_global_theme(self, app: QApplication):
        """
        Aplica el tema global a la aplicación.
        
        Args:
            app: Instancia de QApplication
        """
        # Establecer stylesheet global
        app.setStyleSheet(f"""
            QWidget {{
                background-color: {self.get_color('bg_primary')};
                color: {self.get_color('text_primary')};
                font-family: 'Segoe UI';
                font-size: 10pt;
            }}
            
            QToolTip {{
                background-color: {self.get_color('bg_tertiary')};
                color: {self.get_color('text_primary')};
                border: 1px solid {self.get_color('border')};
                padding: 4px;
            }}
            
            QScrollBar:vertical {{
                background-color: {self.get_color('bg_secondary')};
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.get_color('surface_variant')};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.get_color('surface_hover')};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background-color: {self.get_color('bg_secondary')};
                height: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {self.get_color('surface_variant')};
                min-width: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {self.get_color('surface_hover')};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """)
