# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [0.1.0] - 2024-10-28 (Beta)

### 🎉 Lanzamiento Inicial

Primera versión beta pública del Remuxeador FFmpeg. Incluye todas las funcionalidades básicas para remuxear archivos de video con múltiples pistas de audio y subtítulos.

### ✨ Agregado

#### Funcionalidades Principales
- **Modo Ensamblador (Assembler Tab)**
  - Remuxeo individual de archivos de video
  - Soporte para agregar múltiples pistas de audio y subtítulos
  - Configuración detallada de metadatos por pista (idioma, título, flags)
  - Previsualización integrada con MPV
  - Procesamiento sin recodificación (copy mode)

- **Modo Sincronización Dual (Dual Sync Tab)**
  - Procesamiento por lotes de múltiples episodios
  - Emparejamiento automático de episodios JP/LAT por número
  - Configuración de metadatos predeterminados
  - Vista previa lado a lado de archivos emparejados
  - Barra de progreso en tiempo real

#### Arquitectura
- Implementación de arquitectura limpia en 3 capas:
  - `core/`: Lógica de negocio (domain, engines, services, utils)
  - `infrastructure/`: Configuración, logging, herramientas externas
  - `presentation/`: Interfaz PyQt6 con patrón MVVM

- **Engines de Procesamiento**
  - `MKVMergeEngine`: Motor principal usando MKVToolNix
  - `FFprobeEngine`: Análisis de archivos multimedia
  - `BaseEngine`: Interfaz abstracta para futuros engines

- **Servicios de Aplicación**
  - `RemuxService`: Orquestador principal de remuxeo
  - `BatchService`: Procesamiento por lotes
  - `EpisodeMatcher`: Emparejamiento inteligente de episodios
  - `DualVideoService`: Servicio de sincronización dual
  - `SubtitleService`: Gestión de subtítulos

- **Utilidades del Core**
  - `FileUtils`: Operaciones con archivos
  - `TimeUtils`: Utilidades de tiempo y duración
  - `Validators`: Validadores de datos

#### Interfaz de Usuario
- Sistema de pestañas con PyQt6
- Tema oscuro y claro mediante `ThemeManager`
- **Arquitectura MVVM**:
  - `ViewModels`: Gestión de estado y lógica de presentación
  - `UIBuilders`: Construcción modular de interfaces
  - `LayoutBuilders`: Organización declarativa de layouts
  - `Workers`: Procesamiento asíncrono con QThread
- **Widgets reutilizables** (13 componentes):
  - `MPVPreview`: Widget de previsualización de video
  - `MPVDualPreview`: Preview dual sincronizado
  - `PreviewPanel`: Panel de preview con controles
  - `DualPreview`: Vista dual de archivos
  - `TrackList`: Lista de pistas
  - `FileSelector`: Selector de archivos
  - `ConsoleLog`: Consola de logs en tiempo real
  - Y más componentes especializados
- Diálogos modales para edición de pistas
- Sistema de logs en tiempo real con colores

#### Infraestructura
- Sistema de logging configurable (archivo + consola)
- Gestión de configuración centralizada
- Detección automática de herramientas externas
- MPV portable incluido para Windows

### 🔧 Técnico

- Python 3.10+ como requisito mínimo
- PyQt6 para interfaz gráfica
- python-mpv para previsualización de video
- MKVToolNix (mkvmerge) como motor principal de remuxeo
- Dependency Injection para servicios
- Domain-Driven Design para modelos de negocio
- Enums tipados para estados y tipos

### 📝 Documentación

- README completo con:
  - Descripción de características
  - Arquitectura detallada del proyecto
  - Guía de instalación paso a paso
  - Guía de uso para ambos modos
  - Solución de problemas comunes
  - Roadmap de futuras versiones

- Licencia MIT
- .gitignore configurado para Python y archivos multimedia
- CHANGELOG para seguimiento de versiones

### ⚠️ Limitaciones Conocidas

- Solo soporta archivos MKV como entrada/salida
- No hay procesamiento paralelo de múltiples archivos
- La detección de idiomas de pistas es manual
- No hay presets de configuración guardables
- Falta modo CLI para automatización
- Sin tests unitarios (pendiente para v0.2)

### 🐛 Bugs Conocidos

- Algunos archivos MKV con estructuras complejas pueden fallar
- La previsualización puede no funcionar en algunos sistemas Linux sin libmpv-dev
- El emparejamiento de episodios puede fallar si los nombres no siguen convenciones estándar
- Logs pueden crecer indefinidamente (falta rotación automática)

---

## [Unreleased]

### Planeado para v0.2
- Procesamiento paralelo de múltiples archivos
- Presets de configuración guardables
- Detección automática de idiomas
- Soporte para MP4 y otros contenedores
- Modo CLI
- Tests unitarios y de integración

---

[0.1.0]: https://github.com/Mabci/remuxeador/releases/tag/v0.1.0
