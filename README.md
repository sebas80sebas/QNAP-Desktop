# 🖥️ QNAP File Desk

> A powerful desktop application for managing and interacting with your QNAP server

[English](#english) | [Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

### Overview

QNAP Desktop is a native desktop application designed to provide seamless access to your QNAP server resources. Currently focused on video playback, this application aims to become a comprehensive desktop client for managing all aspects of your QNAP server without relying on web interfaces like Plex or File Station.

**Current Status:** Video Player Module  
**Vision:** Full-featured desktop client for QNAP servers

![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)

### ✨ Current Features

- 📁 **Intuitive Navigation** - Browse folders with double-click
- 🎥 **Direct Playback** - Play videos without downloading
- 📊 **File Information** - View size and type of each video
- 🔙 **Easy Navigation** - Back and home buttons for quick movement
- 🎯 **Multiple Formats** - Supports MP4, AVI, MKV, MOV, WMV, FLV, WEBM, M4V
- 🖥️ **Cross-Platform** - Works on Linux, Windows, and macOS

### 🎯 Planned Features

The roadmap includes expanding QNAP Desktop into a complete management solution:

- 📂 **File Manager** - Upload, download, rename, delete files
- 🔍 **Advanced Search** - Find files across your entire QNAP storage
- ⚙️ **Server Management** - Monitor and configure server settings
- 👥 **User Management** - Handle permissions and user accounts
- 📦 **Backup Tools** - Automated backup and restore functionality
- 🔔 **Notifications** - Real-time alerts for server events
- 📈 **Resource Monitoring** - CPU, RAM, storage usage visualization
- 🗂️ **Photo Gallery** - Browse and manage your photo collection
- 🎵 **Music Player** - Audio playback with playlist support
- 📄 **Document Viewer** - Preview documents without downloading

### 📋 Prerequisites

#### System Requirements

**Linux (Ubuntu/Debian)**
```bash
# Python 3 (usually pre-installed)
sudo apt update
sudo apt install python3 python3-tk

# Video player (choose one)
sudo apt install mpv          # Recommended: lightweight and fast
# or
sudo apt install vlc          # Popular alternative
```

**Windows**
- Python 3.6+ ([Download here](https://www.python.org/downloads/))
- VLC Media Player ([Download here](https://www.videolan.org/vlc/))

**macOS**
```bash
# Install Python 3 if needed
brew install python3

# Install video player
brew install --cask mpv
# or
brew install --cask vlc
```

#### QNAP Server Connection

**Linux**
Mount your QNAP server using SMB/CIFS:

```bash
# Create mount point
sudo mkdir -p /mnt/qnap

# Manual mount (temporary)
sudo mount -t cifs //192.168.1.230/public /mnt/qnap -o username=YOUR_USER,password=YOUR_PASSWORD

# Or configure auto-mount in /etc/fstab
echo "//192.168.1.230/public /mnt/qnap cifs username=YOUR_USER,password=YOUR_PASSWORD,uid=1000,gid=1000 0 0" | sudo tee -a /etc/fstab
```

You can also use GNOME/KDE file manager to connect via SMB.

**Windows**
- Open File Explorer
- Type in address bar: `\\192.168.1.230\public`
- Enter credentials if prompted
- Map network drive if desired (right-click > "Map network drive")

**macOS**
- Open Finder
- Press `Cmd + K`
- Enter: `smb://192.168.1.230/public`
- Connect with your credentials

### 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/sebas80sebas/QNAP-Desktop.git
cd QNAP-Desktop/
```

2. **Configure server path**

Edit the `app.py` file and modify the line with your server path:

```python
# Linux
self.smb_path = "/run/user/1000/gvfs/smb-share:server=192.168.1.230,share=public"

# Or if manually mounted
self.smb_path = "/mnt/qnap"

# Windows
self.smb_path = "Z:\\"  # Or your mapped drive letter

# macOS
self.smb_path = "/Volumes/public"
```

3. **Run the application**
```bash
python3 app.py
```

### 📖 Usage

1. **Launch the app** - Run `python3 app.py`
2. **Browse folders** - Double-click any folder to open it
3. **Play videos** - Double-click any video to play it
4. **Go back** - Use "← Back" button to go to previous folder
5. **Home** - Use "🏠 Home" button to return to server root

### 🛠️ Troubleshooting

**Error: "No video player found"**
Install a compatible video player:
```bash
sudo apt install mpv
```

**VLC error on Linux (symbol lookup error)**
This is a known conflict with snap. Solutions:

*Option 1: Use MPV (recommended)*
```bash
sudo apt install mpv
```

*Option 2: Reinstall VLC from apt*
```bash
sudo snap remove vlc
sudo apt remove vlc
sudo apt install vlc
```

**Cannot access server**
Verify that:
- QNAP server is powered on and on the same network
- You have correct access permissions
- The path in the code is correct for your system
- The shared resource is properly mounted

**Permission error on Linux**
```bash
# Ensure you have permissions on mounted folder
sudo chown -R $USER:$USER /mnt/qnap
```

### 🔧 Advanced Configuration

**Change supported video formats**

Edit the `video_extensions` list in `app.py`:

```python
self.video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.m2ts'}
```

**Change default player**

Modify the order of the `players` list in the `play_video()` method:

```python
players = ['mpv', 'vlc', 'totem', 'xdg-open']
```

### 🤝 Contributing

Contributions are welcome! This project is in active development, and we're looking to expand it into a full-featured QNAP desktop client. Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 👨‍💻 Author

**Sebas**
- GitHub: [@sebas80sebas](https://github.com/sebas80sebas)

---

<a name="español"></a>
## 🇪🇸 Español

### Descripción general

QNAP Desktop es una aplicación de escritorio nativa diseñada para proporcionar acceso fluido a los recursos de tu servidor QNAP. Actualmente enfocada en la reproducción de videos, esta aplicación aspira a convertirse en un cliente de escritorio completo para gestionar todos los aspectos de tu servidor QNAP sin depender de interfaces web como Plex o File Station.

**Estado actual:** Módulo de reproductor de video  
**Visión:** Cliente de escritorio completo para servidores QNAP

### ✨ Características actuales

- 📁 **Navegación intuitiva** - Explora carpetas con doble clic
- 🎥 **Reproducción directa** - Reproduce videos sin necesidad de descargarlos
- 📊 **Información de archivos** - Visualiza el tamaño y tipo de cada video
- 🔙 **Navegación fácil** - Botones para volver atrás y al directorio raíz
- 🎯 **Múltiples formatos** - Compatible con MP4, AVI, MKV, MOV, WMV, FLV, WEBM, M4V
- 🖥️ **Multiplataforma** - Funciona en Linux, Windows y macOS

### 🎯 Características planificadas

La hoja de ruta incluye expandir QNAP Desktop en una solución de gestión completa:

- 📂 **Gestor de archivos** - Subir, descargar, renombrar, eliminar archivos
- 🔍 **Búsqueda avanzada** - Encuentra archivos en todo tu almacenamiento QNAP
- ⚙️ **Gestión del servidor** - Monitoriza y configura los ajustes del servidor
- 👥 **Gestión de usuarios** - Administra permisos y cuentas de usuario
- 📦 **Herramientas de backup** - Funcionalidad de copia de seguridad y restauración automatizada
- 🔔 **Notificaciones** - Alertas en tiempo real para eventos del servidor
- 📈 **Monitorización de recursos** - Visualización del uso de CPU, RAM y almacenamiento
- 🗂️ **Galería de fotos** - Navega y gestiona tu colección de fotos
- 🎵 **Reproductor de música** - Reproducción de audio con soporte de listas de reproducción
- 📄 **Visor de documentos** - Previsualiza documentos sin descargarlos

### 📋 Requisitos previos

#### Requisitos del sistema

**Linux (Ubuntu/Debian)**
```bash
# Python 3 (generalmente ya viene instalado)
sudo apt update
sudo apt install python3 python3-tk

# Reproductor de video (elige uno)
sudo apt install mpv          # Recomendado: ligero y rápido
# o
sudo apt install vlc          # Alternativa popular
```

**Windows**
- Python 3.6 o superior ([Descargar aquí](https://www.python.org/downloads/))
- VLC Media Player ([Descargar aquí](https://www.videolan.org/vlc/))

**macOS**
```bash
# Instalar Python 3 si no lo tienes
brew install python3

# Instalar reproductor de video
brew install --cask mpv
# o
brew install --cask vlc
```

#### Conexión al servidor QNAP

**Linux**
Monta tu servidor QNAP usando SMB/CIFS:

```bash
# Crear punto de montaje
sudo mkdir -p /mnt/qnap

# Montar manualmente (temporal)
sudo mount -t cifs //192.168.1.230/public /mnt/qnap -o username=TU_USUARIO,password=TU_PASSWORD

# O configurar montaje automático en /etc/fstab
echo "//192.168.1.230/public /mnt/qnap cifs username=TU_USUARIO,password=TU_PASSWORD,uid=1000,gid=1000 0 0" | sudo tee -a /etc/fstab
```

También puedes usar el explorador de archivos de GNOME/KDE para conectarte vía SMB.

**Windows**
- Abre el Explorador de archivos
- En la barra de direcciones escribe: `\\192.168.1.230\public`
- Ingresa tus credenciales si es necesario
- Mapea la unidad de red si deseas (clic derecho > "Conectar a unidad de red")

**macOS**
- Abre Finder
- Presiona `Cmd + K`
- Ingresa: `smb://192.168.1.230/public`
- Conecta con tus credenciales

### 🚀 Instalación

1. **Clona el repositorio**
```bash
git clone https://github.com/sebas80sebas/QNAP-Desktop.git
cd QNAP-Desktop/
```

2. **Configura la ruta del servidor**

Edita el archivo `app.py` y modifica la línea con la ruta de tu servidor:

```python
# Linux
self.smb_path = "/run/user/1000/gvfs/smb-share:server=192.168.1.230,share=public"

# O si montaste manualmente
self.smb_path = "/mnt/qnap"

# Windows
self.smb_path = "Z:\\"  # O la letra de tu unidad mapeada

# macOS
self.smb_path = "/Volumes/public"
```

3. **Ejecuta la aplicación**
```bash
python3 app.py
```

### 📖 Uso

1. **Inicia la aplicación** - Ejecuta `python3 app.py`
2. **Navega por carpetas** - Haz doble clic en cualquier carpeta para abrirla
3. **Reproduce videos** - Haz doble clic en cualquier video para reproducirlo
4. **Vuelve atrás** - Usa el botón "← Atrás" para retroceder
5. **Inicio** - Usa el botón "🏠 Inicio" para volver a la raíz del servidor

### 🛠️ Solución de problemas

**Error: "No se encontró ningún reproductor de video"**
Instala un reproductor de video compatible:
```bash
sudo apt install mpv
```

**Error de VLC en Linux (symbol lookup error)**
Este es un conflicto conocido con snap. Soluciones:

*Opción 1: Usar MPV (recomendado)*
```bash
sudo apt install mpv
```

*Opción 2: Reinstalar VLC desde apt*
```bash
sudo snap remove vlc
sudo apt remove vlc
sudo apt install vlc
```

**No puedo acceder al servidor**
Verifica que:
- El servidor QNAP está encendido y en la misma red
- Tienes los permisos correctos de acceso
- La ruta en el código es correcta para tu sistema
- El recurso compartido está montado correctamente

**Error de permisos en Linux**
```bash
# Asegúrate de que tienes permisos en la carpeta montada
sudo chown -R $USER:$USER /mnt/qnap
```

### 🔧 Configuración avanzada

**Cambiar formatos de video soportados**

Edita la lista `video_extensions` en el archivo `app.py`:

```python
self.video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.m2ts'}
```

**Cambiar reproductor predeterminado**

Modifica el orden de la lista `players` en el método `play_video()`:

```python
players = ['mpv', 'vlc', 'totem', 'xdg-open']
```

### 🤝 Contribuir

¡Las contribuciones son bienvenidas! Este proyecto está en desarrollo activo, y buscamos expandirlo en un cliente de escritorio completo para QNAP. Siéntete libre de:

- Reportar errores
- Sugerir nuevas funcionalidades
- Enviar pull requests
- Mejorar la documentación

### 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

### 👨‍💻 Autor

**Sebas**
- GitHub: [@sebas80sebas](https://github.com/sebas80sebas)