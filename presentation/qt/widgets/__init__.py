"""
Widgets - Componentes reutilizables de UI
"""

from .file_selector import FileSelector
from .progress_bar import ProgressBar
from .sync_controls import SyncControls
from .dual_preview import DualPreview
from .console_log import ConsoleLog
from .mpv_dual_preview import MPVDualPreviewWidget
from .mpv_preview import MPVPreviewWidget
from .track_list import TrackListWidget
from .file_input_group import FileInputGroup
from .preview_panel import PreviewPanel
from .progress_panel import ProgressPanel
from .dual_preview_controls import DualPreviewControls
from .simple_preview_panel import SimplePreviewPanel

__all__ = [
    'FileSelector',
    'ProgressBar',
    'SyncControls',
    'DualPreview',
    'ConsoleLog',
    'MPVDualPreviewWidget',
    'MPVPreviewWidget',
    'TrackListWidget',
    'FileInputGroup',
    'PreviewPanel',
    'ProgressPanel',
    'DualPreviewControls',
    'SimplePreviewPanel',
]
