"""
DualSync ViewModel - Lógica de presentación para DualSync Tab

Separa completamente la lógica de la UI.
"""
from pathlib import Path
from typing import Dict, Optional, Tuple
import re

from PyQt6.QtCore import pyqtSignal

from .base_viewmodel import BaseViewModel
from core.services import EpisodeMatcher, DualVideoService


class DualSyncViewModel(BaseViewModel):
    """
    ViewModel para DualSync Tab.
    
    Maneja:
    - Escaneo y matching de episodios
    - Lógica de modo (individual vs batch)
    - Preparación de trabajos de remuxeo
    """
    
    # Signals específicos
    episodes_found = pyqtSignal(dict)  # {ep_num: {'jp': path, 'lat': path}}
    mode_changed = pyqtSignal(str)  # 'single' o 'batch'
    
    def __init__(self, remux_service, episode_matcher: EpisodeMatcher):
        super().__init__(remux_service)
        self.episode_matcher = episode_matcher
        self.matched_episodes: Dict[int, Dict[str, str]] = {}
        self.current_mode = 'single'
        
        # Crear servicio de video dual
        self.dual_video_service = DualVideoService()
    
    def scan_folders(self, jp_folder: str, lat_folder: str) -> int:
        """
        Escanea carpetas y encuentra episodios coincidentes.
        
        Args:
            jp_folder: Carpeta con videos JP
            lat_folder: Carpeta con videos LAT
            
        Returns:
            Número de episodios encontrados
        """
        if not jp_folder or not lat_folder:
            self.emit_error("Faltan carpetas para escanear")
            return 0
        
        try:
            self.log("🔍 Escaneando carpetas...", "info")
            
            jp_path = Path(jp_folder)
            lat_path = Path(lat_folder)
            
            if not jp_path.exists():
                self.emit_error(f"Carpeta JP no existe: {jp_folder}")
                return 0
            
            if not lat_path.exists():
                self.emit_error(f"Carpeta LAT no existe: {lat_folder}")
                return 0
            
            # Buscar archivos
            jp_files = list(jp_path.glob("*.mkv"))
            lat_files = list(lat_path.glob("*.mkv"))
            
            self.log(f"Encontrados {len(jp_files)} videos JP", "info")
            self.log(f"Encontrados {len(lat_files)} videos LAT", "info")
            
            # Emparejar episodios
            self.matched_episodes = {}
            
            for jp_file in jp_files:
                ep_num = self._extract_episode_number(jp_file.name)
                if ep_num:
                    if ep_num not in self.matched_episodes:
                        self.matched_episodes[ep_num] = {}
                    self.matched_episodes[ep_num]['jp'] = str(jp_file)
            
            for lat_file in lat_files:
                ep_num = self._extract_episode_number(lat_file.name)
                if ep_num:
                    if ep_num not in self.matched_episodes:
                        self.matched_episodes[ep_num] = {}
                    self.matched_episodes[ep_num]['lat'] = str(lat_file)
            
            # Filtrar solo episodios completos
            complete_episodes = {
                ep: data for ep, data in self.matched_episodes.items()
                if 'jp' in data and 'lat' in data
            }
            
            self.matched_episodes = complete_episodes
            
            # Emitir resultados
            self.episodes_found.emit(self.matched_episodes)
            
            if complete_episodes:
                self.log(f"✅ Encontrados {len(complete_episodes)} episodios completos", "success")
            else:
                self.log("⚠️ No se encontraron episodios completos", "warning")
            
            return len(complete_episodes)
        
        except Exception as e:
            self.emit_error(f"Error escaneando carpetas: {str(e)}")
            return 0
    
    def _extract_episode_number(self, filename: str) -> Optional[int]:
        """
        Extrae número de episodio del nombre de archivo.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            Número de episodio o None
        """
        patterns = [
            r'[Ee](?:p|pisode)?[\s_-]?(\d{1,3})',
            r'[\s_-](\d{2,3})[\s_-]',
            r'^(\d{2,3})[\s_-]',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return int(match.group(1))
        return None
    
    def get_episode_data(self, ep_num: int) -> Optional[Dict[str, str]]:
        """
        Obtiene datos de un episodio específico.
        
        Args:
            ep_num: Número de episodio
            
        Returns:
            Dict con 'jp' y 'lat' paths o None
        """
        return self.matched_episodes.get(ep_num)
    
    def switch_to_single_mode(self):
        """Cambia a modo individual"""
        self.current_mode = 'single'
        self.mode_changed.emit('single')
        self.log("Modo: Individual (1 video)", "info")
    
    def switch_to_batch_mode(self):
        """Cambia a modo por lotes"""
        self.current_mode = 'batch'
        self.mode_changed.emit('batch')
        self.log("Modo: Lotes (múltiples episodios)", "info")
    
    def validate_single_inputs(self, jp_path: str, lat_path: str, output_path: str) -> Tuple[bool, str]:
        """
        Valida inputs para modo individual.
        
        Returns:
            (es_valido, mensaje_error)
        """
        if not jp_path:
            return False, "Falta video JP"
        if not lat_path:
            return False, "Falta video LAT"
        if not output_path:
            return False, "Falta ruta de salida"
        
        jp_file = Path(jp_path)
        lat_file = Path(lat_path)
        
        if not jp_file.exists():
            return False, f"Video JP no existe: {jp_path}"
        if not lat_file.exists():
            return False, f"Video LAT no existe: {lat_path}"
        
        return True, ""
    
    def validate_batch_inputs(self, output_folder: str) -> Tuple[bool, str]:
        """
        Valida inputs para modo batch.
        
        Returns:
            (es_valido, mensaje_error)
        """
        if not self.matched_episodes:
            return False, "No hay episodios. Escanea primero las carpetas."
        
        if not output_folder:
            return False, "Falta carpeta de salida"
        
        output_path = Path(output_folder)
        if not output_path.exists():
            return False, f"Carpeta de salida no existe: {output_folder}"
        
        return True, ""
    
    def get_episode_count(self) -> int:
        """Obtiene número de episodios emparejados"""
        return len(self.matched_episodes)
    
    def get_sorted_episode_numbers(self) -> list:
        """Obtiene lista ordenada de números de episodio"""
        return sorted(self.matched_episodes.keys())
    
    # === LÓGICA DE SINCRONIZACIÓN ===
    
    def calculate_sync_positions(self, current_pos_jp: float, audio_offset_ms: int, 
                                 rewind_amount: float = 2.0) -> tuple:
        """
        Calcula posiciones de sincronización para ambos videos.
        
        Args:
            current_pos_jp: Posición actual del video JP en segundos
            audio_offset_ms: Offset de audio en milisegundos
            rewind_amount: Cantidad a retroceder para suavizar (segundos)
            
        Returns:
            (sync_pos_jp, sync_pos_lat) en segundos
        """
        # Retroceder un poco para suavizar
        sync_pos_jp = max(0, current_pos_jp - rewind_amount)
        
        # Calcular posición LAT con offset
        offset_seconds = audio_offset_ms / 1000.0
        sync_pos_lat = sync_pos_jp - offset_seconds
        
        # No permitir posiciones negativas
        if sync_pos_lat < 0:
            sync_pos_lat = 0
        
        return (sync_pos_jp, sync_pos_lat)
    
    def calculate_subtitle_delay(self, subtitle_offset_ms: int) -> float:
        """
        Calcula el delay de subtítulos en segundos.
        
        Args:
            subtitle_offset_ms: Offset en milisegundos
            
        Returns:
            Delay en segundos
        """
        return subtitle_offset_ms / 1000.0
