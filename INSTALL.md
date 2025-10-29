# 📦 Guía de Instalación Detallada

Esta guía proporciona instrucciones paso a paso para instalar el Remuxeador FFmpeg en diferentes sistemas operativos.

---

## 📑 Tabla de Contenidos

- [Windows](#-windows)
- [Linux (Ubuntu/Debian)](#-linux-ubuntudebian)
- [macOS](#-macos)
- [Verificación de Instalación](#-verificación-de-instalación)
- [Solución de Problemas](#-solución-de-problemas)

---

## 🪟 Windows

### Requisitos Previos
- Windows 10 o superior
- Python 3.10 o superior

### Paso 1: Instalar Python

1. Descarga Python desde [python.org](https://www.python.org/downloads/)
2. Durante la instalación, **marca la casilla "Add Python to PATH"**
3. Verifica la instalación:
   ```cmd
   python --version
   ```

### Paso 2: Instalar MKVToolNix

1. Descarga MKVToolNix desde [mkvtoolnix.download](https://mkvtoolnix.download/downloads.html#windows)
2. Ejecuta el instalador
3. Durante la instalación, asegúrate de que se agregue al PATH
4. Verifica la instalación:
   ```cmd
   mkvmerge --version
   ```

### Paso 3: Clonar o Descargar el Proyecto

**Opción A: Con Git**
```cmd
git clone https://github.com/Mabci/remuxeador.git
cd remuxeador
```

**Opción B: Descarga Manual**
1. Descarga el ZIP desde GitHub
2. Extrae en una carpeta de tu elección
3. Abre CMD en esa carpeta

### Paso 4: Crear Entorno Virtual

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Deberías ver `(.venv)` al inicio de tu línea de comando.

### Paso 5: Instalar Dependencias

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 6: Ejecutar la Aplicación

```cmd
python main.py
```

### Notas Adicionales para Windows

- **MPV ya está incluido** en `external/mpv/`, no necesitas instalarlo
- Si tienes problemas con permisos, ejecuta CMD como administrador
- Si `mkvmerge` no se encuentra, agrega manualmente la carpeta de MKVToolNix al PATH:
  1. Busca "Variables de entorno" en el menú inicio
  2. Edita la variable PATH
  3. Agrega: `C:\Program Files\MKVToolNix`

---

## 🐧 Linux (Ubuntu/Debian)

### Requisitos Previos
- Ubuntu 20.04+ o Debian 11+
- Python 3.10 o superior

### Paso 1: Actualizar Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### Paso 2: Instalar Python y Dependencias del Sistema

```bash
# Python 3.10+ (Ubuntu 22.04+ ya lo incluye)
sudo apt install -y python3 python3-pip python3-venv

# Verificar versión
python3 --version
```

Si tienes una versión anterior a 3.10, instala desde deadsnakes PPA:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

### Paso 3: Instalar MKVToolNix

```bash
sudo apt install -y mkvtoolnix

# Verificar instalación
mkvmerge --version
```

### Paso 4: Instalar MPV (Opcional pero Recomendado)

```bash
sudo apt install -y mpv libmpv-dev

# Verificar instalación
mpv --version
```

### Paso 5: Clonar el Proyecto

```bash
git clone https://github.com/Mabci/remuxeador.git
cd remuxeador
```

### Paso 6: Crear Entorno Virtual

```bash
# Si usas Python 3.11
python3.11 -m venv .venv

# Si usas Python 3.10 o el default
python3 -m venv .venv

# Activar entorno
source .venv/bin/activate
```

### Paso 7: Instalar Dependencias de Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 8: Ejecutar la Aplicación

```bash
python main.py
```

### Notas Adicionales para Linux

- Si tienes problemas con `python-mpv`, instala `libmpv-dev`:
  ```bash
  sudo apt install libmpv-dev
  ```

- Para sistemas con Wayland, MPV podría necesitar configuración adicional:
  ```bash
  export QT_QPA_PLATFORM=wayland
  ```

- Si usas ARM (Raspberry Pi, etc.), asegúrate de tener las versiones ARM de las herramientas

---

## 🍎 macOS

### Requisitos Previos
- macOS 11 (Big Sur) o superior
- Homebrew instalado

### Paso 1: Instalar Homebrew (si no lo tienes)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Paso 2: Instalar Python

```bash
brew install python@3.11

# Verificar instalación
python3 --version
```

### Paso 3: Instalar MKVToolNix

```bash
brew install mkvtoolnix

# Verificar instalación
mkvmerge --version
```

### Paso 4: Instalar MPV (Opcional pero Recomendado)

```bash
brew install mpv

# Verificar instalación
mpv --version
```

### Paso 5: Clonar el Proyecto

```bash
git clone https://github.com/Mabci/remuxeador.git
cd remuxeador
```

### Paso 6: Crear Entorno Virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Paso 7: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 8: Ejecutar la Aplicación

```bash
python main.py
```

### Notas Adicionales para macOS

- Si tienes problemas con permisos, usa `sudo` solo cuando sea necesario
- PyQt6 puede requerir permisos de accesibilidad en Preferencias del Sistema
- En macOS con Apple Silicon (M1/M2), asegúrate de usar versiones ARM de las herramientas

---

## ✅ Verificación de Instalación

Después de completar la instalación, verifica que todo funcione:

### 1. Verificar Python
```bash
python --version
# Debería mostrar Python 3.10 o superior
```

### 2. Verificar MKVMerge
```bash
mkvmerge --version
# Debería mostrar la versión de MKVToolNix
```

### 3. Verificar MPV (Opcional)
```bash
mpv --version
# Debería mostrar la versión de MPV
```

### 4. Verificar Dependencias de Python
```bash
# Activar entorno virtual primero
python -c "import PyQt6; print('PyQt6 OK')"
python -c "import mpv; print('python-mpv OK')"
```

### 5. Ejecutar la Aplicación
```bash
python main.py
```

Si la aplicación se abre sin errores, ¡la instalación fue exitosa! 🎉

---

## 🔧 Solución de Problemas

### Error: "MKVMerge no encontrado"

**Causa**: MKVToolNix no está instalado o no está en el PATH.

**Solución**:
1. Verifica que esté instalado: `mkvmerge --version`
2. Si no está instalado, sigue los pasos de instalación de tu OS
3. Si está instalado pero no se encuentra, agrega la ruta al PATH

### Error: "No se puede cargar libmpv"

**Causa**: MPV no está instalado o falta la librería compartida.

**Solución**:
- **Windows**: MPV está incluido en `external/mpv/`, no deberías tener este error
- **Linux**: `sudo apt install libmpv-dev`
- **macOS**: `brew install mpv`

### Error: "ModuleNotFoundError: No module named 'PyQt6'"

**Causa**: Las dependencias no se instalaron correctamente.

**Solución**:
```bash
# Asegúrate de estar en el entorno virtual
pip install --upgrade pip
pip install -r requirements.txt
```

### Error: "Permission denied" al ejecutar

**Causa**: Problemas de permisos en el archivo o directorio.

**Solución**:
- **Linux/macOS**: 
  ```bash
  chmod +x main.py
  ```
- **Windows**: Ejecuta CMD como administrador

### La aplicación se cierra inmediatamente

**Causa**: Probablemente un error de Python o dependencias.

**Solución**:
1. Ejecuta desde terminal para ver el error:
   ```bash
   python main.py
   ```
2. Lee el mensaje de error y busca en los issues de GitHub
3. Verifica que todas las dependencias estén instaladas

### Previsualización de video no funciona

**Causa**: MPV no está instalado o configurado correctamente.

**Solución**:
- La previsualización es **opcional**, el remuxeo funcionará sin ella
- Si quieres la previsualización, instala MPV siguiendo los pasos de tu OS
- Verifica: `mpv --version`

### Archivos no se emparejan en Dual Sync

**Causa**: Los nombres de archivo no siguen el patrón esperado.

**Solución**:
- Los archivos deben tener números de episodio en el nombre
- Ejemplos válidos: `Serie_EP01.mkv`, `Anime - 01.mkv`, `Show.E01.mkv`
- Los números deben coincidir entre archivos JP y LAT

---

## 📞 ¿Necesitas Más Ayuda?

Si sigues teniendo problemas:

1. **Revisa los logs**: Busca en la carpeta `logs/` el archivo más reciente
2. **Busca en Issues**: [GitHub Issues](https://github.com/Mabci/remuxeador/issues)
3. **Crea un nuevo Issue**: Incluye:
   - Tu sistema operativo y versión
   - Versión de Python
   - Mensaje de error completo
   - Logs relevantes

---

## 🚀 Próximos Pasos

Una vez instalado, lee el [README.md](README.md) para aprender a usar la aplicación.

¡Disfruta del Remuxeador FFmpeg! 🎬
