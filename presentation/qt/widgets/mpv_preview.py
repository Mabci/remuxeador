"""
MPV Preview Widget - Preview de un solo video con MPV

Widget para mostrar preview de video con controles basicos.
Permite cargar video, audios y subtitulos.
"""
from PyQt6.QtWidgets import QWidget, QFrame
from PyQt6.QtCore import pyqtSignal
import platform

try:
    import mpv
    MPV_AVAILABLE = True
except (ImportError, OSError) as e:
    MPV_AVAILABLE = False
    print(f"⚠️ MPV no disponible: {e}")
    print("⚠️ Asegúrate de tener libmpv instalado y en el PATH del sistema")


class MPVPreviewWidget(QWidget):
    """
    Widget de preview con MPV para un solo video.
    
    Permite:
    - Cargar video
    - Agregar audios externos
    - Agregar subtitulos externos
    - Controles basicos (play/pause/seek)
    """
    
    # Signals
    time_pos_changed = pyqtSignal(float, float)  # (pos, duration)
    log_signal = pyqtSignal(str, str)  # (mensaje, nivel)
    
    def __init__(self, preview_frame: QFrame, parent=None):
        super().__init__(parent)
        
        self.preview_frame = preview_frame
        self.mpv = None
        self.is_playing = False
        self.current_video = None
        
        # Inicializar MPV
        self._init_mpv()
    
    def _init_mpv(self):
        """Inicializa MPV"""
        if not MPV_AVAILABLE:
            self.log_signal.emit("❌ MPV no disponible", "error")
            return
        
        try:
            if platform.system() == 'Windows':
                wid = int(self.preview_frame.winId())
                self.mpv = mpv.MPV(
                    wid=str(wid),
                    keep_open='yes',
                    idle=True,
                    sub_auto='no',
                    hr_seek='yes',
                    hr_seek_framedrop='no'
                )
            else:
                self.mpv = mpv.MPV(
                    keep_open='yes',
                    idle=True,
                    sub_auto='no',
                    hr_seek='yes',
                    hr_seek_framedrop='no'
                )
            
            self.log_signal.emit("✅ MPV inicializado", "success")
        
        except Exception as e:
            self.log_signal.emit(f"❌ Error inicializando MPV: {str(e)}", "error")
            self.mpv = None
    
    def load_video(self, video_path: str):
        """
        Carga un video en el preview.
        
        Args:
            video_path: Ruta al video
        """
        if not self.mpv:
            self.log_signal.emit("❌ MPV no disponible", "error")
            return
        
        try:
            self.mpv.loadfile(video_path)
            self.current_video = video_path
            self.is_playing = False
            self.log_signal.emit(f"✅ Video cargado: {video_path}", "success")
        
        except Exception as e:
            self.log_signal.emit(f"❌ Error cargando video: {str(e)}", "error")
    
    def add_audio(self, audio_path: str, select=True):
        """
        Agrega un audio externo.
        
        Args:
            audio_path: Ruta al audio
            select: Si True, selecciona este audio
        """
        if not self.mpv:
            return
        
        try:
            self.mpv.audio_add(audio_path, select='yes' if select else 'no')
            self.log_signal.emit(f"✅ Audio agregado: {audio_path}", "success")
        
        except Exception as e:
            self.log_signal.emit(f"❌ Error agregando audio: {str(e)}", "error")
    
    def add_subtitle(self, subtitle_path: str, select=True):
        """
        Agrega subtitulos externos.
        
        Args:
            subtitle_path: Ruta a subtitulos
            select: Si True, selecciona estos subtitulos
        """
        if not self.mpv:
            return
        
        try:
            self.mpv.sub_add(subtitle_path, select='yes' if select else 'no')
            self.log_signal.emit(f"✅ Subtitulos agregados: {subtitle_path}", "success")
        
        except Exception as e:
            self.log_signal.emit(f"❌ Error agregando subtitulos: {str(e)}", "error")
    
    def toggle_play(self):
        """Toggle play/pause"""
        if not self.mpv:
            return
        
        self.is_playing = not self.is_playing
        self.mpv.pause = not self.is_playing
    
    def stop(self):
        """Detiene y reinicia"""
        if not self.mpv:
            return
        
        self.mpv.seek(0, reference='absolute')
        self.mpv.pause = True
        self.is_playing = False
    
    def seek(self, seconds: float):
        """
        Navega en el video.
        
        Args:
            seconds: Segundos a avanzar/retroceder (puede ser negativo)
        """
        if not self.mpv:
            return
        
        self.mpv.seek(seconds, reference='relative')
    
    def set_audio_track(self, track_id: int):
        """
        Selecciona una pista de audio.
        
        Args:
            track_id: ID de la pista (1-indexed)
        """
        if not self.mpv:
            return
        
        self.mpv.aid = track_id
    
    def set_subtitle_track(self, track_id: int):
        """
        Selecciona una pista de subtitulos.
        
        Args:
            track_id: ID de la pista (1-indexed)
        """
        if not self.mpv:
            return
        
        self.mpv.sid = track_id
    
    def load_external_audio(self, audio_path: str):
        """
        Carga un archivo de audio externo.
        
        Args:
            audio_path: Ruta al archivo de audio
        """
        if not self.mpv:
            return
        
        try:
            # MPV requiere rutas absolutas y con formato correcto
            import os
            abs_path = os.path.abspath(audio_path)
            
            # Usar el comando correcto de MPV
            # El tercer parámetro puede ser: 'select', 'auto', 'cached'
            # 'select' = agregar y seleccionar automáticamente
            self.mpv.command('audio-add', abs_path, 'select')
            print(f"✅ Audio externo agregado: {abs_path}")
        except Exception as e:
            print(f"❌ Error al cargar audio externo: {e}")
            import traceback
            traceback.print_exc()
    
    def load_external_subtitle(self, subtitle_path: str):
        """
        Carga un archivo de subtítulos externo.
        
        Args:
            subtitle_path: Ruta al archivo de subtítulos
        """
        if not self.mpv:
            return
        
        try:
            # MPV requiere rutas absolutas y con formato correcto
            import os
            abs_path = os.path.abspath(subtitle_path)
            
            # Usar el comando correcto de MPV
            # El tercer parámetro puede ser: 'select', 'auto', 'cached'
            # 'auto' = agregar sin seleccionar automáticamente
            self.mpv.command('sub-add', abs_path, 'auto')
            print(f"✅ Subtítulos externos agregados: {abs_path}")
        except Exception as e:
            print(f"❌ Error al cargar subtítulos externos: {e}")
            import traceback
            traceback.print_exc()
    
    def set_audio_delay(self, delay_ms: int):
        """
        Establece el delay/offset del audio.
        
        Args:
            delay_ms: Delay en milisegundos (positivo = adelantar, negativo = atrasar)
        """
        if not self.mpv:
            return
        
        try:
            # MPV usa segundos, convertir de milisegundos
            delay_seconds = delay_ms / 1000.0
            self.mpv.audio_delay = delay_seconds
        except Exception as e:
            print(f"Error al establecer delay de audio: {e}")
    
    def set_subtitle_delay(self, delay_ms: int):
        """
        Establece el delay/offset de los subtítulos.
        
        Args:
            delay_ms: Delay en milisegundos (positivo = adelantar, negativo = atrasar)
        """
        if not self.mpv:
            return
        
        try:
            # MPV usa segundos, convertir de milisegundos
            delay_seconds = delay_ms / 1000.0
            self.mpv.sub_delay = delay_seconds
        except Exception as e:
            print(f"Error al establecer delay de subtítulos: {e}")
    
    def get_audio_tracks(self):
        """Retorna lista de pistas de audio disponibles"""
        if not self.mpv:
            return []
        
        try:
            track_list = self.mpv.track_list
            return [t for t in track_list if t.get('type') == 'audio']
        except:
            return []
    
    def get_subtitle_tracks(self):
        """Retorna lista de pistas de subtitulos disponibles"""
        if not self.mpv:
            return []
        
        try:
            track_list = self.mpv.track_list
            return [t for t in track_list if t.get('type') == 'sub']
        except:
            return []
    
    def cleanup(self):
        """Limpia recursos"""
        if self.mpv:
            try:
                self.mpv.terminate()
            except:
                pass
            self.mpv = None
