"""
Remux Service - Servicio principal que orquesta el proceso completo de remuxeo.
Usa MKVMerge para todos los remuxeos (arquitectura simplificada).
"""
from pathlib import Path
from typing import Optional, Callable
import time

from ..domain.models import RemuxJob, RemuxResult
from ..engines.mkvmerge_engine import MKVMergeEngine
from ..engines.ffprobe_engine import FFprobeEngine
from ..utils.validators import validate_remux_job, ValidationError


class RemuxService:
    """
    Servicio de remuxeo simplificado.

    Responsabilidades:
    - Validar trabajos de remuxeo
    - Ejecutar remuxeo con MKVMerge
    - Coordinar el flujo completo
    - Reportar progreso

    NOTA: MKVMerge es OBLIGATORIO.
    """

    def __init__(
        self,
        mkvmerge_engine: Optional[MKVMergeEngine] = None,
        ffprobe_engine: Optional[FFprobeEngine] = None
    ):
        """
        Inicializa el servicio de remuxeo.

        Args:
            mkvmerge_engine: Engine de MKVMerge (OBLIGATORIO)
            ffprobe_engine: Engine de FFprobe para análisis

        Raises:
            RuntimeError: Si MKVMerge no está disponible
        """
        # MKVMerge es OBLIGATORIO
        self.mkvmerge = mkvmerge_engine or MKVMergeEngine()

        # FFprobe para análisis de archivos
        try:
            self.ffprobe = ffprobe_engine or FFprobeEngine()
        except RuntimeError as e:
            print(f"⚠️ FFprobe no disponible: {e}")
            self.ffprobe = None

    def remux(
        self,
        job: RemuxJob,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> RemuxResult:
        """
        Ejecuta un remuxeo completo.

        Args:
            job: Trabajo de remuxeo
            progress_callback: Callback para reportar progreso (0-100)

        Returns:
            Resultado del remuxeo
        """
        start_time = time.time()

        try:
            # 1. Validar job
            validate_remux_job(job)

            # 2. Marcar como iniciado
            job.start()

            # 3. Ejecutar remuxeo con MKVMerge
            print(f"\n🔧 Usando MKVMerge para remuxeo")
            result = self.mkvmerge.remux(job, progress_callback)

            # 6. Actualizar estado del job
            if result.success:
                job.complete()
            else:
                job.fail(result.error_message or "Error desconocido")

            # 7. Calcular duración
            duration = time.time() - start_time
            result.duration_seconds = duration

            return result

        except ValidationError as e:
            job.fail(f"Error de validación: {str(e)}")
            return RemuxResult(
                success=False,
                error_message=str(e)
            )

        except Exception as e:
            job.fail(f"Error inesperado: {str(e)}")
            return RemuxResult(
                success=False,
                error_message=str(e)
            )

    def get_media_info(self, file_path: Path):
        """
        Obtiene información de un archivo multimedia.

        Args:
            file_path: Ruta al archivo

        Returns:
            MediaInfo con la información
        """
        return self.ffprobe.get_media_info(file_path)

    def is_available(self) -> bool:
        """
        Verifica si el servicio está disponible (MKVMerge instalado).

        Returns:
            True si MKVMerge está disponible
        """
        return self.mkvmerge is not None

    def get_engines_info(self) -> dict:
        """
        Obtiene información de los engines disponibles.

        Returns:
            Diccionario con información de engines
        """
        return {
            'mkvmerge': {
                'available': self.mkvmerge is not None,
                'version': self.mkvmerge.get_version() if self.mkvmerge else None,
                'supports_audio_offset': True,
                'supports_subtitle_offset': True
            },
            'ffprobe': {
                'available': self.ffprobe is not None,
                'version': self.ffprobe.get_version() if self.ffprobe else None
            }
        }

    def __str__(self) -> str:
        """Representación legible"""
        engines = [str(self.mkvmerge)]
        if self.ffprobe:
            engines.append(str(self.ffprobe))

        return f"RemuxService({', '.join(engines)})"
