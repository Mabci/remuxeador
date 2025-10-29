"""
Episode Matcher - Servicio que empareja archivos de video, audio y subtítulos por número de episodio.
"""
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from ..domain.models import Episode
from ..utils.file_utils import is_video_file, is_audio_file, is_subtitle_file


class EpisodeMatcher:
    """
    Servicio para emparejar archivos por número de episodio.
    
    Detecta números de episodio en nombres de archivo y agrupa
    archivos relacionados (video, audio, subtítulos).
    """
    
    # Patrones para detectar números de episodio (ordenados por prioridad)
    EPISODE_PATTERNS = [
        r'[Ss](\d{1,2})[Ee](\d{1,2})',           # S01E03, s01e03
        r'[Ss](\d{1,2})\s*[Ee](\d{1,2})',        # S01 E03, s01 e03
        r'(?:Episode|Episodio|Ep|E)[\s_-]*(\d{1,3})',  # Episode 03, Ep03, E03
        r'[\s_-](\d{2,3})[\s_\[\(]',             # " 03 ", "_03_", " 03[", " 03("
        r'^(\d{2,3})[\s_\.-]',                   # "03 ", "03_", "03.", "03-"
        r'[\s_-](\d{2,3})$',                     # " 03", "_03" (final)
        r'[\s_-](\d{2,3})[\s_\.-]',              # " 03 ", "_03_", " 03.", " 03-"
    ]
    
    # Patrones para detectar subtítulos forzados (letreros)
    FORCED_PATTERNS = [
        r'forced',
        r'letreros',
        r'signs',
        r'signs?\s*&\s*songs?',
    ]
    
    def __init__(self):
        """Inicializa el matcher compilando patrones"""
        self.episode_patterns = [re.compile(p, re.IGNORECASE) for p in self.EPISODE_PATTERNS]
        self.forced_patterns = [re.compile(p, re.IGNORECASE) for p in self.FORCED_PATTERNS]
    
    def extract_episode_number(self, filename: str) -> Optional[int]:
        """
        Extrae el número de episodio de un nombre de archivo.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            Número de episodio o None si no se encuentra
        """
        # Probar cada patrón en orden de prioridad
        for pattern in self.episode_patterns:
            match = pattern.search(filename)
            if match:
                groups = match.groups()
                
                # Si hay 2 grupos, es formato S01E03 (temporada, episodio)
                if len(groups) == 2:
                    return int(groups[1])  # Retornar solo episodio
                else:
                    return int(groups[0])
        
        return None
    
    def is_forced_subtitle(self, filename: str) -> bool:
        """
        Verifica si un archivo de subtítulos es forzado (letreros).
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            True si es subtítulo forzado
        """
        filename_lower = filename.lower()
        return any(pattern.search(filename_lower) for pattern in self.forced_patterns)
    
    def group_files_by_episode(
        self,
        video_files: List[Path],
        audio_files: List[Path],
        subtitle_files: List[Path]
    ) -> Dict[int, Episode]:
        """
        Agrupa archivos por número de episodio.
        
        Args:
            video_files: Lista de archivos de video
            audio_files: Lista de archivos de audio
            subtitle_files: Lista de archivos de subtítulos
            
        Returns:
            Diccionario {episodio_num: Episode}
        """
        episodes: Dict[int, Episode] = {}
        
        # Procesar videos
        for video in video_files:
            if not is_video_file(video):
                continue
            
            ep_num = self.extract_episode_number(video.name)
            if ep_num is not None:
                if ep_num not in episodes:
                    episodes[ep_num] = Episode(number=ep_num)
                episodes[ep_num].video_file = video
        
        # Procesar audios
        for audio in audio_files:
            if not is_audio_file(audio):
                continue
            
            ep_num = self.extract_episode_number(audio.name)
            if ep_num is not None:
                if ep_num not in episodes:
                    episodes[ep_num] = Episode(number=ep_num)
                episodes[ep_num].audio_files.append(audio)
        
        # Procesar subtítulos
        for subtitle in subtitle_files:
            if not is_subtitle_file(subtitle):
                continue
            
            ep_num = self.extract_episode_number(subtitle.name)
            if ep_num is not None:
                if ep_num not in episodes:
                    episodes[ep_num] = Episode(number=ep_num)
                
                # Determinar si es forzado
                if self.is_forced_subtitle(subtitle.name):
                    episodes[ep_num].forced_subtitle_files.append(subtitle)
                else:
                    episodes[ep_num].subtitle_files.append(subtitle)
        
        return episodes
    
    def scan_directory(
        self,
        directory: Path,
        recursive: bool = False
    ) -> Dict[int, Episode]:
        """
        Escanea un directorio y agrupa archivos por episodio.
        
        Args:
            directory: Directorio a escanear
            recursive: Si True, busca recursivamente
            
        Returns:
            Diccionario {episodio_num: Episode}
        """
        if not directory.exists() or not directory.is_dir():
            return {}
        
        # Buscar archivos
        pattern = "**/*" if recursive else "*"
        all_files = list(directory.glob(pattern))
        
        # Separar por tipo
        video_files = [f for f in all_files if is_video_file(f)]
        audio_files = [f for f in all_files if is_audio_file(f)]
        subtitle_files = [f for f in all_files if is_subtitle_file(f)]
        
        # Agrupar
        return self.group_files_by_episode(video_files, audio_files, subtitle_files)
    
    def validate_episode(self, episode: Episode) -> Tuple[bool, str]:
        """
        Valida que un episodio esté completo.
        
        Args:
            episode: Episodio a validar
            
        Returns:
            (es_valido, mensaje)
        """
        if not episode.is_complete:
            return False, "❌ Falta archivo de video"
        
        # Advertencias (no errores)
        warnings = []
        if not episode.has_audio:
            warnings.append("Sin audio externo")
        if not episode.has_subtitles:
            warnings.append("Sin subtítulos externos")
        
        if warnings:
            return True, f"⚠️ {', '.join(warnings)}"
        
        return True, "✅ Completo"
    
    def get_summary(self, episodes: Dict[int, Episode]) -> str:
        """
        Genera un resumen legible de los episodios encontrados.
        
        Args:
            episodes: Diccionario de episodios
            
        Returns:
            String con el resumen
        """
        if not episodes:
            return "No se encontraron episodios para emparejar"
        
        lines = [f"📺 Se encontraron {len(episodes)} episodios:\n"]
        
        for ep_num in sorted(episodes.keys()):
            episode = episodes[ep_num]
            is_valid, status = self.validate_episode(episode)
            
            lines.append(f"\nEpisodio {ep_num:02d} - {status}")
            
            if episode.video_file:
                lines.append(f"  📹 Video: {episode.video_file.name}")
            
            for audio in episode.audio_files:
                lines.append(f"  🎵 Audio: {audio.name}")
            
            for subtitle in episode.subtitle_files:
                lines.append(f"  📝 Sub: {subtitle.name}")
            
            for forced in episode.forced_subtitle_files:
                lines.append(f"  🔤 Letreros: {forced.name}")
        
        return "\n".join(lines)
    
    def filter_complete_episodes(
        self,
        episodes: Dict[int, Episode]
    ) -> Dict[int, Episode]:
        """
        Filtra solo los episodios completos (con video).
        
        Args:
            episodes: Diccionario de episodios
            
        Returns:
            Diccionario solo con episodios completos
        """
        return {
            num: ep 
            for num, ep in episodes.items() 
            if ep.is_complete
        }
    
    def get_episode_range(
        self,
        episodes: Dict[int, Episode]
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Obtiene el rango de episodios (mínimo y máximo).
        
        Args:
            episodes: Diccionario de episodios
            
        Returns:
            (min_episode, max_episode) o (None, None) si está vacío
        """
        if not episodes:
            return None, None
        
        episode_numbers = list(episodes.keys())
        return min(episode_numbers), max(episode_numbers)
    
    def __str__(self) -> str:
        """Representación legible"""
        return f"EpisodeMatcher({len(self.episode_patterns)} patterns)"


# Función de utilidad para testing
def test_episode_matcher():
    """Función de prueba del matcher"""
    matcher = EpisodeMatcher()
    
    test_cases = [
        "Anime - S01E03 - Title.mkv",
        "[Group] Anime - 03 [1080p].mp4",
        "Anime Episode 12.mkv",
        "03_audio_latino.m4a",
        "Anime_Ep_05_subs.ass",
        "anime-07-forced.ass",
    ]
    
    print("🧪 Pruebas de EpisodeMatcher:\n")
    for test in test_cases:
        ep_num = matcher.extract_episode_number(test)
        is_forced = matcher.is_forced_subtitle(test)
        print(f"Archivo: {test}")
        print(f"  Episodio: {ep_num}")
        print(f"  Forzado: {is_forced}\n")


if __name__ == "__main__":
    test_episode_matcher()
