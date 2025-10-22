import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import platform
from pathlib import Path
from PIL import Image, ImageTk
import time

class VideoPlayerApp:
    def __init__(self, root):
        """
        Initialize the Video Player Application
        
        Args:
            root: The main Tkinter window instance
        """
        self.root = root
        self.root.title("Video Player - Local Server")
        self.root.geometry("900x600")
        
        # SMB server configuration
        # Read server IP and share name from environment variables
        self.server_ip = os.getenv("SERVER_IP")
        self.share_name = os.getenv("SHARE_NAME")
        self.smb_uri = f"smb://{self.server_ip}/{self.share_name}"
        
        # Attempt to get the GVFS path (Linux virtual filesystem for network shares)
        self.smb_path = self.get_gvfs_path()
        self.current_path = self.smb_path
        
        # Supported video file extensions
        self.video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        self.document_extensions = {'.pdf'}

        # Setup the user interface
        self.setup_ui()
        
        # Connect to server and start after 100ms
        self.root.after(100, self.initialize_connection)
    
    def get_gvfs_path(self):
        """
        Search for the GVFS path of the SMB server
        GVFS (GNOME Virtual File System) is used by Linux to mount network shares
        
        Returns:
            str: The GVFS mount path for the SMB share
        """
        try:
            # Get user ID for constructing GVFS path
            uid = os.getuid()
            gvfs_base = f"/run/user/{uid}/gvfs"
            
            # Check if GVFS base directory exists
            if os.path.exists(gvfs_base):
                # Look through mounted shares for matching server and share name
                for mount in os.listdir(gvfs_base):
                    if f"server={self.server_ip}" in mount and f"share={self.share_name}" in mount:
                        return os.path.join(gvfs_base, mount)
            
            # If not found, return the expected path format
            return f"/run/user/{uid}/gvfs/smb-share:server={self.server_ip},share={self.share_name}"
        except:
            # Fallback to default user ID 1000 if there's an error
            return f"/run/user/1000/gvfs/smb-share:server={self.server_ip},share={self.share_name}"
    
    def connect_to_server(self):
        """
        Automatically connect to the SMB server using gio mount command
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            # Use gio mount to mount the SMB resource
            result = subprocess.run(
                ['gio', 'mount', self.smb_uri],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Wait a moment for the mount to complete
            time.sleep(1)
            
            # Update the GVFS path after mounting
            self.smb_path = self.get_gvfs_path()
            self.current_path = self.smb_path
            
            return True
            
        except subprocess.TimeoutExpired:
            # Connection timed out
            return False
        except FileNotFoundError:
            # gio command not found on the system
            messagebox.showwarning(
                "Tool Not Available",
                "Could not use 'gio' to mount automatically.\n"
                "Please connect manually to the server from the file manager."
            )
            return False
        except Exception as e:
            # Generic error handling
            return False
    
    def initialize_connection(self):
        """
        Initialize the connection and load the directory
        First checks if already mounted, then attempts automatic connection
        """
        # Check if the share is already mounted and accessible
        if os.path.exists(self.smb_path):
            try:
                os.listdir(self.smb_path)  # Test access to the directory
                self.load_directory(self.smb_path)
                return
            except:
                pass
        
        # Attempt automatic connection
        self.info_label.config(text="🔄 Connecting to server...")
        self.root.update()
        
        if self.connect_to_server():
            if os.path.exists(self.smb_path):
                self.load_directory(self.smb_path)
            else:
                self.show_connection_error()
        else:
            self.show_connection_error()
    
    def show_connection_error(self):
        """
        Display connection error dialog with manual connection instructions
        """
        msg = (
            f"Could not automatically connect to the server.\n\n"
            f"Please connect manually:\n"
            f"1. Open the file manager\n"
            f"2. Press Ctrl+L and type: {self.smb_uri}\n"
            f"3. Enter your credentials if prompted\n"
            f"4. Reopen this application\n\n"
            f"Or configure automatic mounting (see README)"
        )
        
        response = messagebox.askretrycancel("Connection Error", msg)
        
        if response:
            # Retry connection
            self.initialize_connection()
        else:
            # Close application
            self.root.destroy()
    
    def setup_ui(self):
        """
        Setup the user interface components
        Creates the layout with path display, navigation buttons, file tree, and status bar
        """
        # Top frame for current path display
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Current path:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        # Label to display current directory path
        self.path_label = ttk.Label(top_frame, text="", font=('Arial', 9))
        self.path_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Reconnect button
        ttk.Button(top_frame, text="🔄 Reconnect", command=self.reconnect).pack(side=tk.RIGHT, padx=5)
        
        # Back button to navigate to parent directory
        self.back_btn = ttk.Button(top_frame, text="← Back", command=self.go_back)
        self.back_btn.pack(side=tk.RIGHT, padx=5)
        
        # Home button to return to root directory
        ttk.Button(top_frame, text="🏠 Home", command=self.go_home).pack(side=tk.RIGHT)
        
        # Frame for file listing
        list_frame = ttk.Frame(self.root, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for the file tree
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview widget to display folders and files
        self.tree = ttk.Treeview(list_frame, yscrollcommand=scrollbar.set, selectmode='browse')
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Configure columns for the tree view
        self.tree['columns'] = ('tipo', 'tamaño')
        self.tree.column('#0', width=500, minwidth=200)
        self.tree.column('tipo', width=100, minwidth=80)
        self.tree.column('tamaño', width=100, minwidth=80)
        
        # Set column headings
        self.tree.heading('#0', text='Name', anchor=tk.W)
        self.tree.heading('tipo', text='Type', anchor=tk.W)
        self.tree.heading('tamaño', text='Size', anchor=tk.W)
        
        # Bind double-click event to tree items
        self.tree.bind('<Double-Button-1>', self.on_double_click)
        
        # Bottom frame for status information
        info_frame = ttk.Frame(self.root, padding="10")
        info_frame.pack(fill=tk.X)
        
        # Status label to show current operation or statistics
        self.info_label = ttk.Label(info_frame, text="Starting...", 
                                   font=('Arial', 9))
        self.info_label.pack()
    
    def reconnect(self):
        """
        Force a reconnection to the server
        Called when user clicks the Reconnect button
        """
        self.initialize_connection()
    
    def load_directory(self, path):
        """
        Load and display the contents of a directory
        
        Args:
            path: Full path to the directory to load
        """
        # Clear existing items from tree
        self.tree.delete(*self.tree.get_children())
        self.current_path = path
        
        # Create a more user-friendly display path
        display_path = path.replace(self.smb_path, "Server")
        if display_path == path:
            display_path = f"Server/{os.path.basename(path)}"
        
        self.path_label.config(text=display_path)
        
        try:
            # Get list of items in directory
            items = os.listdir(path)
            items.sort()
            
            folders = []
            videos = []
            documents = []

            # Separate folders and video files
            for item in items:
                # Skip hidden and system files (starting with @ or .)
                if item.startswith('@') or item.startswith('.'):
                    continue
                
                full_path = os.path.join(path, item)
                
                if os.path.isdir(full_path):
                    folders.append(item)
                elif os.path.isfile(full_path):
                    ext = os.path.splitext(item)[1].lower()
                    if ext in self.video_extensions:
                        videos.append(item)
                    elif ext in self.document_extensions:
                        documents.append(item)
            
            # Insert folders first (with folder icon emoji)
            for folder in folders:
                self.tree.insert('', tk.END, text=f"📁 {folder}", values=('Folder', ''), tags=('folder',))
            
            # Insert videos (with film icon emoji)
            for video in videos:
                full_path = os.path.join(path, video)
                size = self.get_file_size(full_path)
                ext = os.path.splitext(video)[1].upper()[1:]  # Get extension without dot
                self.tree.insert('', tk.END, text=f"🎬 {video}", values=(f'Video {ext}', size), tags=('video',))
            
            # Insert documents (with document icon emoji)
            for doc in documents:
                full_path = os.path.join(path, doc)
                size = self.get_file_size(full_path)
                ext = os.path.splitext(doc)[1].upper()[1:]
                self.tree.insert('', tk.END, text=f"📄 {doc}", values=(f'Document {ext}', size), tags=('document',))

            # Update status label with count of items
            self.info_label.config(text=f"📁 {len(folders)} folders | 🎬 {len(videos)} videos | 📄 {len(documents)} documents")

        except PermissionError:
            messagebox.showerror("Error", "You don't have permission to access this folder")
        except FileNotFoundError:
            messagebox.showerror("Error", "Directory not found. Did the server disconnect?")
            self.show_connection_error()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading directory: {str(e)}")
    
    def get_file_size(self, filepath):
        """
        Get file size in human-readable format
        
        Args:
            filepath: Full path to the file
            
        Returns:
            str: Formatted file size (e.g., "1.5 GB")
        """
        try:
            size = os.path.getsize(filepath)
            # Convert to appropriate unit
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "N/A"
    
    def on_double_click(self, event):
        """
        Handle double-click events on tree items
        Opens folders or plays videos depending on item type
        
        Args:
            event: The click event object
        """
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get item data
        item = self.tree.item(selection[0])
        name = item['text'].replace('📁 ', '').replace('🎬 ', '').replace('📄 ', '')
        tipo = item['values'][0]
        
        full_path = os.path.join(self.current_path, name)
        
        # Navigate into folder or play video
        if tipo == 'Folder':
            self.load_directory(full_path)
        elif 'Video' in tipo:
            self.play_video(full_path)
        elif 'Document' in tipo:
            self.open_document(full_path)
    
    def open_document(self, doc_path):
        """Opens a document with integrated or external viewer"""
        ext = os.path.splitext(doc_path)[1].lower()
        
        if ext == '.pdf':
            # For PDF files, use the integrated viewer
            self.open_pdf_viewer(doc_path)
        else:
            # For other document types, open with external application
            self.open_external(doc_path, "document")

    def play_video(self, video_path):
        """
        Play a video using the system's default video player
        Tries multiple players on Linux for better compatibility
        
        Args:
            video_path: Full path to the video file
        """
        try:
            system = platform.system()
            
            if system == 'Linux':
                # Try various common Linux video players
                # MPV is tried first because it's more stable and lightweight
                players = ['mpv', 'totem', 'gnome-videos', 'xdg-open', '/usr/bin/vlc']
                for player in players:
                    try:
                        # Use DEVNULL to avoid terminal output
                        subprocess.Popen([player, video_path], 
                                       stdout=subprocess.DEVNULL, 
                                       stderr=subprocess.DEVNULL)
                        self.info_label.config(text=f"▶️ Playing: {os.path.basename(video_path)}")
                        return
                    except FileNotFoundError:
                        # Try next player if this one isn't found
                        continue
                # If no player was found, show error
                messagebox.showerror("Error", "No video player found. Install MPV with: sudo apt install mpv")
            
            elif system == 'Windows':
                # Use Windows default file handler
                os.startfile(video_path)
                self.info_label.config(text=f"▶️ Playing: {os.path.basename(video_path)}")
            
            elif system == 'Darwin':  # macOS
                # Use macOS 'open' command
                subprocess.Popen(['open', video_path])
                self.info_label.config(text=f"▶️ Playing: {os.path.basename(video_path)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error playing video: {str(e)}")
    
    def open_pdf_viewer(self, pdf_path):
        """Integrated viewer for PDF files"""
        viewer = tk.Toplevel(self.root)
        viewer.title(f"📄 {os.path.basename(pdf_path)}")
        viewer.geometry("900x700")
        
        try:
            import fitz  # PyMuPDF library for PDF handling
            
            # Control frame for navigation buttons and tools
            control_frame = ttk.Frame(viewer)
            control_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # State variables
            current_page = tk.IntVar(value=1)
            zoom_level = tk.DoubleVar(value=1.0)
            
            # Open PDF document
            pdf_doc = fitz.open(pdf_path)
            total_pages = pdf_doc.page_count
            
            # Canvas frame for PDF display
            canvas_frame = ttk.Frame(viewer)
            canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Create scrollable canvas with dark background
            canvas = tk.Canvas(canvas_frame, bg='#2b2b2b')
            scrollbar_y = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
            scrollbar_x = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
            
            # Configure scrollbars
            canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
            
            # Pack scrollbars and canvas
            scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
            scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            def render_page():
                """Renders the current page with current zoom level"""
                page = pdf_doc[current_page.get() - 1]
                
                # Apply zoom transformation
                zoom = zoom_level.get()
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image format
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Convert to Tkinter PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Clear previous content
                canvas.delete("all")
                
                # Display new image
                canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                canvas.image = photo  # Keep reference to prevent garbage collection
                
                # Update scroll region
                canvas.configure(scrollregion=canvas.bbox("all"))
                
                # Update status labels
                page_label.config(text=f"Page {current_page.get()} of {total_pages}")
                zoom_label.config(text=f"Zoom: {int(zoom * 100)}%")
            
            def prev_page():
                """Navigate to previous page if available"""
                if current_page.get() > 1:
                    current_page.set(current_page.get() - 1)
                    render_page()
            
            def next_page():
                """Navigate to next page if available"""
                if current_page.get() < total_pages:
                    current_page.set(current_page.get() + 1)
                    render_page()
            
            def go_to_page():
                """Jump to specific page number"""
                try:
                    page = int(page_entry.get())
                    if 1 <= page <= total_pages:
                        current_page.set(page)
                        render_page()
                except ValueError:
                    pass
            
            def zoom_in():
                """Increase zoom level up to 300%"""
                new_zoom = min(zoom_level.get() + 0.2, 3.0)
                zoom_level.set(new_zoom)
                render_page()
            
            def zoom_out():
                """Decrease zoom level down to 40%"""
                new_zoom = max(zoom_level.get() - 0.2, 0.4)
                zoom_level.set(new_zoom)
                render_page()
            
            def zoom_fit():
                """Reset zoom to 100%"""
                zoom_level.set(1.0)
                render_page()
            
            def on_mouse_wheel(event):
                """Handle mouse wheel events for scrolling and zooming
                Ctrl + wheel = zoom
                Wheel only = vertical scroll
                """
                if event.state & 0x0004:  # Ctrl key pressed
                    if event.delta > 0 or event.num == 4:
                        zoom_in()
                    else:
                        zoom_out()
                else:  # Normal scroll
                    if event.delta > 0 or event.num == 4:
                        canvas.yview_scroll(-1, "units")
                    else:
                        canvas.yview_scroll(1, "units")
            
            # Navigation controls
            ttk.Button(control_frame, text="◀ Previous", command=prev_page).pack(side=tk.LEFT, padx=2)
            ttk.Button(control_frame, text="Next ▶", command=next_page).pack(side=tk.LEFT, padx=2)
            
            # Page indicator and navigation
            page_label = ttk.Label(control_frame, text=f"Page 1 of {total_pages}")
            page_label.pack(side=tk.LEFT, padx=10)
            
            ttk.Label(control_frame, text="Go to:").pack(side=tk.LEFT, padx=2)
            page_entry = ttk.Entry(control_frame, width=5)
            page_entry.pack(side=tk.LEFT, padx=2)
            page_entry.bind('<Return>', lambda e: go_to_page())
            
            ttk.Button(control_frame, text="Go", command=go_to_page).pack(side=tk.LEFT, padx=2)
            
            # Visual separator
            ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
            
            # Zoom controls
            ttk.Button(control_frame, text="🔍−", command=zoom_out, width=3).pack(side=tk.LEFT, padx=2)
            ttk.Button(control_frame, text="🔍+", command=zoom_in, width=3).pack(side=tk.LEFT, padx=2)
            ttk.Button(control_frame, text="Fit", command=zoom_fit).pack(side=tk.LEFT, padx=2)
            
            zoom_label = ttk.Label(control_frame, text="Zoom: 100%")
            zoom_label.pack(side=tk.LEFT, padx=5)
            
            ttk.Button(control_frame, text="Close", command=viewer.destroy).pack(side=tk.RIGHT, padx=5)
            
            # Key and mouse bindings
            canvas.bind("<MouseWheel>", on_mouse_wheel)  # Windows/MacOS
            canvas.bind("<Button-4>", on_mouse_wheel)    # Linux scroll up
            canvas.bind("<Button-5>", on_mouse_wheel)    # Linux scroll down
            
            # Keyboard shortcuts
            viewer.bind('<Left>', lambda e: prev_page())
            viewer.bind('<Right>', lambda e: next_page())
            viewer.bind('<plus>', lambda e: zoom_in())
            viewer.bind('<minus>', lambda e: zoom_out())
            viewer.bind('<Control-plus>', lambda e: zoom_in())
            viewer.bind('<Control-minus>', lambda e: zoom_out())
            viewer.bind('<Control-0>', lambda e: zoom_fit())
            
            # Display first page
            render_page()
            
            # Update status
            self.info_label.config(text=f"📄 Viewing PDF: {os.path.basename(pdf_path)}")
            
        except ImportError:
            # PyMuPDF not installed
            viewer.destroy()
        except Exception as e:
            # Handle other errors
            viewer.destroy()
            messagebox.showerror("Error", f"Error loading PDF: {str(e)}")
    
    def go_back(self):
        """
        Navigate to the parent directory
        Only works if not already at the root server directory
        """
        if self.current_path != self.smb_path:
            parent_path = os.path.dirname(self.current_path)
            self.load_directory(parent_path)
    
    def go_home(self):
        """
        Navigate back to the server root directory
        """
        self.load_directory(self.smb_path)

def main():
    """
    Main entry point for the application
    Checks for graphical environment before launching GUI
    """
    # Check if there's a graphical environment (Linux with X11 or Windows)
    if os.environ.get("DISPLAY") or os.name == "nt":
        root = tk.Tk()
        app = VideoPlayerApp(root)
        root.mainloop()
    else:
        print("🔸 No graphical environment detected, running in console mode.")
        return

if __name__ == "__main__":
    main()
