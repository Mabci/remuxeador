"""
Tool Detector - Detección de herramientas externas

Detecta y valida la disponibilidad de herramientas externas.
"""
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class ToolInfo:
    """Información de una herramienta"""
    name: str
    available: bool
    path: Optional[str] = None
    version: Optional[str] = None
    error: Optional[str] = None
    
    def __str__(self) -> str:
        """Representación legible"""
        if self.available:
            return f"✅ {self.name} v{self.version} ({self.path})"
        else:
            return f"❌ {self.name} no disponible ({self.error})"


class ToolDetector:
    """
    Detector de herramientas externas.
    
    Detecta FFmpeg, FFprobe, MKVMerge, MPV, etc.
    """
    
    @staticmethod
    def detect_ffmpeg(ffmpeg_path: str = "ffmpeg") -> ToolInfo:
        """
        Detecta FFmpeg.
        
        Args:
            ffmpeg_path: Ruta o nombre del ejecutable
            
        Returns:
            ToolInfo con información de FFmpeg
        """
        try:
            # Buscar en PATH si es necesario
            if not Path(ffmpeg_path).exists():
                found_path = shutil.which(ffmpeg_path)
                if found_path:
                    ffmpeg_path = found_path
            
            # Ejecutar --version
            result = subprocess.run(
                [ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parsear versión
                import re
                match = re.search(r'ffmpeg version ([^\s]+)', result.stdout)
                version = match.group(1) if match else "unknown"
                
                return ToolInfo(
                    name="FFmpeg",
                    available=True,
                    path=ffmpeg_path,
                    version=version
                )
            else:
                return ToolInfo(
                    name="FFmpeg",
                    available=False,
                    error="Comando falló"
                )
        
        except FileNotFoundError:
            return ToolInfo(
                name="FFmpeg",
                available=False,
                error="No encontrado en PATH"
            )
        except Exception as e:
            return ToolInfo(
                name="FFmpeg",
                available=False,
                error=str(e)
            )
    
    @staticmethod
    def detect_ffprobe(ffprobe_path: str = "ffprobe") -> ToolInfo:
        """
        Detecta FFprobe.
        
        Args:
            ffprobe_path: Ruta o nombre del ejecutable
            
        Returns:
            ToolInfo con información de FFprobe
        """
        try:
            if not Path(ffprobe_path).exists():
                found_path = shutil.which(ffprobe_path)
                if found_path:
                    ffprobe_path = found_path
            
            result = subprocess.run(
                [ffprobe_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                import re
                match = re.search(r'ffprobe version ([^\s]+)', result.stdout)
                version = match.group(1) if match else "unknown"
                
                return ToolInfo(
                    name="FFprobe",
                    available=True,
                    path=ffprobe_path,
                    version=version
                )
            else:
                return ToolInfo(
                    name="FFprobe",
                    available=False,
                    error="Comando falló"
                )
        
        except FileNotFoundError:
            return ToolInfo(
                name="FFprobe",
                available=False,
                error="No encontrado en PATH"
            )
        except Exception as e:
            return ToolInfo(
                name="FFprobe",
                available=False,
                error=str(e)
            )
    
    @staticmethod
    def detect_mkvmerge(mkvmerge_path: Optional[str] = None) -> ToolInfo:
        """
        Detecta MKVMerge.
        
        Args:
            mkvmerge_path: Ruta o nombre del ejecutable
            
        Returns:
            ToolInfo con información de MKVMerge
        """
        # Buscar en ubicaciones comunes si no se especifica
        if mkvmerge_path is None:
            # Buscar en PATH
            mkvmerge_path = shutil.which("mkvmerge")
            
            # Buscar en ubicaciones comunes de Windows
            if mkvmerge_path is None:
                common_paths = [
                    r"C:\Program Files\MKVToolNix\mkvmerge.exe",
                    r"C:\Program Files (x86)\MKVToolNix\mkvmerge.exe",
                ]
                for path in common_paths:
                    if Path(path).exists():
                        mkvmerge_path = path
                        break
        
        if mkvmerge_path is None:
            return ToolInfo(
                name="MKVMerge",
                available=False,
                error="No encontrado"
            )
        
        try:
            result = subprocess.run(
                [mkvmerge_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                import re
                match = re.search(r'mkvmerge v(\d+\.\d+\.\d+)', result.stdout)
                version = match.group(1) if match else "unknown"
                
                return ToolInfo(
                    name="MKVMerge",
                    available=True,
                    path=mkvmerge_path,
                    version=version
                )
            else:
                return ToolInfo(
                    name="MKVMerge",
                    available=False,
                    error="Comando falló"
                )
        
        except Exception as e:
            return ToolInfo(
                name="MKVMerge",
                available=False,
                error=str(e)
            )
    
    @staticmethod
    def detect_mpv(mpv_path: Optional[str] = None) -> ToolInfo:
        """
        Detecta MPV.
        
        Args:
            mpv_path: Ruta o nombre del ejecutable
            
        Returns:
            ToolInfo con información de MPV
        """
        if mpv_path is None:
            mpv_path = shutil.which("mpv")
        
        if mpv_path is None:
            return ToolInfo(
                name="MPV",
                available=False,
                error="No encontrado"
            )
        
        try:
            result = subprocess.run(
                [mpv_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                import re
                match = re.search(r'mpv ([^\s]+)', result.stdout)
                version = match.group(1) if match else "unknown"
                
                return ToolInfo(
                    name="MPV",
                    available=True,
                    path=mpv_path,
                    version=version
                )
            else:
                return ToolInfo(
                    name="MPV",
                    available=False,
                    error="Comando falló"
                )
        
        except Exception as e:
            return ToolInfo(
                name="MPV",
                available=False,
                error=str(e)
            )
    
    @classmethod
    def detect_all(cls) -> Dict[str, ToolInfo]:
        """
        Detecta todas las herramientas.
        
        Returns:
            Diccionario con información de todas las herramientas
        """
        return {
            'ffmpeg': cls.detect_ffmpeg(),
            'ffprobe': cls.detect_ffprobe(),
            'mkvmerge': cls.detect_mkvmerge(),
            'mpv': cls.detect_mpv(),
        }
    
    @classmethod
    def print_report(cls) -> None:
        """Imprime un reporte de herramientas disponibles"""
        print("\n" + "="*70)
        print("REPORTE DE HERRAMIENTAS EXTERNAS")
        print("="*70)
        
        tools = cls.detect_all()
        
        for tool_name, tool_info in tools.items():
            print(f"\n{tool_info}")
        
        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Test
    ToolDetector.print_report()
