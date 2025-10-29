"""
Layout Factory - Factory para crear layouts comunes

Proporciona métodos estáticos para crear layouts reutilizables
siguiendo el patrón Factory y principios DRY.
"""
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
                              QFormLayout, QGroupBox, QFrame, QSplitter, QLabel)
from PyQt6.QtCore import Qt
from typing import List, Tuple, Optional
from .theme_manager import ThemeManager


class LayoutFactory:
    """
    Factory para crear layouts comunes de forma consistente.
    
    Proporciona métodos estáticos para crear:
    - Layouts horizontales y verticales
    - Grupos con frames
    - Forms
    - Splitters
    """
    
    theme = ThemeManager()
    
    @staticmethod
    def create_horizontal_layout(
        widgets: List[QWidget],
        spacing: Optional[int] = None,
        margins: Optional[Tuple[int, int, int, int]] = None,
        stretch_factors: Optional[List[int]] = None
    ) -> QHBoxLayout:
        """
        Crea un layout horizontal con los widgets proporcionados.
        
        Args:
            widgets: Lista de widgets a agregar
            spacing: Espaciado entre widgets (None usa tema por defecto)
            margins: Márgenes (top, right, bottom, left)
            stretch_factors: Factores de estiramiento para cada widget
            
        Returns:
            QHBoxLayout configurado
        """
        layout = QHBoxLayout()
        
        # Aplicar spacing
        if spacing is not None:
            layout.setSpacing(spacing)
        else:
            layout.setSpacing(LayoutFactory.theme.get_spacing('md'))
        
        # Aplicar margins
        if margins is not None:
            layout.setContentsMargins(*margins)
        else:
            layout.setContentsMargins(*LayoutFactory.theme.get_margins('md'))
        
        # Agregar widgets
        for i, widget in enumerate(widgets):
            if stretch_factors and i < len(stretch_factors):
                layout.addWidget(widget, stretch=stretch_factors[i])
            else:
                layout.addWidget(widget)
        
        return layout
    
    @staticmethod
    def create_vertical_layout(
        widgets: List[QWidget],
        spacing: Optional[int] = None,
        margins: Optional[Tuple[int, int, int, int]] = None,
        stretch_factors: Optional[List[int]] = None
    ) -> QVBoxLayout:
        """
        Crea un layout vertical con los widgets proporcionados.
        
        Args:
            widgets: Lista de widgets a agregar
            spacing: Espaciado entre widgets (None usa tema por defecto)
            margins: Márgenes (top, right, bottom, left)
            stretch_factors: Factores de estiramiento para cada widget
            
        Returns:
            QVBoxLayout configurado
        """
        layout = QVBoxLayout()
        
        # Aplicar spacing
        if spacing is not None:
            layout.setSpacing(spacing)
        else:
            layout.setSpacing(LayoutFactory.theme.get_spacing('md'))
        
        # Aplicar margins
        if margins is not None:
            layout.setContentsMargins(*margins)
        else:
            layout.setContentsMargins(*LayoutFactory.theme.get_margins('md'))
        
        # Agregar widgets
        for i, widget in enumerate(widgets):
            if stretch_factors and i < len(stretch_factors):
                layout.addWidget(widget, stretch=stretch_factors[i])
            else:
                layout.addWidget(widget)
        
        return layout
    
    @staticmethod
    def create_grid_layout(
        widget_positions: List[Tuple[QWidget, int, int, int, int]],
        spacing: Optional[int] = None,
        margins: Optional[Tuple[int, int, int, int]] = None
    ) -> QGridLayout:
        """
        Crea un layout de grilla con widgets en posiciones específicas.
        
        Args:
            widget_positions: Lista de tuplas (widget, row, col, rowspan, colspan)
            spacing: Espaciado entre widgets
            margins: Márgenes del layout
            
        Returns:
            QGridLayout configurado
        """
        layout = QGridLayout()
        
        # Aplicar spacing
        if spacing is not None:
            layout.setSpacing(spacing)
        else:
            layout.setSpacing(LayoutFactory.theme.get_spacing('md'))
        
        # Aplicar margins
        if margins is not None:
            layout.setContentsMargins(*margins)
        else:
            layout.setContentsMargins(*LayoutFactory.theme.get_margins('md'))
        
        # Agregar widgets
        for widget, row, col, rowspan, colspan in widget_positions:
            layout.addWidget(widget, row, col, rowspan, colspan)
        
        return layout
    
    @staticmethod
    def create_form_layout(
        label_widget_pairs: List[Tuple[str, QWidget]],
        spacing: Optional[int] = None,
        margins: Optional[Tuple[int, int, int, int]] = None
    ) -> QFormLayout:
        """
        Crea un layout de formulario con pares label-widget.
        
        Args:
            label_widget_pairs: Lista de tuplas (texto_label, widget)
            spacing: Espaciado vertical entre filas
            margins: Márgenes del layout
            
        Returns:
            QFormLayout configurado
        """
        layout = QFormLayout()
        
        # Aplicar spacing
        if spacing is not None:
            layout.setVerticalSpacing(spacing)
            layout.setHorizontalSpacing(spacing)
        else:
            spacing_val = LayoutFactory.theme.get_spacing('md')
            layout.setVerticalSpacing(spacing_val)
            layout.setHorizontalSpacing(spacing_val)
        
        # Aplicar margins
        if margins is not None:
            layout.setContentsMargins(*margins)
        else:
            layout.setContentsMargins(*LayoutFactory.theme.get_margins('md'))
        
        # Agregar pares
        for label_text, widget in label_widget_pairs:
            label = QLabel(label_text)
            label.setStyleSheet(LayoutFactory.theme.get_label_style('primary'))
            layout.addRow(label, widget)
        
        return layout
    
    @staticmethod
    def create_group_box(
        title: str,
        layout: Optional[QHBoxLayout | QVBoxLayout] = None,
        widgets: Optional[List[QWidget]] = None
    ) -> QGroupBox:
        """
        Crea un QGroupBox con título y layout.
        
        Args:
            title: Título del grupo
            layout: Layout a usar (si None, crea QVBoxLayout)
            widgets: Widgets a agregar al layout (opcional)
            
        Returns:
            QGroupBox configurado
        """
        group = QGroupBox(title)
        group.setStyleSheet(LayoutFactory.theme.get_groupbox_style())
        
        # Crear layout si no se proporciona
        if layout is None:
            layout = QVBoxLayout()
            layout.setSpacing(LayoutFactory.theme.get_spacing('md'))
            layout.setContentsMargins(*LayoutFactory.theme.get_margins('md'))
        
        # Agregar widgets si se proporcionan
        if widgets:
            for widget in widgets:
                layout.addWidget(widget)
        
        group.setLayout(layout)
        return group
    
    @staticmethod
    def create_frame(
        layout: Optional[QHBoxLayout | QVBoxLayout] = None,
        elevated: bool = False
    ) -> QFrame:
        """
        Crea un QFrame con estilo y layout.
        
        Args:
            layout: Layout a usar (si None, crea QVBoxLayout)
            elevated: Si True, usa estilo elevado
            
        Returns:
            QFrame configurado
        """
        frame = QFrame()
        frame.setStyleSheet(LayoutFactory.theme.get_frame_style(elevated))
        
        # Crear layout si no se proporciona
        if layout is None:
            layout = QVBoxLayout()
            layout.setSpacing(LayoutFactory.theme.get_spacing('md'))
            layout.setContentsMargins(*LayoutFactory.theme.get_margins('md'))
        
        frame.setLayout(layout)
        return frame
    
    @staticmethod
    def create_splitter(
        widgets: List[QWidget],
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
        stretch_factors: Optional[List[int]] = None,
        sizes: Optional[List[int]] = None
    ) -> QSplitter:
        """
        Crea un QSplitter con widgets redimensionables.
        
        Args:
            widgets: Lista de widgets a agregar
            orientation: Orientación (Horizontal o Vertical)
            stretch_factors: Factores de estiramiento para cada widget
            sizes: Tamaños iniciales para cada widget
            
        Returns:
            QSplitter configurado
        """
        splitter = QSplitter(orientation)
        
        # Agregar widgets
        for widget in widgets:
            splitter.addWidget(widget)
        
        # Aplicar stretch factors
        if stretch_factors:
            for i, factor in enumerate(stretch_factors):
                if i < splitter.count():
                    splitter.setStretchFactor(i, factor)
        
        # Aplicar tamaños iniciales
        if sizes:
            splitter.setSizes(sizes)
        
        # Estilo del splitter
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {LayoutFactory.theme.get_color('border')};
            }}
            QSplitter::handle:hover {{
                background-color: {LayoutFactory.theme.get_color('border_light')};
            }}
        """)
        
        return splitter
    
    @staticmethod
    def add_stretch(layout: QHBoxLayout | QVBoxLayout, stretch: int = 1):
        """
        Agrega un stretch al layout.
        
        Args:
            layout: Layout al que agregar el stretch
            stretch: Factor de estiramiento
        """
        layout.addStretch(stretch)
    
    @staticmethod
    def add_spacing(layout: QHBoxLayout | QVBoxLayout, size: int):
        """
        Agrega espaciado fijo al layout.
        
        Args:
            layout: Layout al que agregar el espaciado
            size: Tamaño del espaciado en píxeles
        """
        layout.addSpacing(size)
