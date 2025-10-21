import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import platform
from pathlib import Path
import time

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reproductor de Videos - Servidor Local")
        self.root.geometry("900x600")
        
        # Configuración del servidor SMB
        self.server_ip = os.getenv("SERVER_IP")
        self.share_name = os.getenv("SHARE_NAME")
        self.smb_uri = f"smb://{self.server_ip}/{self.share_name}"
        
        # Intentar obtener la ruta GVFS
        self.smb_path = self.get_gvfs_path()
        self.current_path = self.smb_path
        
        # Extensiones de video soportadas
        self.video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        
        self.setup_ui()
        
        # Conectar al servidor e iniciar
        self.root.after(100, self.initialize_connection)
    
    def get_gvfs_path(self):
        """Busca la ruta GVFS del servidor SMB"""
        try:
            uid = os.getuid()
            gvfs_base = f"/run/user/{uid}/gvfs"
            
            if os.path.exists(gvfs_base):
                for mount in os.listdir(gvfs_base):
                    if f"server={self.server_ip}" in mount and f"share={self.share_name}" in mount:
                        return os.path.join(gvfs_base, mount)
            
            # Si no existe, devolver la ruta esperada
            return f"/run/user/{uid}/gvfs/smb-share:server={self.server_ip},share={self.share_name}"
        except:
            return f"/run/user/1000/gvfs/smb-share:server={self.server_ip},share={self.share_name}"
    
    def connect_to_server(self):
        """Conecta automáticamente al servidor SMB usando gio"""
        try:
            # Usar gio mount para montar el recurso SMB
            result = subprocess.run(
                ['gio', 'mount', self.smb_uri],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Esperar un momento para que se monte
            time.sleep(1)
            
            # Actualizar la ruta GVFS
            self.smb_path = self.get_gvfs_path()
            self.current_path = self.smb_path
            
            return True
            
        except subprocess.TimeoutExpired:
            return False
        except FileNotFoundError:
            messagebox.showwarning(
                "Herramienta no disponible",
                "No se pudo usar 'gio' para montar automáticamente.\n"
                "Por favor, conecta manualmente al servidor desde el explorador de archivos."
            )
            return False
        except Exception as e:
            return False
    
    def initialize_connection(self):
        """Inicializa la conexión y carga el directorio"""
        # Verificar si ya está montado
        if os.path.exists(self.smb_path):
            try:
                os.listdir(self.smb_path)  # Test de acceso
                self.load_directory(self.smb_path)
                return
            except:
                pass
        
        # Intentar conectar automáticamente
        self.info_label.config(text="🔄 Conectando al servidor...")
        self.root.update()
        
        if self.connect_to_server():
            if os.path.exists(self.smb_path):
                self.load_directory(self.smb_path)
            else:
                self.show_connection_error()
        else:
            self.show_connection_error()
    
    def show_connection_error(self):
        """Muestra diálogo de error de conexión con instrucciones"""
        msg = (
            f"No se pudo conectar automáticamente al servidor.\n\n"
            f"Por favor, conecta manualmente:\n"
            f"1. Abre el explorador de archivos\n"
            f"2. Presiona Ctrl+L y escribe: {self.smb_uri}\n"
            f"3. Ingresa tus credenciales si es necesario\n"
            f"4. Vuelve a abrir esta aplicación\n\n"
            f"O configura el montaje automático (ver README)"
        )
        
        response = messagebox.askretrycancel("Error de conexión", msg)
        
        if response:
            # Reintentar
            self.initialize_connection()
        else:
            self.root.destroy()
    
    def setup_ui(self):
        # Frame superior para la ruta actual
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Ruta actual:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        self.path_label = ttk.Label(top_frame, text="", font=('Arial', 9))
        self.path_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Botón para reconectar
        ttk.Button(top_frame, text="🔄 Reconectar", command=self.reconnect).pack(side=tk.RIGHT, padx=5)
        
        # Botón para volver atrás
        self.back_btn = ttk.Button(top_frame, text="← Atrás", command=self.go_back)
        self.back_btn.pack(side=tk.RIGHT, padx=5)
        
        # Botón para ir al inicio
        ttk.Button(top_frame, text="🏠 Inicio", command=self.go_home).pack(side=tk.RIGHT)
        
        # Frame para el listado de archivos
        list_frame = ttk.Frame(self.root, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview para mostrar carpetas y archivos
        self.tree = ttk.Treeview(list_frame, yscrollcommand=scrollbar.set, selectmode='browse')
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        self.tree['columns'] = ('tipo', 'tamaño')
        self.tree.column('#0', width=500, minwidth=200)
        self.tree.column('tipo', width=100, minwidth=80)
        self.tree.column('tamaño', width=100, minwidth=80)
        
        self.tree.heading('#0', text='Nombre', anchor=tk.W)
        self.tree.heading('tipo', text='Tipo', anchor=tk.W)
        self.tree.heading('tamaño', text='Tamaño', anchor=tk.W)
        
        # Eventos
        self.tree.bind('<Double-Button-1>', self.on_double_click)
        
        # Frame inferior para información
        info_frame = ttk.Frame(self.root, padding="10")
        info_frame.pack(fill=tk.X)
        
        self.info_label = ttk.Label(info_frame, text="Iniciando...", 
                                   font=('Arial', 9))
        self.info_label.pack()
    
    def reconnect(self):
        """Fuerza una reconexión al servidor"""
        self.initialize_connection()
    
    def load_directory(self, path):
        """Carga el contenido de un directorio"""
        self.tree.delete(*self.tree.get_children())
        self.current_path = path
        
        # Mostrar ruta más amigable
        display_path = path.replace(self.smb_path, "Servidor")
        if display_path == path:
            display_path = f"Servidor/{os.path.basename(path)}"
        
        self.path_label.config(text=display_path)
        
        try:
            items = os.listdir(path)
            items.sort()
            
            folders = []
            videos = []
            
            for item in items:
                if item.startswith('@') or item.startswith('.'):
                    continue
                
                full_path = os.path.join(path, item)
                
                if os.path.isdir(full_path):
                    folders.append(item)
                elif os.path.isfile(full_path):
                    ext = os.path.splitext(item)[1].lower()
                    if ext in self.video_extensions:
                        videos.append(item)
            
            # Insertar carpetas primero
            for folder in folders:
                self.tree.insert('', tk.END, text=f"📁 {folder}", values=('Carpeta', ''), tags=('folder',))
            
            # Insertar videos
            for video in videos:
                full_path = os.path.join(path, video)
                size = self.get_file_size(full_path)
                ext = os.path.splitext(video)[1].upper()[1:]
                self.tree.insert('', tk.END, text=f"🎬 {video}", values=(f'Video {ext}', size), tags=('video',))
            
            self.info_label.config(text=f"📁 {len(folders)} carpetas | 🎬 {len(videos)} videos")
            
        except PermissionError:
            messagebox.showerror("Error", "No tienes permisos para acceder a esta carpeta")
        except FileNotFoundError:
            messagebox.showerror("Error", "No se encontró el directorio. ¿Se desconectó el servidor?")
            self.show_connection_error()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el directorio: {str(e)}")
    
    def get_file_size(self, filepath):
        """Obtiene el tamaño del archivo en formato legible"""
        try:
            size = os.path.getsize(filepath)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "N/A"
    
    def on_double_click(self, event):
        """Maneja el doble clic en un elemento"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        name = item['text'].replace('📁 ', '').replace('🎬 ', '')
        tipo = item['values'][0]
        
        full_path = os.path.join(self.current_path, name)
        
        if tipo == 'Carpeta':
            self.load_directory(full_path)
        elif 'Video' in tipo:
            self.play_video(full_path)
    
    def play_video(self, video_path):
        """Reproduce un video usando el reproductor predeterminado del sistema"""
        try:
            system = platform.system()
            
            if system == 'Linux':
                # Intentar con varios reproductores comunes en Linux
                # MPV primero porque es más estable y ligero
                players = ['mpv', 'totem', 'gnome-videos', 'xdg-open', '/usr/bin/vlc']
                for player in players:
                    try:
                        # Usar DEVNULL para evitar output en terminal
                        subprocess.Popen([player, video_path], 
                                       stdout=subprocess.DEVNULL, 
                                       stderr=subprocess.DEVNULL)
                        self.info_label.config(text=f"▶️ Reproduciendo: {os.path.basename(video_path)}")
                        return
                    except FileNotFoundError:
                        continue
                messagebox.showerror("Error", "No se encontró ningún reproductor de video. Instala MPV con: sudo apt install mpv")
            
            elif system == 'Windows':
                os.startfile(video_path)
                self.info_label.config(text=f"▶️ Reproduciendo: {os.path.basename(video_path)}")
            
            elif system == 'Darwin':  # macOS
                subprocess.Popen(['open', video_path])
                self.info_label.config(text=f"▶️ Reproduciendo: {os.path.basename(video_path)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al reproducir el video: {str(e)}")
    
    def go_back(self):
        """Vuelve al directorio anterior"""
        if self.current_path != self.smb_path:
            parent_path = os.path.dirname(self.current_path)
            self.load_directory(parent_path)
    
    def go_home(self):
        """Vuelve al directorio raíz del servidor"""
        self.load_directory(self.smb_path)

def main():
    root = tk.Tk()
    app = VideoPlayerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
