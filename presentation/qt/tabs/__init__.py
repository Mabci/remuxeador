"""
Tabs - Pestañas principales de la aplicación
"""

from .assembler_tab import AssemblerTab
from .dual_sync_tab import DualSyncTab

__all__ = [
    'AssemblerTab',  # 🔧 Assembler - Ensamblar video con pistas externas
    'DualSyncTab',   # 🔀 DualSync - Combinar videos JP + LAT
]
