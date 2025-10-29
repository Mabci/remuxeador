"""
Subtitle Service - Validación de subtítulos

Servicio simplificado para validar archivos de subtítulos.
Los offsets ahora se manejan directamente en MKVMerge.
"""
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass

from ..utils.file_utils import get_file_extension, is_subtitle_file


@dataclass
class SubtitleValidation:
    """Resultado de validar un subtítulo"""
    is_valid: bool
    file_path: Optional[Path] = None
    format: Optional[str] = None
    error_message: Optional[str] = None


class SubtitleService:
    """
    Servicio para validar subtítulos.
    
    Responsabilidades:
    - Validar formatos de subtítulos
    - Verificar que los archivos existan
    
    NOTA: Los offsets se aplican directamente en MKVMerge,
    ya no es necesario modificar archivos.
    """
    
    def __init__(self):
        """Inicializa el servicio de subtítulos"""
        pass
    
    def validate_subtitle(
        self,
        subtitle_file: Path
    ) -> SubtitleValidation:
        """
        Valida un archivo de subtítulos.
        
        Args:
            subtitle_file: Archivo de subtítulos a validar
            
        Returns:
            SubtitleValidation con el resultado
        """
        # Validar que el archivo exista
        if not subtitle_file.exists():
            return SubtitleValidation(
                is_valid=False,
                error_message=f"Archivo no existe: {subtitle_file}"
            )
        
        # Validar que sea un archivo de subtítulos
        if not is_subtitle_file(subtitle_file):
            return SubtitleValidation(
                is_valid=False,
                error_message=f"No es un archivo de subtítulos válido: {subtitle_file.suffix}"
            )
        
        # Obtener formato
        extension = get_file_extension(subtitle_file)
        
        return SubtitleValidation(
            is_valid=True,
            file_path=subtitle_file,
            format=extension
        )
    
    def validate_subtitles(
        self,
        subtitle_files: List[Path]
    ) -> List[SubtitleValidation]:
        """
        Valida múltiples archivos de subtítulos.
        
        Args:
            subtitle_files: Lista de archivos a validar
            
        Returns:
            Lista de resultados de validación
        """
        return [self.validate_subtitle(file) for file in subtitle_files]
    
    def is_supported_format(self, subtitle_file: Path) -> bool:
        """
        Verifica si el formato del subtítulo es soportado.
        
        Args:
            subtitle_file: Archivo de subtítulos
            
        Returns:
            True si el formato es soportado
        """
        return is_subtitle_file(subtitle_file)
    
    def get_subtitle_format(self, subtitle_file: Path) -> Optional[str]:
        """
        Obtiene el formato de un archivo de subtítulos.
        
        Args:
            subtitle_file: Archivo de subtítulos
            
        Returns:
            Formato del archivo (ej: '.srt', '.ass') o None
        """
        if not subtitle_file.exists():
            return None
        
        return get_file_extension(subtitle_file)
    
    def __str__(self) -> str:
        """Representación legible"""
        return "SubtitleService(validation only)"
