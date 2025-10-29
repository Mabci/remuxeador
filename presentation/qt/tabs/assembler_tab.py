"""
Assembler Tab - Ensamblar video con pistas externas

Permite ensamblar un video agregando:
- Audio externo en español latino
- Subtítulos externos en español latino
- Letreros (forced subtitles)

Integra:
- MPVPreviewWidget para preview de video
- Selectores de archivos externos
- Controles de offset con botones +/-
- AssemblerUIBuilder para la UI
"""
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from pathlib import Path

from ..ui_builders.assembler_layout_builder import AssemblerLayoutBuilder
from ..widgets.mpv_preview import MPVPreviewWidget
from ..viewmodels.assembler_viewmodel import AssemblerViewModel
from core.domain.models import RemuxJob, Track
from core.domain.enums import TrackType, LanguageCode


class AssemblerTab(QWidget):
    """
    Tab Assembler - Ensamblar video con pistas externas.
    
    Permite:
    - Cargar video base
    - Agregar audio externo (español latino)
    - Agregar subtítulos externos (español latino)
    - Agregar letreros/forced subtitles
    - Preview con MPV
    - Ajuste de offsets con botones +/-
    - Remuxeo sin re-encoding
    """
    
    def __init__(self, viewmodel: AssemblerViewModel, parent=None):
        super().__init__(parent)
        
        self.viewmodel = viewmodel
        self.is_folder_mode = False
        self.current_video_path = None
        self.episodes = {}  # Diccionario de episodios escaneados
        
        # Construir UI
        self._build_ui()
        
        # Conectar signals
        self._connect_signals()
    
    def _build_ui(self):
        """Construye la interfaz usando AssemblerLayoutBuilder"""
        # Usar el nuevo layout builder
        layout_builder = AssemblerLayoutBuilder(self)
        self.widgets = layout_builder.build_widgets()
        
        # Crear MPV widget dentro del frame de preview
        preview_frame = self.widgets.preview_panel.get_preview_frame()
        self.mpv_widget = MPVPreviewWidget(preview_frame, self)
        
        # Referencias directas a widgets comunes
        self.sync_controls = self.widgets.sync_controls
        self.console = self.widgets.console
        self.progress_panel = self.widgets.progress_panel
    
    def _connect_signals(self):
        """Conecta todos los signals"""
        # FileInputGroup signals (detectar cambios de modo)
        self.widgets.video_input.file_selected.connect(lambda p: self._set_folder_mode(False))
        self.widgets.video_input.folder_selected.connect(lambda p: self._set_folder_mode(True))
        self.widgets.video_input.path_changed.connect(self._on_video_path_changed)
        
        # Escaneo (modo carpetas)
        self.widgets.scan_btn.clicked.connect(self._scan_folders)
        self.widgets.episode_combo.currentIndexChanged.connect(self._on_episode_changed)
        
        # Botón de cargar preview
        self.widgets.load_preview_btn.clicked.connect(self._load_preview)
        
        # Preview panel signals
        self.widgets.preview_panel.play_clicked.connect(self._toggle_play)
        self.widgets.preview_panel.stop_clicked.connect(self._stop_preview)
        self.widgets.preview_panel.seek_requested.connect(self._seek)
        
        # Selectores de pistas
        self.widgets.audio_track_combo.currentIndexChanged.connect(self._on_audio_track_changed)
        self.widgets.subtitle_track_combo.currentIndexChanged.connect(self._on_subtitle_track_changed)
        
        # Progress panel (botón de procesamiento)
        self.progress_panel.action_clicked.connect(self._start_remux)
        
        # ViewModel signals
        self.viewmodel.progress_changed.connect(self._on_progress)
        self.viewmodel.status_changed.connect(self._on_status)
        self.viewmodel.log_message.connect(self._on_log)
        self.viewmodel.error_occurred.connect(self._on_error)
        self.viewmodel.completed.connect(self._on_completed)
        
        # MPV signals
        self.mpv_widget.log_signal.connect(self._on_log)
        
        # SyncControls signals
        self.sync_controls.offset_changed.connect(self._on_offsets_changed)
    
    # === HELPERS ===
    
    def _set_folder_mode(self, is_folder: bool):
        """Establece el modo de carpeta"""
        self.is_folder_mode = is_folder
        self._log(f"Modo: {'Carpetas' if is_folder else 'Archivo individual'}", "info")
    
    def _on_video_path_changed(self, path: str):
        """Callback cuando cambia la ruta del video"""
        self.current_video_path = path if path else None
    
    # === PREVIEW ===
    
    def _scan_folders(self):
        """Escanea carpetas y encuentra episodios"""
        self._log("🔍 Escaneando carpetas...", "info")
        
        video_path = self.widgets.video_input.get_path()
        
        if not video_path:
            self._log("⚠️ Selecciona la carpeta de videos", "warning")
            return
        
        # Verificar que sea una carpeta
        if not Path(video_path).is_dir():
            self._log("⚠️ La ruta de video debe ser una carpeta", "warning")
            return
        
        try:
            # Usar EpisodeMatcher para encontrar episodios
            from core.services.episode_matcher import EpisodeMatcher
            
            matcher = EpisodeMatcher()
            
            # Escanear directorio de videos
            episodes_dict = matcher.scan_directory(Path(video_path), recursive=False)
            
            if not episodes_dict:
                self._log("⚠️ No se encontraron episodios", "warning")
                return
            
            # Convertir Episode objects a diccionarios simples
            episodes = {}
            for ep_num, episode in episodes_dict.items():
                episodes[ep_num] = {
                    'video': str(episode.video_file) if episode.video_file else None,
                    'audio': str(episode.audio_files[0]) if episode.audio_files else None,
                    'subtitle': str(episode.subtitle_files[0]) if episode.subtitle_files else None,
                    'forced': str(episode.forced_subtitle_files[0]) if episode.forced_subtitle_files else None
                }
            
            # Limpiar y llenar el combo
            self.widgets.episode_combo.clear()
            for ep_num in sorted(episodes.keys()):
                self.widgets.episode_combo.addItem(f"Episodio {ep_num}", ep_num)
            
            # Guardar episodios
            self.episodes = episodes
            
            self._log(f"✅ {len(episodes)} episodios encontrados", "success")
            
        except Exception as e:
            self._log(f"❌ Error al escanear: {str(e)}", "error")
    
    def _on_episode_changed(self, index):
        """Callback cuando cambia el episodio seleccionado"""
        if index < 0 or not self.episodes:
            return
        
        ep_num = self.widgets.episode_combo.currentData()
        if not ep_num or ep_num not in self.episodes:
            return
        
        ep_data = self.episodes[ep_num]
        self._log(f"📺 Episodio {ep_num:02d} seleccionado", "info")
        
        # Actualizar current_video_path con el video del episodio
        if ep_data.get('video'):
            self.current_video_path = ep_data['video']
            video_name = Path(ep_data['video']).name
            self._log(f"  📹 Video: {video_name}", "info")
        
        # Mostrar info de otros archivos
        if ep_data.get('audio'):
            audio_name = Path(ep_data['audio']).name
            self._log(f"  🎵 Audio: {audio_name}", "info")
        if ep_data.get('subtitle'):
            sub_name = Path(ep_data['subtitle']).name
            self._log(f"  📝 Subtítulos: {sub_name}", "info")
        if ep_data.get('forced'):
            forced_name = Path(ep_data['forced']).name
            self._log(f"  🔤 Letreros: {forced_name}", "info")
    
    # === PREVIEW ===
    
    def _load_preview(self):
        """Carga el video en el preview"""
        # Si hay un video específico seleccionado (episodio), usar ese
        if self.current_video_path:
            video_path = self.current_video_path
        else:
            # Si no, intentar obtener del input
            video_path = self.widgets.video_input.get_path()
            
            # Si es una carpeta, necesita seleccionar episodio
            if video_path and Path(video_path).is_dir():
                self._log("⚠️ Selecciona un episodio del combo primero", "warning")
                return
        
        if not video_path:
            self._log("⚠️ Selecciona un video primero", "warning")
            return
        
        # Cargar video
        self.mpv_widget.load_video(video_path)
        
        # Esperar un momento para que MPV procese el video
        # Luego cargar archivos externos y pistas
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self._load_external_files_and_tracks)
        
        self._log("✅ Preview cargado", "success")
    
    def _load_external_files_and_tracks(self):
        """Carga archivos externos y actualiza la lista de pistas (con delay)"""
        # Cargar archivos externos en MPV si existen
        self._load_external_files()
        
        # Esperar otro momento para que MPV procese los archivos externos
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(300, self._load_available_tracks)
    
    def _load_external_files(self):
        """Carga archivos de audio y subtítulos externos en MPV"""
        self._log("DEBUG: Iniciando carga de archivos externos...", "info")
        
        # Obtener archivos externos según el modo
        audio_external = None
        subtitle_external = None
        forced_external = None
        
        if self.is_folder_mode and self.episodes:
            ep_num = self.widgets.episode_combo.currentData()
            self._log(f"DEBUG: Modo carpetas, episodio {ep_num}", "info")
            if ep_num and ep_num in self.episodes:
                audio_external = self.episodes[ep_num].get('audio')
                subtitle_external = self.episodes[ep_num].get('subtitle')
                forced_external = self.episodes[ep_num].get('forced')
                self._log(f"DEBUG: Audio={audio_external}", "info")
                self._log(f"DEBUG: Sub={subtitle_external}", "info")
                self._log(f"DEBUG: Forced={forced_external}", "info")
        else:
            audio_external = self.widgets.audio_input.get_path()
            subtitle_external = self.widgets.subtitle_input.get_path()
            forced_external = self.widgets.forced_input.get_path()
            self._log(f"DEBUG: Modo individual", "info")
        
        # Cargar audio externo
        if audio_external and Path(audio_external).is_file():
            self._log(f"DEBUG: Cargando audio: {audio_external}", "info")
            self.mpv_widget.load_external_audio(audio_external)
            self._log(f"🎵 Audio externo cargado: {Path(audio_external).name}", "info")
        else:
            self._log(f"DEBUG: No hay audio externo o no existe", "info")
        
        # Cargar subtítulos externos
        if subtitle_external and Path(subtitle_external).is_file():
            self._log(f"DEBUG: Cargando subtítulos: {subtitle_external}", "info")
            self.mpv_widget.load_external_subtitle(subtitle_external)
            self._log(f"📝 Subtítulos externos cargados: {Path(subtitle_external).name}", "info")
        else:
            self._log(f"DEBUG: No hay subtítulos externos o no existen", "info")
        
        # Cargar letreros/forced
        if forced_external and Path(forced_external).is_file():
            self._log(f"DEBUG: Cargando letreros: {forced_external}", "info")
            self.mpv_widget.load_external_subtitle(forced_external)
            self._log(f"🔤 Letreros cargados: {Path(forced_external).name}", "info")
        else:
            self._log(f"DEBUG: No hay letreros o no existen", "info")
        
        self._log("DEBUG: Carga de archivos externos completada", "info")
    
    def _load_available_tracks(self):
        """Carga las pistas disponibles del video en los selectores"""
        # Limpiar selectores
        self.widgets.audio_track_combo.clear()
        self.widgets.subtitle_track_combo.clear()
        
        try:
            # Obtener pistas del video original en MPV
            audio_tracks = self.mpv_widget.get_audio_tracks() or []
            subtitle_tracks = self.mpv_widget.get_subtitle_tracks() or []
            
            # === AUDIO ===
            self.widgets.audio_track_combo.addItem("Sin audio", None)
            
            # Agregar todas las pistas de audio (originales + externas cargadas)
            for track in audio_tracks:
                track_id = track.get('id', 0)
                track_lang = track.get('lang', 'und')
                track_title = track.get('title', '')
                
                # Determinar si es externa por el título o filename
                is_external = track.get('external', False) or 'external' in str(track_title).lower()
                prefix = "🎵 " if is_external else ""
                
                label = f"{prefix}Audio {track_id}: {track_lang}"
                if track_title:
                    label += f" - {track_title}"
                
                self.widgets.audio_track_combo.addItem(label, track_id)
            
            # === SUBTÍTULOS ===
            self.widgets.subtitle_track_combo.addItem("Sin subtítulos", None)
            
            # Agregar todas las pistas de subtítulos (originales + externas cargadas)
            for track in subtitle_tracks:
                track_id = track.get('id', 0)
                track_lang = track.get('lang', 'und')
                track_title = track.get('title', '')
                
                # Determinar si es externa por el título o filename
                is_external = track.get('external', False) or 'external' in str(track_title).lower()
                prefix = "📝 " if is_external else ""
                
                label = f"{prefix}Subtitle {track_id}: {track_lang}"
                if track_title:
                    label += f" - {track_title}"
                
                self.widgets.subtitle_track_combo.addItem(label, track_id)
            
            # Log de resumen
            self._log(f"🎵 {len(audio_tracks)} pistas de audio disponibles", "info")
            self._log(f"📝 {len(subtitle_tracks)} pistas de subtítulos disponibles", "info")
            
        except Exception as e:
            self._log(f"⚠️ Error al cargar pistas: {str(e)}", "warning")
            # Agregar opciones por defecto
            self.widgets.audio_track_combo.addItem("Sin audio", None)
            self.widgets.subtitle_track_combo.addItem("Sin subtítulos", None)
    
    def _toggle_play(self):
        """Toggle play/pause"""
        self.mpv_widget.toggle_play()
        
        # Actualizar botón en el preview panel
        if self.mpv_widget.is_playing:
            self.widgets.preview_panel.set_play_text("⏸")
        else:
            self.widgets.preview_panel.set_play_text("▶")
    
    def _stop_preview(self):
        """Detiene el preview"""
        self.mpv_widget.stop()
        self.widgets.preview_panel.set_play_text("▶")
    
    def _seek(self, seconds: float):
        """Navega en el video"""
        self.mpv_widget.seek(seconds)
    
    # === PISTAS ===
    
    def _on_audio_track_changed(self, index):
        """Callback cuando cambia la pista de audio seleccionada"""
        if index < 0:
            return
        
        track_id = self.widgets.audio_track_combo.currentData()
        
        if track_id is not None:
            self.mpv_widget.set_audio_track(track_id)
            self._log(f"🎵 Pista de audio cambiada: {track_id}", "info")
    
    def _on_subtitle_track_changed(self, index):
        """Callback cuando cambia la pista de subtítulos seleccionada"""
        if index < 0:
            return
        
        track_id = self.widgets.subtitle_track_combo.currentData()
        
        if track_id is not None:
            self.mpv_widget.set_subtitle_track(track_id)
            self._log(f"📝 Pista de subtítulos cambiada: {track_id}", "info")
        else:
            # Desactivar subtítulos
            self.mpv_widget.set_subtitle_track(0)
            self._log("📝 Subtítulos desactivados", "info")
    
    # === OFFSETS ===
    
    def _on_offsets_changed(self, audio_ms: int, subtitle_ms: int):
        """
        Callback cuando cambian los offsets desde SyncControls.
        
        Args:
            audio_ms: Offset de audio en milisegundos
            subtitle_ms: Offset de subtítulos en milisegundos
        """
        self._log(f"🎵 Audio offset: {audio_ms}ms", "info")
        self._log(f"📝 Subtitle offset: {subtitle_ms}ms", "info")
        
        # Aplicar offsets al MPV para preview en tiempo real
        self.mpv_widget.set_audio_delay(audio_ms)
        self.mpv_widget.set_subtitle_delay(subtitle_ms)
    
    # === REMUXEO ===
    
    def _start_remux(self):
        """Inicia el remuxeo usando ViewModel"""
        # Validar
        video_path = self.widgets.video_input.get_path()
        output_path = self.widgets.output_input.get_path()
        
        if not video_path or not output_path:
            self._log("⚠️ Faltan archivos requeridos (Video y Salida)", "warning")
            return
        
        # Modo por lotes (carpetas)
        if self.is_folder_mode:
            self._start_batch_remux()
            return
        
        # Obtener archivos externos (opcionales)
        audio_path = self.widgets.audio_input.get_path() or ""
        subtitle_path = self.widgets.subtitle_input.get_path() or ""
        forced_path = self.widgets.forced_input.get_path() or ""
        
        # Log de inicio
        self._log("🎬 Iniciando remuxeo (Assembler)...", "info")
        self._log(f"📹 Video: {Path(video_path).name}", "info")
        if audio_path:
            self._log(f"🎵 Audio externo: {Path(audio_path).name}", "info")
        if subtitle_path:
            self._log(f"📝 Subtítulos externos: {Path(subtitle_path).name}", "info")
        if forced_path:
            self._log(f"🔤 Letreros: {Path(forced_path).name}", "info")
        self._log(f"💾 Salida: {Path(output_path).name}", "info")
        
        # Obtener offsets del widget SyncControls
        audio_offset_ms = self.sync_controls.get_audio_offset_ms()
        subtitle_offset_ms = self.sync_controls.get_subtitle_offset_ms()
        
        if audio_offset_ms != 0:
            self._log(f"⏱️ Offset audio: {audio_offset_ms}ms", "info")
        if subtitle_offset_ms != 0:
            self._log(f"⏱️ Offset subtítulos: {subtitle_offset_ms}ms", "info")
        
        # Ejecutar remuxeo usando ViewModel
        self.viewmodel.start_remux(
            video_path=video_path,
            audio_path=audio_path,
            subtitle_path=subtitle_path,
            forced_path=forced_path,
            output_path=output_path,
            audio_offset_ms=audio_offset_ms,
            subtitle_offset_ms=subtitle_offset_ms
        )
        
        self.progress_panel.set_button_enabled(False)
    
    def _start_batch_remux(self):
        """Inicia el remuxeo por lotes usando los episodios escaneados"""
        if not self.episodes:
            self._log("⚠️ No hay episodios para procesar. Escanea primero.", "warning")
            return
        
        output_path = self.widgets.output_input.get_path()
        if not output_path:
            self._log("⚠️ Selecciona una carpeta de salida", "warning")
            return
        
        # Obtener offsets
        audio_offset_ms = self.sync_controls.get_audio_offset_ms()
        subtitle_offset_ms = self.sync_controls.get_subtitle_offset_ms()
        
        # Log de inicio
        self._log("🎬 Iniciando remuxeo por lotes (Assembler)...", "info")
        self._log(f"📦 {len(self.episodes)} episodios a procesar", "info")
        self._log(f"💾 Carpeta de salida: {output_path}", "info")
        
        if audio_offset_ms != 0:
            self._log(f"⏱️ Offset audio: {audio_offset_ms}ms", "info")
        if subtitle_offset_ms != 0:
            self._log(f"⏱️ Offset subtítulos: {subtitle_offset_ms}ms", "info")
        
        # Iniciar procesamiento por lotes usando ViewModel
        self.viewmodel.start_batch_remux(
            episodes=self.episodes,
            output_directory=Path(output_path),
            audio_offset_ms=audio_offset_ms,
            subtitle_offset_ms=subtitle_offset_ms
        )
        
        self.progress_panel.set_button_enabled(False)
    
    # === CALLBACKS ===
    
    def _on_progress(self, progress: int, message: str):
        """Callback de progreso"""
        self.progress_panel.set_progress(progress, message)
    
    def _on_status(self, status: str):
        """Callback de status"""
        self._log(status, "info")
    
    def _on_log(self, message: str, level: str):
        """Callback de log"""
        self._log(message, level)
    
    def _on_error(self, error: str):
        """Callback de error"""
        self._log(f"❌ {error}", "error")
        QMessageBox.critical(self, "Error", error)
        self.progress_panel.set_button_enabled(True)
    
    def _on_completed(self, success: bool):
        """Callback de completado"""
        self.progress_panel.set_button_enabled(True)
        
        if success:
            self._log("✅ Remuxeo completado exitosamente", "success")
            QMessageBox.information(self, "Éxito", "Remuxeo completado exitosamente")
        else:
            self._log("❌ Remuxeo falló", "error")
    
    def _log(self, message: str, level: str = "info"):
        """
        Agrega un mensaje al log usando ConsoleLog widget.
        
        Args:
            message: Mensaje a mostrar
            level: Nivel (info, warning, error, success)
        """
        self.console.log(message, level)
    
    def cleanup(self):
        """Limpia recursos"""
        if hasattr(self, 'mpv_widget'):
            self.mpv_widget.cleanup()
