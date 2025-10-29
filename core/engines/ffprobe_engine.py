"""
FFprobe Engine - Análisis de archivos multimedia

Engine especializado en obtener información de archivos multimedia.
"""
import json
import subprocess
import re
from pathlib import Path
from typing import Optional, List

from ..domain.models import MediaInfo, Track
from ..domain.enums import TrackType, CodecType, LanguageCode


class FFprobeEngine:
    """
    Engine para analizar archivos multimedia con FFprobe.
    
    Solo se encarga de obtener información, no de procesamiento.
    """
    
    def __init__(self, ffprobe_path: str = "ffprobe"):
        """
        Inicializa el engine de FFprobe.
        
        Args:
            ffprobe_path: Ruta al ejecutable de ffprobe
        """
        self.ffprobe_path = ffprobe_path
        self._validate_installation()
    
    def get_media_info(self, file_path: Path) -> Optional[MediaInfo]:
        """
        Obtiene información completa de un archivo multimedia.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            MediaInfo con toda la información o None si falla
        """
        try:
            # Ejecutar ffprobe
            cmd = [
                self.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                "-show_format",
                str(file_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
            
            # Parsear JSON
            data = json.loads(result.stdout)
            
            # Extraer información
            format_info = data.get('format', {})
            streams = data.get('streams', [])
            
            # Procesar pistas
            video_tracks = []
            audio_tracks = []
            subtitle_tracks = []
            
            for stream in streams:
                track = self._parse_stream(stream)
                if track:
                    if track.type == TrackType.VIDEO:
                        video_tracks.append(track)
                    elif track.type == TrackType.AUDIO:
                        audio_tracks.append(track)
                    elif track.type == TrackType.SUBTITLE:
                        subtitle_tracks.append(track)
            
            # Crear MediaInfo
            return MediaInfo(
                file_path=file_path,
                duration=float(format_info.get('duration', 0)),
                format_name=format_info.get('format_name', 'unknown'),
                size_bytes=int(format_info.get('size', 0)),
                video_tracks=video_tracks,
                audio_tracks=audio_tracks,
                subtitle_tracks=subtitle_tracks,
                metadata=format_info.get('tags', {})
            )
        
        except Exception as e:
            print(f"Error obteniendo info de {file_path}: {e}")
            return None
    
    def get_duration(self, file_path: Path) -> Optional[float]:
        """
        Obtiene solo la duración de un archivo.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Duración en segundos o None
        """
        info = self.get_media_info(file_path)
        return info.duration if info else None
    
    def has_video(self, file_path: Path) -> bool:
        """
        Verifica si un archivo tiene pistas de video.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si tiene video
        """
        info = self.get_media_info(file_path)
        return info.has_video if info else False
    
    def has_audio(self, file_path: Path) -> bool:
        """
        Verifica si un archivo tiene pistas de audio.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si tiene audio
        """
        info = self.get_media_info(file_path)
        return info.has_audio if info else False
    
    def _parse_stream(self, stream: dict) -> Optional[Track]:
        """
        Parsea un stream de FFprobe a un objeto Track.
        
        Args:
            stream: Diccionario con información del stream
            
        Returns:
            Track o None si no se puede parsear
        """
        try:
            codec_type = stream.get('codec_type', '')
            
            # Determinar tipo de pista
            if codec_type == 'video':
                track_type = TrackType.VIDEO
            elif codec_type == 'audio':
                track_type = TrackType.AUDIO
            elif codec_type == 'subtitle':
                track_type = TrackType.SUBTITLE
            else:
                return None
            
            # Extraer información
            track_id = stream.get('index', 0)
            codec = stream.get('codec_name', 'unknown')
            
            # Idioma
            tags = stream.get('tags', {})
            lang_str = tags.get('language', 'und')
            language = self._parse_language(lang_str)
            
            # Título
            title = tags.get('title')
            
            # Bitrate
            bitrate = stream.get('bit_rate')
            if bitrate:
                bitrate = int(bitrate)
            
            # Duración
            duration = stream.get('duration')
            if duration:
                duration = float(duration)
            
            # Crear Track
            return Track(
                id=track_id,
                type=track_type,
                codec=codec,
                language=language,
                title=title,
                bitrate=bitrate,
                duration=duration
            )
        
        except Exception as e:
            print(f"Error parseando stream: {e}")
            return None
    
    def _parse_language(self, lang_str: str) -> LanguageCode:
        """
        Parsea códigos de idioma (ISO 639-1, ISO 639-2, y variantes regionales).
        
        Soporta:
        - ISO 639-1 (2 letras): ja, es, en, pt, etc.
        - ISO 639-2 (3 letras): jpn, spa, eng, por, etc.
        - Variantes regionales: es-419, es-ES, en-US, pt-BR, etc.
        - Nombres en inglés: japanese, spanish, english, etc.
        
        Args:
            lang_str: String con código de idioma
            
        Returns:
            LanguageCode correspondiente
        """
        if not lang_str:
            return LanguageCode.UNKNOWN
        
        lang_lower = lang_str.lower().strip()
        
        # Mapeo completo de códigos
        lang_map = {
            # Japonés
            'jpn': LanguageCode.JAPANESE,
            'ja': LanguageCode.JAPANESE,
            'japanese': LanguageCode.JAPANESE,
            
            # Español (con detección de variantes)
            'spa': LanguageCode.SPANISH,
            'es': LanguageCode.SPANISH,
            'es-419': LanguageCode.SPANISH_LATIN,
            'es-mx': LanguageCode.SPANISH_MEXICO,
            'es-es': LanguageCode.SPANISH_SPAIN,
            'spanish': LanguageCode.SPANISH,
            'spanish (latin america)': LanguageCode.SPANISH_LATIN,
            'spanish (spain)': LanguageCode.SPANISH_SPAIN,
            
            # Inglés (con variantes)
            'eng': LanguageCode.ENGLISH,
            'en': LanguageCode.ENGLISH,
            'en-us': LanguageCode.ENGLISH_US,
            'en-gb': LanguageCode.ENGLISH_UK,
            'english': LanguageCode.ENGLISH,
            'english (us)': LanguageCode.ENGLISH_US,
            'english (uk)': LanguageCode.ENGLISH_UK,
            
            # Portugués (con variantes)
            'por': LanguageCode.PORTUGUESE,
            'pt': LanguageCode.PORTUGUESE,
            'pt-br': LanguageCode.PORTUGUESE_BR,
            'pt-pt': LanguageCode.PORTUGUESE_PT,
            'portuguese': LanguageCode.PORTUGUESE,
            'portuguese (brazil)': LanguageCode.PORTUGUESE_BR,
            'portuguese (portugal)': LanguageCode.PORTUGUESE_PT,
            
            # Francés
            'fre': LanguageCode.FRENCH,
            'fra': LanguageCode.FRENCH,
            'fr': LanguageCode.FRENCH,
            'french': LanguageCode.FRENCH,
            
            # Alemán
            'ger': LanguageCode.GERMAN,
            'deu': LanguageCode.GERMAN,
            'de': LanguageCode.GERMAN,
            'german': LanguageCode.GERMAN,
            
            # Italiano
            'ita': LanguageCode.ITALIAN,
            'it': LanguageCode.ITALIAN,
            'italian': LanguageCode.ITALIAN,
            
            # Chino
            'chi': LanguageCode.CHINESE,
            'zho': LanguageCode.CHINESE,
            'zh': LanguageCode.CHINESE,
            'chinese': LanguageCode.CHINESE,
            
            # Coreano
            'kor': LanguageCode.KOREAN,
            'ko': LanguageCode.KOREAN,
            'korean': LanguageCode.KOREAN,
            
            # Ruso
            'rus': LanguageCode.RUSSIAN,
            'ru': LanguageCode.RUSSIAN,
            'russian': LanguageCode.RUSSIAN,
            
            # Árabe
            'ara': LanguageCode.ARABIC,
            'ar': LanguageCode.ARABIC,
            'arabic': LanguageCode.ARABIC,
        }
        
        return lang_map.get(lang_lower, LanguageCode.UNKNOWN)
    
    def is_available(self) -> bool:
        """
        Verifica si FFprobe está disponible.
        
        Returns:
            True si está disponible
        """
        try:
            result = subprocess.run(
                [self.ffprobe_path, "-version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def get_version(self) -> Optional[str]:
        """
        Obtiene la versión de FFprobe.
        
        Returns:
            String con la versión o None
        """
        try:
            result = subprocess.run(
                [self.ffprobe_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parsear versión: ffprobe version N-xxxxx
                match = re.search(r'ffprobe version ([^\s]+)', result.stdout)
                if match:
                    return match.group(1)
        except:
            pass
        return None
    
    def _validate_installation(self) -> None:
        """
        Valida que FFprobe está instalado.
        
        Raises:
            RuntimeError: Si FFprobe no está disponible
        """
        if not self.is_available():
            raise RuntimeError(
                f"FFprobe no está disponible. "
                f"Verifica que '{self.ffprobe_path}' está instalado."
            )
    
    def __str__(self) -> str:
        """Representación legible"""
        version = self.get_version()
        return f"FFprobeEngine(v{version})" if version else "FFprobeEngine"
