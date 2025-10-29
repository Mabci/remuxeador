"""
MPV Dual Preview Widget - Widget con MPV embebido

Maneja toda la lógica de MPV separada de la UI principal.
"""
from PyQt6.QtWidgets import QWidget, QFrame
from PyQt6.QtCore import QTimer, pyqtSignal
import platform
from pathlib import Path


class MPVDualPreviewWidget(QWidget):
    """
    Widget que maneja dos instancias de MPV para preview dual.
    
    Encapsula toda la lógica de MPV, sincronización y control de reproducción.
    """
    
    # Signals
    log_signal = pyqtSignal(str, str)  # (mensaje, nivel)
    timestamps_updated = pyqtSignal(str, str)  # (time_jp, time_lat)
    
    def __init__(self, preview_jp_frame: QFrame, preview_lat_frame: QFrame, parent=None):
        super().__init__(parent)
        
        # Frames donde se embebe MPV
        self.preview_jp_frame = preview_jp_frame
        self.preview_lat_frame = preview_lat_frame
        
        # MPV instances
        self.mpv_jp = None
        self.mpv_lat = None
        self.current_video_jp = None
        self.current_video_lat = None
        self.is_playing = False
        
        # Timer para timestamps
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timestamps)
    
    def load_videos(self, video_jp_path: str, video_lat_path: str):
        """
        Carga ambos videos en MPV.
        
        Args:
            video_jp_path: Ruta al video japonés
            video_lat_path: Ruta al video latino
        """
        try:
            self.log_signal.emit(f"Cargando Video 1: {video_jp_path}", "info")
            self.log_signal.emit(f"Cargando Video 2: {video_lat_path}", "info")
            
            # Inicializar MPV si es necesario
            if not self.mpv_jp:
                self._init_mpv_jp()
            if not self.mpv_lat:
                self._init_mpv_lat()
            
            # Cargar videos
            self.mpv_jp.play(video_jp_path)
            self.mpv_jp.pause = True
            
            self.mpv_lat.play(video_lat_path)
            self.mpv_lat.pause = True
            
            import time
            time.sleep(0.3)
            
            # Por defecto: JP muted, LAT audible
            self.mpv_jp.mute = True
            self.mpv_lat.mute = False
            
            # Cargar subtítulos del video LAT en el preview JP
            self._load_subtitles_to_jp(video_lat_path)
            
            self.current_video_jp = video_jp_path
            self.current_video_lat = video_lat_path
            
            # Iniciar timer de timestamps
            self.timer.start(500)
            
            self.log_signal.emit("✅ Previews cargados", "success")
            
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}", "error")
            raise
    
    def _init_mpv_jp(self):
        """Inicializa MPV para video JP con subtítulos habilitados"""
        import mpv
        
        if platform.system() == 'Windows':
            wid = int(self.preview_jp_frame.winId())
            self.mpv_jp = mpv.MPV(
                wid=str(wid), 
                keep_open='yes', 
                idle=True,
                sub_auto='no',
                hr_seek='yes',
                hr_seek_framedrop='no'
            )
        else:
            self.mpv_jp = mpv.MPV(
                keep_open='yes', 
                idle=True,
                sub_auto='no',
                hr_seek='yes',
                hr_seek_framedrop='no'
            )
    
    def _init_mpv_lat(self):
        """Inicializa MPV para video LAT SIN subtítulos"""
        import mpv
        
        if platform.system() == 'Windows':
            wid = int(self.preview_lat_frame.winId())
            self.mpv_lat = mpv.MPV(
                wid=str(wid), 
                keep_open='yes', 
                idle=True,
                sub_auto='no',
                hr_seek='yes',
                hr_seek_framedrop='no'
            )
        else:
            self.mpv_lat = mpv.MPV(
                keep_open='yes', 
                idle=True,
                sub_auto='no',
                hr_seek='yes',
                hr_seek_framedrop='no'
            )
    
    def _load_subtitles_to_jp(self, video_lat_path: str):
        """Carga los subtítulos del video LAT en el preview JP"""
        try:
            import os
            
            base_path = os.path.splitext(video_lat_path)[0]
            subtitle_extensions = ['.ass', '.ssa', '.srt', '.sub']
            
            subtitle_file = None
            for ext in subtitle_extensions:
                potential_sub = base_path + ext
                if os.path.exists(potential_sub):
                    subtitle_file = potential_sub
                    self.log_signal.emit(f"✅ Encontrado: {potential_sub}", "success")
                    break
            
            if subtitle_file:
                import time
                
                self.log_signal.emit(f"Cargando subtítulos en Video 1: {subtitle_file}", "info")
                
                self.mpv_jp.sub_add(subtitle_file, select=True)
                time.sleep(0.1)
                
                self.mpv_jp.sid = 1
                self.mpv_jp.sub_visibility = True
                
                try:
                    track_list = self.mpv_jp.track_list
                    sub_tracks = [t for t in track_list if t.get('type') == 'sub']
                    self.log_signal.emit(f"✅ Subtítulos cargados: {os.path.basename(subtitle_file)} ({len(sub_tracks)} pistas)", "success")
                except:
                    self.log_signal.emit(f"✅ Subtítulos cargados: {os.path.basename(subtitle_file)}", "success")
            else:
                self.log_signal.emit("⚠ No se encontró archivo de subtítulos externo", "warning")
                    
        except Exception as e:
            self.log_signal.emit(f"Error cargando subtítulos: {str(e)}", "error")
    
    def apply_sync(self, audio_offset_ms: int, subtitle_offset_ms: int):
        """
        Aplica sincronización con ALTA PRECISIÓN.
        
        Args:
            audio_offset_ms: Offset de audio en milisegundos
            subtitle_offset_ms: Offset de subtítulos en milisegundos
        """
        if not self.mpv_jp or not self.mpv_lat:
            return
        
        if not self.current_video_jp or not self.current_video_lat:
            return
        
        try:
            import time
            
            current_pos_jp = self.mpv_jp.time_pos or 0
            was_playing = self.is_playing
            
            # Pausar ambos
            self.mpv_jp.pause = True
            self.mpv_lat.pause = True
            time.sleep(0.05)
            
            # Retroceder un poco para suavizar
            rewind_amount = 2.0
            sync_pos_jp = max(0, current_pos_jp - rewind_amount)
            
            # Calcular posición LAT con offset
            offset_seconds = audio_offset_ms / 1000.0
            sync_pos_lat = sync_pos_jp - offset_seconds
            
            if sync_pos_lat < 0:
                sync_pos_lat = 0
            
            # Seek con precisión exacta
            self.mpv_jp.seek(sync_pos_jp, reference='absolute', precision='exact')
            self.mpv_lat.seek(sync_pos_lat, reference='absolute', precision='exact')
            
            time.sleep(0.2)
            
            # Aplicar subtitle delay
            if subtitle_offset_ms != 0:
                subtitle_delay = subtitle_offset_ms / 1000.0
                self.mpv_jp.sub_delay = subtitle_delay
                self.log_signal.emit(f"Subtitle delay aplicado: {subtitle_delay:.3f}s", "info")
            
            # Reanudar si estaba reproduciendo
            if was_playing:
                time.sleep(0.05)
                self.mpv_jp.pause = False
                self.mpv_lat.pause = False
            
            self.log_signal.emit(f"✓ Sync: JP={sync_pos_jp:.3f}s, LAT={sync_pos_lat:.3f}s (offset={audio_offset_ms}ms)", "success")
            
        except Exception as e:
            self.log_signal.emit(f"Error en sync: {str(e)}", "error")
    
    def apply_subtitle_offset(self, subtitle_offset_ms: int):
        """Aplica solo el offset de subtítulos"""
        if self.mpv_jp:
            subtitle_delay = subtitle_offset_ms / 1000.0
            self.mpv_jp.sub_delay = subtitle_delay
            self.log_signal.emit(f"Subtitle delay: {subtitle_delay:.3f}s", "info")
    
    def toggle_play(self):
        """Toggle play/pause"""
        if not self.mpv_jp or not self.mpv_lat:
            return
        
        self.is_playing = not self.is_playing
        self.mpv_jp.pause = not self.is_playing
        self.mpv_lat.pause = not self.is_playing
    
    def stop(self):
        """Detiene y reinicia"""
        if not self.mpv_jp or not self.mpv_lat:
            return
        
        self.mpv_jp.seek(0, reference='absolute')
        self.mpv_lat.seek(0, reference='absolute')
        self.mpv_jp.pause = True
        self.mpv_lat.pause = True
        self.is_playing = False
    
    def seek(self, seconds: int):
        """Navega en ambos videos"""
        if not self.mpv_jp or not self.mpv_lat:
            return
        
        self.mpv_jp.seek(seconds, reference='relative')
        self.mpv_lat.seek(seconds, reference='relative')
    
    def toggle_mute_jp(self) -> bool:
        """Toggle mute JP. Returns nuevo estado (True = muted)"""
        if not self.mpv_jp:
            return False
        
        self.mpv_jp.mute = not self.mpv_jp.mute
        return self.mpv_jp.mute
    
    def toggle_mute_lat(self) -> bool:
        """Toggle mute LAT. Returns nuevo estado (True = muted)"""
        if not self.mpv_lat:
            return False
        
        self.mpv_lat.mute = not self.mpv_lat.mute
        return self.mpv_lat.mute
    
    def _update_timestamps(self):
        """Actualiza timestamps y emite signal"""
        try:
            time_jp = "0:00:00/0:00:00"
            time_lat = "0:00:00/0:00:00"
            
            if self.mpv_jp and self.current_video_jp:
                pos = self.mpv_jp.time_pos or 0
                dur = self.mpv_jp.duration or 0
                time_jp = f"Time: {self._format_time(pos)}/{self._format_time(dur)}"
            
            if self.mpv_lat and self.current_video_lat:
                pos = self.mpv_lat.time_pos or 0
                dur = self.mpv_lat.duration or 0
                time_lat = f"Time: {self._format_time(pos)}/{self._format_time(dur)}"
            
            self.timestamps_updated.emit(time_jp, time_lat)
        except:
            pass
    
    def _format_time(self, seconds: float) -> str:
        """Formatea segundos a H:MM:SS"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h}:{m:02d}:{s:02d}"
    
    def cleanup(self):
        """Limpia recursos"""
        self.timer.stop()
        if self.mpv_jp:
            try:
                self.mpv_jp.terminate()
            except:
                pass
        if self.mpv_lat:
            try:
                self.mpv_lat.terminate()
            except:
                pass
