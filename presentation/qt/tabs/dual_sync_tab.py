"""
DualSync Tab - Refactorizado con MVVM

UI separada de lógica usando ViewModel y Workers.
"""
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QFrame, 
                              QTextEdit, QProgressBar, QFileDialog, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import platform
from datetime import datetime
from pathlib import Path

# Imports de la arquitectura MVVM
from presentation.qt.viewmodels import DualSyncViewModel
from presentation.qt.workers import DualSyncSingleWorker, DualSyncBatchWorker
from presentation.qt.widgets import MPVDualPreviewWidget
from presentation.qt.ui_builders import DualSyncLayoutBuilder


class DualSyncTab(QWidget):
    """
    Tab DualSync - Refactorizado con MVVM.
    
    Solo maneja UI. Toda la lógica está en DualSyncViewModel.
    """
    
    def __init__(self, viewmodel: DualSyncViewModel, parent=None):
        super().__init__(parent)
        
        # ViewModel (lógica de presentación)
        self.viewmodel = viewmodel
        
        # Workers
        self.single_worker = None
        self.batch_worker = None
        self.processing = False
        
        # MPV Widget (se creará después de build_ui)
        self.mpv_widget = None
        
        # Construir UI
        self._build_ui()
        self._connect_signals()
        self._connect_viewmodel_signals()
        
        # Crear MPV widget DESPUÉS de que los frames existan
        self._init_mpv_widget()
    
    def _build_ui(self):
        """Construye la UI usando DualSyncLayoutBuilder"""
        # Usar el nuevo layout builder
        layout_builder = DualSyncLayoutBuilder(self)
        self.widgets = layout_builder.build_widgets()
        
        # Referencias directas a widgets comunes
        self.sync_controls = self.widgets.sync_controls
        self.console = self.widgets.console
        self.progress_panel = self.widgets.progress_panel
    
    def _connect_signals(self):
        """Conecta señales"""
        # Escanear (solo en modo batch)
        self.widgets.scan_btn.clicked.connect(self.scan_folders)
        
        # Botón de cargar preview
        self.widgets.load_preview_btn.clicked.connect(self.load_previews)
        
        # Controles centralizados (controlan ambos videos)
        self.widgets.dual_controls.play_clicked.connect(self.toggle_play)
        self.widgets.dual_controls.stop_clicked.connect(self.stop)
        self.widgets.dual_controls.seek_requested.connect(self.seek)
        
        # Botones de mute individuales
        self.widgets.preview_jp.mute_clicked.connect(self.toggle_mute_jp)
        self.widgets.preview_lat.mute_clicked.connect(self.toggle_mute_lat)
        
        # Progress panel (botón de procesamiento)
        self.progress_panel.action_clicked.connect(self.start_processing)
        
        # SyncControls signals
        self.sync_controls.offset_changed.connect(self._on_offsets_changed)
    
    def _connect_viewmodel_signals(self):
        """Conecta signals del ViewModel"""
        # Cuando se encuentran episodios
        self.viewmodel.episodes_found.connect(self._on_episodes_found)
        
        # Cuando cambia el modo
        self.viewmodel.mode_changed.connect(self._on_mode_changed)
        
        # Logs del ViewModel
        self.viewmodel.log_message.connect(self._log)
    
    def _on_episodes_found(self, episodes):
        """Callback cuando el ViewModel encuentra episodios"""
        # Actualizar combo con episodios
        self.widgets.episode_combo.clear()
        for ep_num in sorted(episodes.keys()):
            self.widgets.episode_combo.addItem(f"Episodio {ep_num:02d}", ep_num)
    
    def _on_mode_changed(self, mode):
        """Callback cuando cambia el modo"""
        if mode == 'single':
            self.widgets.scan_btn.hide()
            self.widgets.episode_combo.hide()
            self.progress_panel.set_button_text("Remuxear")
        else:  # batch
            self.widgets.scan_btn.show()
            self.widgets.episode_combo.show()
            self.progress_panel.set_button_text("Procesar Lotes")
    
    def _init_mpv_widget(self):
        """Inicializa el widget MPV DESPUÉS de que los frames existan"""
        # Obtener frames de los preview panels
        jp_frame = self.widgets.preview_jp.get_preview_frame()
        lat_frame = self.widgets.preview_lat.get_preview_frame()
        
        self.mpv_widget = MPVDualPreviewWidget(
            jp_frame,
            lat_frame,
            self
        )
        
        # Conectar signals del MPV widget
        self.mpv_widget.log_signal.connect(self._log)
        self.mpv_widget.timestamps_updated.connect(self._on_timestamps_updated)
    
    def _on_timestamps_updated(self, time_jp: str, time_lat: str):
        """Callback cuando se actualizan los timestamps"""
        # Actualizar labels de tiempo en los controles centralizados
        current_jp, total_jp = time_jp.split(' / ') if ' / ' in time_jp else (time_jp, "00:00:00")
        current_lat, total_lat = time_lat.split(' / ') if ' / ' in time_lat else (time_lat, "00:00:00")
        self.widgets.dual_controls.set_time_jp(current_jp, total_jp)
        self.widgets.dual_controls.set_time_lat(current_lat, total_lat)
    
    
    def _switch_to_single_mode(self):
        """Cambia a modo individual - Delega al ViewModel"""
        self.viewmodel.switch_to_single_mode()
    
    def _switch_to_batch_mode(self):
        """Cambia a modo por lotes - Delega al ViewModel"""
        self.viewmodel.switch_to_batch_mode()
    
    def scan_folders(self):
        """Escanea carpetas - Delega al ViewModel"""
        jp_folder = self.widgets.jp_input.get_path()
        lat_folder = self.widgets.lat_input.get_path()
        
        if not jp_folder or not lat_folder:
            QMessageBox.warning(self, "Faltan carpetas", "Selecciona ambas carpetas")
            return
        
        # Delegar al ViewModel (la lógica está allí)
        self.viewmodel.scan_folders(jp_folder, lat_folder)
    
    def load_previews(self):
        """Carga preview del episodio seleccionado - Usa MPV Widget"""
        if self.viewmodel.get_episode_count() == 0:
            QMessageBox.warning(self, "Sin episodios", "Primero escanea las carpetas")
            return
        
        ep_num = self.widgets.episode_combo.currentData()
        if not ep_num:
            return
        
        # Obtener datos del episodio desde el ViewModel
        ep_data = self.viewmodel.get_episode_data(ep_num)
        if not ep_data:
            return
        
        video_jp = ep_data.get('jp')
        video_lat = ep_data.get('lat')
        
        if not video_jp or not video_lat:
            QMessageBox.warning(self, "Error", "Episodio incompleto")
            return
        
        try:
            # Delegar al widget MPV
            self.mpv_widget.load_videos(video_jp, video_lat)
            
            # Actualizar botones de mute en los preview panels
            self.widgets.preview_jp.set_mute_text("🔇 Unmute")
            self.widgets.preview_lat.set_mute_text("🔊 Mute")
            
        except Exception as e:
            self._log(f"Error: {str(e)}", "error")
    
    # === OFFSETS ===
    
    def _on_offsets_changed(self, audio_ms: int, subtitle_ms: int):
        """
        Callback cuando cambian los offsets desde SyncControls.
        
        Args:
            audio_ms: Offset de audio en milisegundos
            subtitle_ms: Offset de subtítulos en milisegundos
        """
        self._log(f"Audio offset: {audio_ms}ms", "info")
        self._log(f"Subtitle offset: {subtitle_ms}ms", "info")
        
        # Aplicar sincronización al widget MPV
        if self.mpv_widget:
            self.mpv_widget.apply_sync(audio_ms, subtitle_ms)
    
    def toggle_play(self):
        """Toggle play/pause - Delega al widget MPV"""
        self.mpv_widget.toggle_play()
        # Actualizar botón en los controles centralizados
        is_playing = self.mpv_widget.is_playing
        play_text = "⏸" if is_playing else "▶"
        self.widgets.dual_controls.set_play_text(play_text)
    
    def stop(self):
        """Detiene y reinicia - Delega al widget MPV"""
        self.mpv_widget.stop()
        self.widgets.dual_controls.set_play_text("▶")
    
    def seek(self, seconds):
        """Navega en ambos videos - Delega al widget MPV"""
        self.mpv_widget.seek(seconds)
    
    def toggle_mute_jp(self):
        """Toggle mute JP - Delega al widget MPV"""
        is_muted = self.mpv_widget.toggle_mute_jp()
        self.widgets.preview_jp.set_mute_text("🔇 Unmute" if is_muted else "🔊 Mute")
    
    def toggle_mute_lat(self):
        """Toggle mute LAT - Delega al widget MPV"""
        is_muted = self.mpv_widget.toggle_mute_lat()
        self.widgets.preview_lat.set_mute_text("🔇 Unmute" if is_muted else "🔊 Mute")
    
    def start_processing(self):
        """Detecta el modo y procesa (single o batch)"""
        if self.processing:
            return
        
        jp_path = self.widgets.jp_input.get_path()
        es_path = self.widgets.lat_input.get_path()
        output_path = self.widgets.output_input.get_path()
        
        if not jp_path or not es_path or not output_path:
            QMessageBox.warning(self, "Faltan datos", "Selecciona todos los archivos/carpetas")
            return
        
        # Detectar modo basado en si son archivos o carpetas
        from pathlib import Path
        jp_is_file = Path(jp_path).is_file()
        es_is_file = Path(es_path).is_file()
        
        if jp_is_file and es_is_file:
            # Modo individual
            self._start_single_remux()
        else:
            # Modo por lotes
            self._start_batch_remux()
    
    def _start_single_remux(self):
        """Inicia remuxeo de un solo video - Usa DualSyncSingleWorker"""
        video_jp = self.widgets.jp_input.get_path()
        video_lat = self.widgets.lat_input.get_path()
        output = self.widgets.output_input.get_path()
        
        # Validar con ViewModel
        is_valid, error_msg = self.viewmodel.validate_single_inputs(video_jp, video_lat, output)
        if not is_valid:
            QMessageBox.warning(self, "Error", error_msg)
            return
        
        self.processing = True
        self.progress_panel.reset()
        
        # Obtener offsets del widget SyncControls
        audio_offset_ms = self.sync_controls.get_audio_offset_ms()
        subtitle_offset_ms = self.sync_controls.get_subtitle_offset_ms()
        
        # Usar Worker con DualVideoService (arquitectura SOLID)
        self.single_worker = DualSyncSingleWorker(
            self.viewmodel.dual_video_service,
            video_jp, video_lat, output,
            audio_offset_ms, subtitle_offset_ms
        )
        
        # Conectar signals
        self.single_worker.progress.connect(self._on_progress)
        self.single_worker.log.connect(self._log)
        self.single_worker.finished.connect(self._on_single_complete)
        
        # Iniciar
        self.single_worker.start()
    
    def _start_batch_remux(self):
        """Inicia procesamiento por lotes - Usa DualSyncBatchWorker"""
        output_folder = self.widgets.output_input.get_path()
        
        # Validar con ViewModel
        is_valid, error_msg = self.viewmodel.validate_batch_inputs(output_folder)
        if not is_valid:
            QMessageBox.warning(self, "Error", error_msg)
            return
        
        # Obtener offsets del widget SyncControls
        audio_offset_ms = self.sync_controls.get_audio_offset_ms()
        subtitle_offset_ms = self.sync_controls.get_subtitle_offset_ms()
        
        self._log("Iniciando procesamiento por lotes...", "info")
        self._log(f"Total de episodios: {self.viewmodel.get_episode_count()}", "info")
        self._log(f"Audio offset: {audio_offset_ms}ms", "info")
        self._log(f"Subtitle offset: {subtitle_offset_ms}ms", "info")
        
        self.processing = True
        self.progress_panel.reset()
        
        # Obtener episodios del ViewModel
        episodes = {ep_num: self.viewmodel.get_episode_data(ep_num) 
                   for ep_num in self.viewmodel.get_sorted_episode_numbers()}
        
        # Usar Worker con DualVideoService (arquitectura SOLID)
        self.batch_worker = DualSyncBatchWorker(
            self.viewmodel.dual_video_service,
            episodes, output_folder,
            audio_offset_ms, subtitle_offset_ms
        )
        
        # Conectar signals
        self.batch_worker.progress.connect(self._on_progress)
        self.batch_worker.log.connect(self._log)
        self.batch_worker.finished.connect(self._on_batch_complete)
        
        # Iniciar
        self.batch_worker.start()
    
    def _on_progress(self, value, text):
        """Callback de progreso"""
        self.progress_panel.set_progress(value, text if text else "")
    
    def _on_single_complete(self, success):
        """Callback al completar single"""
        self.processing = False
        
        if success:
            self._log(f"✅ Remuxeo completado exitosamente", "success")
            QMessageBox.information(self, "Éxito", "Remuxeo completado exitosamente")
        else:
            self._log(f"❌ Remuxeo falló", "error")
            QMessageBox.critical(self, "Error", "El remuxeo falló. Revisa la consola para más detalles.")
    
    def _on_batch_complete(self, results):
        """Callback al completar lotes"""
        self.processing = False
        
        success_count = sum(1 for r in results if r.get('success'))
        total_count = len(results)
        
        self._log(f"✅ Procesamiento completado: {success_count}/{total_count} exitosos", "success")
        
        QMessageBox.information(
            self, 
            "Completado", 
            f"Procesamiento completado:\n{success_count}/{total_count} episodios exitosos"
        )
    
    def _log(self, message: str, level: str = "info"):
        """
        Agrega mensaje a la consola usando ConsoleLog widget.
        
        Args:
            message: Mensaje a mostrar
            level: Nivel (info, success, error, warning)
        """
        self.console.log(message, level)
    
    def cleanup(self):
        """Limpia recursos - Delega al widget MPV"""
        if self.mpv_widget:
            self.mpv_widget.cleanup()
