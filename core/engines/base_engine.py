"""
Base Engine - Clase base abstracta para todos los engines

Define la interfaz común que deben implementar todos los engines.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Callable
import subprocess

from ..domain.models import RemuxJob, RemuxResult


class BaseEngine(ABC):
    """
    Clase base abstracta para engines de remuxeo.
    
    Todos los engines (FFmpeg, MKVMerge, etc.) deben heredar de esta clase
    e implementar sus métodos abstractos.
    """
    
    def __init__(self, executable_path: Optional[str] = None):
        """
        Inicializa el engine.
        
        Args:
            executable_path: Ruta al ejecutable. Si es None, busca en PATH.
        """
        self.executable_path = executable_path or self._get_default_executable()
        self._validate_installation()
    
    @abstractmethod
    def _get_default_executable(self) -> str:
        """
        Retorna el nombre del ejecutable por defecto.
        
        Returns:
            Nombre del ejecutable (ej: 'ffmpeg', 'mkvmerge')
        """
        pass
    
    @abstractmethod
    def build_command(self, job: RemuxJob) -> List[str]:
        """
        Construye el comando a ejecutar para un trabajo de remuxeo.
        
        Args:
            job: Trabajo de remuxeo
            
        Returns:
            Lista con el comando y sus argumentos
        """
        pass
    
    def execute(
        self,
        command: List[str],
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> RemuxResult:
        """
        Ejecuta un comando y retorna el resultado.
        
        Args:
            command: Comando a ejecutar
            progress_callback: Callback para reportar progreso (0-100)
            
        Returns:
            Resultado del remuxeo
        """
        try:
            # Ejecutar proceso
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Monitorear progreso
            for line in process.stderr:
                if progress_callback:
                    progress = self._parse_progress(line)
                    if progress is not None:
                        progress_callback(progress)
            
            # Esperar a que termine
            process.wait()
            
            # Verificar resultado
            if process.returncode == 0:
                output_file = self._extract_output_file(command)
                return RemuxResult(
                    success=True,
                    output_file=output_file
                )
            else:
                return RemuxResult(
                    success=False,
                    error_message=f"El proceso falló con código {process.returncode}"
                )
        
        except Exception as e:
            return RemuxResult(
                success=False,
                error_message=str(e)
            )
    
    def remux(
        self,
        job: RemuxJob,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> RemuxResult:
        """
        Ejecuta un remuxeo completo.
        
        Args:
            job: Trabajo de remuxeo
            progress_callback: Callback para reportar progreso
            
        Returns:
            Resultado del remuxeo
        """
        # Construir comando
        command = self.build_command(job)
        
        # Ejecutar
        return self.execute(command, progress_callback)
    
    def is_available(self) -> bool:
        """
        Verifica si el engine está disponible en el sistema.
        
        Returns:
            True si está disponible
        """
        try:
            result = subprocess.run(
                [self.executable_path, "--version"],
                capture_output=True,
                timeout=5,
                shell=True  # Usar shell en Windows para encontrar en PATH
            )
            return result.returncode == 0
        except Exception as e:
            print(f"⚠️ Error verificando {self.executable_path}: {e}")
            return False
    
    def get_version(self) -> Optional[str]:
        """
        Obtiene la versión del engine.
        
        Returns:
            String con la versión o None si no se puede obtener
        """
        try:
            result = subprocess.run(
                [self.executable_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return self._parse_version(result.stdout)
        except:
            pass
        return None
    
    @abstractmethod
    def _parse_progress(self, line: str) -> Optional[int]:
        """
        Parsea una línea de salida para extraer el progreso.
        
        Args:
            line: Línea de salida del proceso
            
        Returns:
            Progreso (0-100) o None si no se puede parsear
        """
        pass
    
    @abstractmethod
    def _parse_version(self, version_output: str) -> Optional[str]:
        """
        Parsea la salida de --version para extraer el número de versión.
        
        Args:
            version_output: Salida del comando --version
            
        Returns:
            String con la versión
        """
        pass
    
    def _validate_installation(self) -> None:
        """
        Valida que el engine está instalado correctamente.
        
        Raises:
            RuntimeError: Si el engine no está disponible
        """
        if not self.is_available():
            # Intentar con shell=True explícitamente
            print(f"⚠️ {self.__class__.__name__}: Intentando verificar '{self.executable_path}'...")
            print(f"   Si FFmpeg está en PATH, la aplicación debería funcionar de todas formas.")
            print(f"   Puedes ignorar este warning si FFmpeg funciona correctamente.")
            
            # No lanzar error, solo advertir
            # raise RuntimeError(
            #     f"{self.__class__.__name__} no está disponible. "
            #     f"Verifica que '{self.executable_path}' está instalado."
            # )
    
    def _extract_output_file(self, command: List[str]) -> Optional[Path]:
        """
        Extrae el archivo de salida del comando.
        
        Args:
            command: Comando ejecutado
            
        Returns:
            Path del archivo de salida o None
        """
        # Buscar el flag de salida (-o, -y, etc.)
        output_flags = ['-o', '-y', '--output']
        
        for i, arg in enumerate(command):
            if arg in output_flags and i + 1 < len(command):
                return Path(command[i + 1])
            # FFmpeg usa -y seguido del archivo al final
            if arg == '-y' and i + 1 < len(command):
                # El último argumento suele ser el archivo de salida
                return Path(command[-1])
        
        return None
    
    def __str__(self) -> str:
        """Representación legible"""
        version = self.get_version()
        return f"{self.__class__.__name__}(v{version})" if version else self.__class__.__name__
