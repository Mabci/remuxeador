"""
Gestor de MPV Player Portable
Maneja la descarga, instalación y configuración de MPV

Migrado a infrastructure/external/
"""
import os
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path
from typing import Optional


class MPVManager:
    """Gestor de MPV portable para Windows"""
    
    # URL de descarga de MPV portable
    MPV_DOWNLOAD_URL = "https://sourceforge.net/projects/mpv-player-windows/files/64bit/mpv-x86_64-latest.7z/download"
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Inicializa el gestor de MPV
        
        Args:
            base_dir: Directorio base del proyecto. Si es None, usa el actual.
        """
        if base_dir is None:
            # Obtener directorio del proyecto (3 niveles arriba de este archivo)
            base_dir = Path(__file__).parent.parent.parent
        
        self.base_dir = Path(base_dir)
        self.external_dir = self.base_dir / "external"
        self.mpv_dir = self.external_dir / "mpv"
        self.mpv_exe = self.mpv_dir / "mpv.exe"
        
        # Crear directorios si no existen
        self.external_dir.mkdir(exist_ok=True)
    
    def is_installed(self) -> bool:
        """Verifica si MPV está instalado"""
        return self.mpv_exe.exists()
    
    def get_mpv_path(self) -> Optional[str]:
        """
        Obtiene la ruta al ejecutable de MPV
        
        Returns:
            Ruta al mpv.exe o None si no está instalado
        """
        if self.is_installed():
            return str(self.mpv_exe)
        
        # Intentar buscar en PATH del sistema
        try:
            result = subprocess.run(
                ['where', 'mpv'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        return None
    
    def download_mpv(self, progress_callback=None) -> bool:
        """
        Descarga MPV portable
        
        Args:
            progress_callback: Función a llamar con el progreso (bytes_descargados, total_bytes)
        
        Returns:
            True si la descarga fue exitosa
        """
        try:
            zip_path = self.external_dir / "mpv.zip"
            
            print("Descargando MPV desde SourceForge...")
            
            def report_progress(block_count, block_size, total_size):
                if progress_callback:
                    downloaded = block_count * block_size
                    progress_callback(downloaded, total_size)
            
            urllib.request.urlretrieve(
                self.MPV_DOWNLOAD_URL,
                zip_path,
                reporthook=report_progress
            )
            
            print(f"MPV descargado en: {zip_path}")
            return True
            
        except Exception as e:
            print(f"Error descargando MPV: {e}")
            return False
    
    def extract_mpv(self) -> bool:
        """
        Extrae el archivo de MPV descargado
        
        Returns:
            True si la extracción fue exitosa
        """
        try:
            zip_path = self.external_dir / "mpv.zip"
            
            if not zip_path.exists():
                print("Archivo de MPV no encontrado")
                return False
            
            print(f"Extrayendo MPV en: {self.mpv_dir}")
            
            # Crear directorio de MPV
            self.mpv_dir.mkdir(exist_ok=True)
            
            # Extraer ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.mpv_dir)
            
            # Buscar mpv.exe dentro del directorio extraído
            # A veces viene en una subcarpeta
            for root, dirs, files in os.walk(self.mpv_dir):
                if 'mpv.exe' in files:
                    found_exe = Path(root) / 'mpv.exe'
                    if found_exe != self.mpv_exe:
                        # Mover al directorio correcto
                        shutil.move(str(found_exe), str(self.mpv_exe))
                    break
            
            # Limpiar archivo ZIP
            zip_path.unlink()
            
            print("MPV extraído correctamente")
            return True
            
        except Exception as e:
            print(f"Error extrayendo MPV: {e}")
            return False
    
    def install_mpv(self, progress_callback=None) -> bool:
        """
        Descarga e instala MPV portable
        
        Args:
            progress_callback: Función para reportar progreso
        
        Returns:
            True si la instalación fue exitosa
        """
        if self.is_installed():
            print("MPV ya está instalado")
            return True
        
        print("Instalando MPV portable...")
        
        # Descargar
        if not self.download_mpv(progress_callback):
            return False
        
        # Extraer
        if not self.extract_mpv():
            return False
        
        # Verificar instalación
        if self.is_installed():
            print(f"✅ MPV instalado correctamente en: {self.mpv_exe}")
            return True
        else:
            print("❌ Error: MPV no se pudo instalar correctamente")
            return False
    
    def test_mpv(self) -> bool:
        """
        Prueba que MPV funciona correctamente
        
        Returns:
            True si MPV funciona
        """
        mpv_path = self.get_mpv_path()
        
        if not mpv_path:
            return False
        
        try:
            result = subprocess.run(
                [mpv_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def get_libmpv_path(self) -> Optional[str]:
        """
        Obtiene la ruta a libmpv-2.dll (necesario para python-mpv)
        
        Returns:
            Ruta a libmpv-2.dll o None
        """
        if not self.is_installed():
            return None
        
        # libmpv-2.dll debería estar en el mismo directorio que mpv.exe
        libmpv = self.mpv_dir / "libmpv-2.dll"
        
        if libmpv.exists():
            return str(libmpv)
        
        return None


def check_mpv_installation() -> dict:
    """
    Verifica el estado de la instalación de MPV
    
    Returns:
        Diccionario con información del estado
    """
    manager = MPVManager()
    
    return {
        'installed': manager.is_installed(),
        'mpv_path': manager.get_mpv_path(),
        'libmpv_path': manager.get_libmpv_path(),
        'working': manager.test_mpv()
    }


if __name__ == "__main__":
    # Prueba del gestor
    print("=" * 60)
    print("PRUEBA DEL GESTOR DE MPV")
    print("=" * 60)
    
    manager = MPVManager()
    
    print(f"\nDirectorio base: {manager.base_dir}")
    print(f"Directorio MPV: {manager.mpv_dir}")
    
    if manager.is_installed():
        print("\n✅ MPV ya está instalado")
        print(f"Ruta: {manager.get_mpv_path()}")
        
        if manager.test_mpv():
            print("✅ MPV funciona correctamente")
        else:
            print("⚠️ MPV instalado pero no funciona")
    else:
        print("\n❌ MPV no está instalado")
        print("Ejecuta install.bat para instalarlo")
    
    print("\n" + "=" * 60)
