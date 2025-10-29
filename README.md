# 🎬 Remuxeador FFmpeg v0.1 (Beta)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Herramienta para remuxear y combinar archivos de video con múltiples pistas de audio y subtítulos.**

Diseñada específicamente para combinar episodios de anime con audio japonés y latino, pero flexible para cualquier flujo de trabajo de remuxeo de video.

---

## ✨ Características Principales

### 🎯 Modo Ensamblador (Assembler)
- **Remuxeo individual de archivos de video**
- Combina múltiples pistas de audio y subtítulos en un solo archivo MKV
- Previsualización integrada con MPV para verificar pistas antes de procesar
- Configuración detallada de metadatos (idioma, título, flags de pista)
- Soporte para múltiples codecs de video, audio y subtítulos
- Procesamiento sin recodificación (copy mode) para máxima velocidad

### 🔄 Modo Sincronización Dual (Dual Sync)
- **Procesamiento por lotes de múltiples episodios**
- Emparejamiento automático de episodios JP/LAT por número
- Combina automáticamente audio japonés + audio/subtítulos latinos
- Configuración de metadatos predeterminados personalizables
- Vista previa lado a lado de ambos archivos antes de procesar
- Procesamiento paralelo con barra de progreso en tiempo real

### 🎨 Interfaz Gráfica (PyQt6
- Diseño con PyQt6 y tema oscuro/claro
- Sistema de pestañas
- Previsualización de video integrada con controles MPV
- Logs en tiempo real del proceso de remuxeo
- Gestión de errores con mensajes descriptivos
- La interfaz es muy basica y no busca ser bonita, la finalidad es mejorarla a futuro

---

## 🏗️ Arquitectura del Proyecto

El proyecto sigue una **arquitectura limpia en capas** para máxima mantenibilidad y escalabilidad:

```
remuxeador-ffmpeg/
│
├── core/                          # 🧠 Lógica de Negocio (Domain Layer)
│   ├── domain/                    # Modelos y enums del dominio
│   │   ├── models.py              # RemuxJob, Track, Episode, etc.
│   │   └── enums.py               # JobStatus, TrackType, LanguageCode
│   │
│   ├── engines/                   # Motores de procesamiento
│   │   ├── base_engine.py         # Interfaz base para engines
│   │   ├── mkvmerge_engine.py     # Motor MKVMerge (principal)
│   │   └── ffprobe_engine.py      # Motor FFprobe (análisis de archivos)
│   │
│   ├── services/                  # Servicios de aplicación
│   │   ├── remux_service.py       # Orquestador de remuxeo
│   │   ├── batch_service.py       # Procesamiento por lotes
│   │   ├── episode_matcher.py     # Emparejamiento de episodios
│   │   ├── dual_video_service.py  # Servicio de sincronización dual
│   │   └── subtitle_service.py    # Gestión de subtítulos
│   │
│   └── utils/                     # Utilidades del dominio
│       ├── file_utils.py          # Operaciones con archivos
│       ├── time_utils.py          # Utilidades de tiempo
│       └── validators.py          # Validadores de datos
│
├── infrastructure/                # ⚙️ Infraestructura (Infrastructure Layer)
│   ├── config/                    # Configuración de la aplicación
│   │   └── settings.py            # Settings centralizados
│   │
│   ├── external/                  # Gestión de herramientas externas
│   │   ├── mpv_manager.py         # Manager de MPV
│   │   └── tool_detector.py       # Detección de herramientas
│   │
│   └── logging/                   # Sistema de logging
│       └── logger.py              # Configuración de logs
│
├── presentation/                  # 🎨 Capa de Presentación (UI Layer)
│   └── qt/                        # Interfaz PyQt6
│       ├── main_window.py         # Ventana principal
│       │
│       ├── tabs/                  # Pestañas principales
│       │   ├── assembler_tab.py   # Tab de ensamblador
│       │   └── dual_sync_tab.py   # Tab de sincronización dual
│       │
│       ├── widgets/               # Widgets reutilizables (13 archivos)
│       │   ├── mpv_preview.py     # Widget de previsualización MPV
│       │   ├── mpv_dual_preview.py # Preview dual con MPV
│       │   ├── preview_panel.py   # Panel de preview
│       │   ├── dual_preview.py    # Preview dual sincronizado
│       │   ├── track_list.py      # Lista de pistas
│       │   ├── file_selector.py   # Selector de archivos
│       │   ├── console_log.py     # Consola de logs
│       │   └── ...                # Y más widgets
│       │
│       ├── ui_builders/           # Constructores de UI
│       │   ├── assembler_ui_builder.py      # Builder del tab assembler
│       │   ├── assembler_layout_builder.py  # Layout del assembler
│       │   ├── dualsync_ui_builder.py       # Builder del tab dual sync
│       │   └── dualsync_layout_builder.py   # Layout del dual sync
│       │
│       ├── viewmodels/            # ViewModels (patrón MVVM)
│       │   ├── base_viewmodel.py       # ViewModel base
│       │   ├── assembler_viewmodel.py  # ViewModel del assembler
│       │   └── dualsync_viewmodel.py   # ViewModel del dual sync
│       │
│       ├── workers/               # Workers para procesamiento async
│       │   ├── remux_worker.py         # Worker de remuxeo
│       │   ├── batch_worker.py         # Worker de procesamiento por lotes
│       │   ├── dualsync_worker.py      # Worker de sincronización dual
│       │   └── advanced_worker.py      # Worker avanzado
│       │
│       ├── layouts/               # Gestión de layouts y temas
│       │   ├── theme_manager.py        # Gestor de temas
│       │   ├── layout_factory.py       # Factory de layouts
│       │   └── base_layout_builder.py  # Builder base de layouts
│       │
│       ├── dialogs/               # Diálogos modales
│       │
│       ├── styles/                # Estilos CSS/QSS
│       │   └── dark_theme.qss          # Tema oscuro y default de la app
│
├── external/                      # 📦 Herramientas externas (Windows)
│   └── mpv/                       # MPV portable (incluido)
│
├── logs/                          # 📝 Archivos de log
│
├── main.py                        # 🚀 Punto de entrada
├── config.py                      # Configuración legacy (deprecado)
├── requirements.txt               # Dependencias Python
└── README.md                      # Este archivo
```

### 📐 Principios de Diseño

1. **Separación de Responsabilidades**: Cada capa tiene un propósito claro
   - `core/`: Lógica de negocio pura, sin dependencias de UI o infraestructura
   - `infrastructure/`: Configuración, logging, herramientas externas
   - `presentation/`: Solo UI, delega toda la lógica a `core/`

2. **Patrón MVVM (Model-View-ViewModel)**: Arquitectura moderna de UI
   - `ViewModels`: Intermediarios entre UI y servicios, manejan estado de UI
   - `Views` (tabs/widgets): Solo renderizado, sin lógica de negocio
   - `Models`: Entidades del dominio en `core/domain/`
   - Comunicación mediante señales de PyQt6

3. **Builder Pattern**: Construcción modular de interfaces complejas
   - `UIBuilder`: Construye la estructura de cada tab
   - `LayoutBuilder`: Organiza los layouts de forma declarativa
   - `LayoutFactory`: Factory para crear layouts consistentes
   - Facilita mantenimiento y reutilización de componentes

4. **Worker Pattern**: Procesamiento asíncrono sin bloquear UI
   - `QThread` workers para operaciones largas (remuxeo, análisis)
   - Comunicación mediante señales para actualizar progreso
   - Evita congelamiento de la interfaz

5. **Dependency Injection**: Los servicios reciben sus dependencias por constructor
   - Facilita testing y mantenimiento
   - Reduce acoplamiento entre componentes

6. **Domain-Driven Design**: Modelos ricos que encapsulan lógica de negocio
   - `RemuxJob`, `Track`, `Episode` son entidades del dominio
   - Enums tipados para estados y tipos (`JobStatus`, `TrackType`)
   - Validadores separados en `core/utils/validators.py`

7. **Engine Pattern**: Abstracción de herramientas de remuxeo
   - `BaseEngine`: Interfaz común para todos los engines
   - `MKVMergeEngine`: Implementación principal para remuxeo
   - `FFprobeEngine`: Análisis de archivos multimedia
   - Fácil agregar nuevos engines (HandBrake, etc.)

---

## 📋 Requisitos del Sistema

### Obligatorios
- **Python 3.10+**
- **MKVToolNix (mkvmerge)** - [Descargar aquí](https://mkvtoolnix.download/downloads.html)
  - Windows: Instalar desde el sitio oficial
  - Linux: `sudo apt install mkvtoolnix`
  - macOS: `brew install mkvtoolnix`

### Opcionales (pero recomendados)
- **MPV Player** - Para previsualización de video
  - Windows: [Descargar MPV](https://mpv.io/installation/) o usar [Shinchiro builds](https://sourceforge.net/projects/mpv-player-windows/files/)
  - Linux: `sudo apt install mpv libmpv-dev`
  - macOS: `brew install mpv`

---

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/Mabci/remuxeador.git
cd remuxeador
```

### 2. Crear entorno virtual (recomendado)
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 3. Instalar dependencias de Python
```bash
pip install -r requirements.txt
```

### 4. Instalar MKVToolNix
**Windows:**
- Descargar desde https://mkvtoolnix.download/downloads.html
- Instalar y asegurarse de que `mkvmerge.exe` esté en el PATH

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mkvtoolnix
```

**macOS:**
```bash
brew install mkvtoolnix
```

### 5. (Opcional) Instalar MPV
**Windows:** Ya incluido en `external/mpv/`

**Linux:**
```bash
sudo apt install mpv libmpv-dev
```

**macOS:**
```bash
brew install mpv
```

---

## 🎮 Uso

### Iniciar la aplicación
```bash
python main.py
```

### Modo Ensamblador (Assembler Tab)

1. **Seleccionar archivo de video base**
   - Click en "Seleccionar Video Base"
   - Elige el archivo MKV principal

2. **Agregar pistas adicionales**
   - Click en "Agregar Audio" o "Agregar Subtítulos"
   - Selecciona archivos de audio/subtítulos externos
   - O extrae pistas de otros archivos MKV

3. **Configurar metadatos**
   - Edita idioma, título y flags de cada pista
   - Marca pistas como predeterminadas o forzadas

4. **Previsualizar (opcional)**
   - Click en "Preview" para verificar el video
   - Usa los controles de MPV para navegar

5. **Procesar**
   - Click en "Remuxear"
   - Elige ubicación de salida
   - Espera a que termine el proceso

### Modo Sincronización Dual (Dual Sync Tab)

1. **Seleccionar carpetas**
   - Carpeta JP: Episodios con audio japonés
   - Carpeta LAT: Episodios con audio/subtítulos latinos

2. **Configurar metadatos predeterminados**
   - Títulos de audio JP y LAT
   - Título de subtítulos LAT
   - Idiomas de cada pista

3. **Emparejar episodios**
   - Click en "Emparejar Episodios"
   - Verifica los emparejamientos en la tabla

4. **Previsualizar (opcional)**
   - Selecciona un par de episodios
   - Click en "Preview" para ver ambos archivos

5. **Procesar lote**
   - Click en "Procesar Lote"
   - Elige carpeta de salida
   - Monitorea el progreso en tiempo real

---

## 🛠️ Configuración Avanzada

### Archivo de configuración: `infrastructure/config/settings.py`

```python
# Rutas de herramientas
MKVMERGE_PATH = "mkvmerge"  # Cambiar si no está en PATH
MPV_PATH = "mpv"            # Cambiar si no está en PATH

# Configuración de logging
LOG_LEVEL = "INFO"          # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True          # Guardar logs en archivos
LOG_TO_CONSOLE = True       # Mostrar logs en consola

# Configuración de UI
THEME = "dark"              # dark, light
```

---

## 🐛 Solución de Problemas

### Error: "MKVMerge no encontrado"
- **Solución**: Instala MKVToolNix y asegúrate de que `mkvmerge` esté en el PATH del sistema
- Verifica con: `mkvmerge --version`

### Error: "No se puede cargar libmpv"
- **Windows**: Asegúrate de que `external/mpv/libmpv-2.dll` exista
- **Linux**: Instala `libmpv-dev`: `sudo apt install libmpv-dev`

### La previsualización no funciona
- Verifica que MPV esté instalado correctamente
- La previsualización es opcional, el remuxeo funcionará sin ella

### Archivos no se emparejan en Dual Sync
- Asegúrate de que los archivos tengan números de episodio en el nombre
- Formato esperado: `Nombre_EP01.mkv`, `Serie - 01.mkv`, etc.
- Los números deben coincidir entre archivos JP y LAT

---

## 📊 Roadmap v0.2+

- [ ] Rediseño de UI y UX
- [ ] Modo CLI para automatización
- [ ] Mejoras de QoL
