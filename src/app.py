import customtkinter as ctk
from tkinter import filedialog
import os
import threading
import sys
import subprocess
import ctypes
import datetime
import shutil
from PIL import Image
try:
    import gdown
except ImportError:
    gdown = None
from compressor import VideoCompressor

# Set appearance and theme
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue") 

# Fix for PyInstaller noconsole mode:
# Redirect stdout/stderr to bit bucket if they are None (which happens in windowed apps)
# This prevents libraries like gdown/tqdm from crashing when they try to print.
class NullWriter:
    def write(self, text):
        pass
    def flush(self):
        pass

if sys.stdout is None:
    sys.stdout = NullWriter()
if sys.stderr is None:
    sys.stderr = NullWriter()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ITG Video Compressor")
        self.geometry("1200x950")
        self.resizable(True, True)
        
        # Initialize icon_image to prevent errors
        self.icon_image = None
        
        # Set window icon (for both title bar and Windows taskbar)
        # We'll set it after window is fully initialized using after()
        self.after(100, self._set_window_icon)
        
        # Theme Palettes
        self.palettes = {
            "Light": {
                "bg": "#F0F2F5",            # Modern Dashboard Gray
                "card": "#FFFFFF",          # Pure White
                "accent": "#FF9F43",        # Softer, Professional Orange
                "accent_hover": "#F28C28",  # Deeper Orange
                "text": "#101828",          # Dark Slate Blue-Black
                "text_scd": "#667085",      # Cool Gray
                "btn_bg": "#FFFFFF",        # White buttons
                "btn_hover": "#F7F9FC",     # very subtle hover
                "btn_border": "#E4E7EC",    # Light border
                "entry_bg": "#FFFFFF",
                "logo_light": True
            },
            "Dark": {
                "bg": "#121212",
                "card": "#1E1E1E",
                "accent": "#FF9F43",
                "accent_hover": "#F28C28",
                "text": "#FFFFFF",
                "text_scd": "#A0A0A0",
                "btn_bg": "#2C2C2C",
                "btn_hover": "#383838",
                "btn_border": "#404040",
                "entry_bg": "#2C2C2C",
                "logo_light": False
            }
        }
        
        self.current_mode = "Light"
        self.colors = self.palettes[self.current_mode]
        
        self.configure(fg_color=self.colors["bg"])
        
        # Handle window closing event to ensure process termination
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Container (Card Style)
        self.main_container = ctk.CTkFrame(
            self, 
            fg_color=self.colors["card"], 
            corner_radius=20,
            border_width=0
        )
        self.main_container.grid(row=0, column=0, padx=45, pady=40, sticky="nsew")  # Increased padx for scrollbar space
        self.main_container.grid_columnconfigure(0, weight=1)
        # Distribute rows customized
        self.main_container.grid_rowconfigure(0, weight=0)
        self.main_container.grid_rowconfigure(1, weight=0)
        self.main_container.grid_rowconfigure(2, weight=1) # The queue expands
        self.main_container.grid_rowconfigure(3, weight=0)
        self.main_container.grid_rowconfigure(4, weight=0)
        self.main_container.grid_rowconfigure(5, weight=0)
        self.main_container.grid_rowconfigure(6, weight=0)
        self.main_container.grid_rowconfigure(7, weight=0)  # Copyright row

        # --- Header Section (Logo + Title) ---
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, pady=(40, 10), sticky="ew")
        
        # Custom Theme Toggle (Clickable Image)
        try:
            # Get project root directory (parent of src/)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            assets_dir = os.path.join(project_root, "assets")
            # Load toggle assets
            self.img_sun = ctk.CTkImage(Image.open(os.path.join(assets_dir, "toggle_sun.png")), size=(100, 40))
            self.img_moon = ctk.CTkImage(Image.open(os.path.join(assets_dir, "toggle_moon.png")), size=(100, 40))
        except Exception as e:
            print(f"Error loading toggle assets: {e}")
            self.img_sun = None
            self.img_moon = None
            
        self.lbl_toggle = ctk.CTkLabel(self.main_container, text="")
        if self.current_mode == "Light":
            self.lbl_toggle.configure(image=self.img_sun)
        else:
            self.lbl_toggle.configure(image=self.img_moon)
            
        self.lbl_toggle.bind("<Button-1>", lambda e: self.toggle_theme())
        self.lbl_toggle.place(relx=0.95, rely=0.03, anchor="ne")
        # Initialize cursor change on hover
        self.lbl_toggle.bind("<Enter>", lambda e: self.lbl_toggle.configure(cursor="hand2"))
        self.lbl_toggle.bind("<Leave>", lambda e: self.lbl_toggle.configure(cursor="arrow"))

        # Content Frame (Center Aligned)
        self.header_content = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_content.pack(side="top", anchor="center")

        # Load Logo
        try:
            # Get project root directory (parent of src/)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            assets_dir = os.path.join(project_root, "assets")
            # Load the image using PIL
            image_path = os.path.join(assets_dir, "ITG-Logo.png")
            # Resize image to fit nicely, standard usually around 100-150px wide/tall depending on ratio
            pil_image = Image.open(image_path)
            # Maintain aspect ratio - lets say max height 80
            ratio = pil_image.width / pil_image.height
            new_height = 80
            new_width = int(new_height * ratio)
            
            self.logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(new_width, new_height))
            
            self.logo_label = ctk.CTkLabel(self.header_content, text="", image=self.logo_image)
            self.logo_label.pack(side="top", pady=(0, 10))
            
        except Exception as e:
            print(f"Could not load logo: {e}")
            self.logo_label = ctk.CTkLabel(self.header_content, text="ITG", font=("Helvetica", 42, "bold"), text_color=self.colors["accent"])
            self.logo_label.pack(side="top", pady=(0, 10))

        self.label_title = ctk.CTkLabel(
            self.header_content, 
            text="ITG Video Compressor", 
            font=("Roboto", 32, "bold"),  # Larger font
            text_color=self.colors["text"]
        )
        self.label_title.pack(side="top", pady=(0, 5))
        
        self.label_subtitle = ctk.CTkLabel(
            self.header_content, 
            text="Compress videos for the QA Team", 
            font=("Roboto", 15),  # Larger font
            text_color=self.colors["text_scd"]
        )
        self.label_subtitle.pack(side="top")

        # --- Drop Zone / File Selection ---
        self.file_frame = ctk.CTkFrame(
            self.main_container, 
            fg_color="transparent", 
            border_width=0, 
        )
        self.file_frame.grid(row=1, column=0, padx=50, pady=(20, 20), sticky="ew")
        self.file_frame.grid_columnconfigure(0, weight=1)
        self.file_frame.grid_columnconfigure(1, weight=1)

        # Custom File Select Button (Styled like a drop zone)
        self.btn_select = ctk.CTkButton(
            self.file_frame, 
            text="SELECT LOCAL FILE", 
            command=self.select_file, 
            height=50,
            fg_color=self.colors["btn_bg"], 
            border_width=2,
            border_color=self.colors["accent"],
            text_color=self.colors["text"], 
            hover_color=self.colors["btn_hover"], 
            font=("Roboto", 17, "bold"),  # Larger font
            corner_radius=12
        )
        self.btn_select.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="ew")

        # Drive Link Button
        self.btn_drive = ctk.CTkButton(
            self.file_frame, 
            text="IMPORT FROM DRIVE", 
            command=self.import_from_drive, 
            height=50,
            fg_color=self.colors["btn_bg"], 
            border_width=2,
            border_color="#4285F4", 
            text_color=self.colors["text"], 
            hover_color=self.colors["btn_hover"], 
            font=("Roboto", 17, "bold"),  # Larger font
            corner_radius=12
        )
        self.btn_drive.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="ew")
        
        # File Queue Display (Scrollable) - Styled Professional List
        self.queue_frame = ctk.CTkScrollableFrame(
            self.main_container, 
            label_text="Selected Videos Queue",
            label_text_color=self.colors["text"],
            label_font=("Roboto", 15, "bold"),
            height=320,
            fg_color=self.colors["entry_bg"],
            border_width=3,  # Thicker border
            border_color=self.colors["text_scd"],
            corner_radius=10,
            scrollbar_button_color=self.colors["accent"],
            scrollbar_button_hover_color=self.colors["accent_hover"]
        )
        self.queue_frame.grid(row=2, column=0, pady=(20, 20), padx=50, sticky="nsew")
        
        # Configure scrollbar to be narrower and stay inside border
        try:
            self.queue_frame._scrollbar.configure(width=14)
            self.queue_frame._scrollbar.grid_configure(padx=(0, 6), pady=6)
        except:
            pass
        
        # Store queue data
        self.queue_files = [] # List of dicts: {'path': str, 'status': 'pending', 'frame': widget}

        # --- Settings Area ---
        self.settings_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.settings_frame.grid(row=3, column=0, padx=100, pady=(0, 20), sticky="ew")
        self.settings_frame.grid_columnconfigure(0, weight=1) # expand center
        
        self.settings_inner = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.settings_inner.pack(anchor="center")

        self.label_target = ctk.CTkLabel(self.settings_inner, text="Target Size (MB)", text_color=self.colors["text_scd"], font=("Roboto", 14))  # Larger font
        self.label_target.pack(side="left", padx=(0, 10))
        
        self.entry_size = ctk.CTkEntry(
            self.settings_inner, 
            width=80, 
            justify="center",
            fg_color=self.colors["entry_bg"],
            text_color=self.colors["text"],
            border_color=self.colors["text_scd"],
            border_width=2  # Thicker border
        )
        self.entry_size.insert(0, "10")
        self.entry_size.pack(side="left", padx=(0, 20))
        
        # Suffix customization
        self.label_suffix = ctk.CTkLabel(self.settings_inner, text="Suffix", text_color=self.colors["text_scd"], font=("Roboto", 14))  # Larger font
        self.label_suffix.pack(side="left", padx=(0, 10))
        
        self.entry_suffix = ctk.CTkEntry(
            self.settings_inner,
            width=120,
            justify="center",
            fg_color=self.colors["entry_bg"],
            text_color=self.colors["text"],
            border_color=self.colors["text_scd"],
            border_width=2,
            placeholder_text="_compressed",
            font=("Roboto", 13)  # Larger font
        )
        self.entry_suffix.insert(0, "_compressed")
        self.entry_suffix.pack(side="left", padx=(0, 20))
        
        # Speed vs Quality Selection
        self.label_speed = ctk.CTkLabel(self.settings_inner, text="Mode", text_color=self.colors["text_scd"], font=("Roboto", 14))
        self.label_speed.pack(side="left", padx=(0, 10))
        
        self.seg_speed = ctk.CTkSegmentedButton(
            self.settings_inner,
            values=["Fast", "Balanced"],
            width=140,
            fg_color=self.colors["entry_bg"],
            selected_color=self.colors["accent"],
            selected_hover_color=self.colors["accent_hover"],
            unselected_color=self.colors["entry_bg"],
            unselected_hover_color=self.colors["btn_hover"],
            text_color=self.colors["text"],
            font=("Roboto", 13, "bold")
        )
        self.seg_speed.set("Fast") # Default to Fast as requested
        self.seg_speed.pack(side="left", padx=(0, 20))
        
        # Output Folder Selection
        self.btn_output_folder = ctk.CTkButton(
            self.settings_inner,
            text="Output Folder",
            command=self.select_output_folder,
            width=160,
            height=32,
            fg_color=self.colors["accent"],
            text_color="#FFFFFF",
            hover_color=self.colors["accent_hover"],
            font=("Roboto", 13, "bold"),
            corner_radius=8
        )
        self.btn_output_folder.pack(side="left")
        
        # Output folder label - placed below settings in same frame
        self.label_output_folder = ctk.CTkLabel(
            self.settings_frame,
            text="Output: Same as source",
            text_color=self.colors["text_scd"],
            font=("Roboto", 13)  # Larger font
        )
        self.label_output_folder.pack(pady=(5, 0))

        # --- Action Section ---
        self.action_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.action_frame.grid(row=4, column=0, pady=20)
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=0)
        
        # Button container
        btn_container = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        btn_container.grid(row=0, column=0, columnspan=2)
        
        # Single dynamic button (Compress/Abort)
        self.btn_compress = ctk.CTkButton(
            btn_container, 
            text="COMPRESS NOW", 
            command=self.toggle_compression, 
            state="disabled", 
            fg_color=self.colors["accent"], 
            hover_color=self.colors["accent_hover"],
            text_color="#FFFFFF",
            text_color_disabled="#FFFFFF",
            height=55, 
            width=220,
            font=("Roboto", 18, "bold"),
            corner_radius=28
        )
        self.btn_compress.pack(side="left", padx=(0, 10))
        
        # Refresh button
        self.btn_refresh = ctk.CTkButton(
            btn_container,
            text="REFRESH",
            command=self.refresh_app,
            height=55,
            width=150,
            fg_color="#3498db",
            hover_color="#2980b9",
            text_color="#FFFFFF",
            font=("Roboto", 14, "bold"),
            corner_radius=28
        )
        self.btn_refresh.pack(side="left")

        # --- Status & Progress ---
        self.status_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.status_frame.grid(row=5, column=0, padx=50, pady=(0, 10), sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.progressbar = ctk.CTkProgressBar(
            self.status_frame, 
            progress_color=self.colors["accent"],
            height=12
        )
        self.progressbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.progressbar.set(0)
        
        self.label_status = ctk.CTkLabel(
            self.status_frame, 
            text="Ready", 
            text_color=self.colors["text_scd"],
            font=("Roboto", 14)  # Larger font
        )
        self.label_status.grid(row=1, column=0)
        
        # Logs viewer - positioned at bottom, doesn't affect other elements
        self.logs_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.logs_frame.grid(row=6, column=0, padx=50, pady=(0, 10))
        
        # Copyright notice
        self.copyright_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.copyright_frame.grid(row=7, column=0, padx=50, pady=(0, 15))
        
        self.label_copyright = ctk.CTkLabel(
            self.copyright_frame,
            text="© 2025 Eyab Ghifari  |  ITG Software",
            text_color=self.colors["text_scd"],
            font=("Roboto", 10)
        )
        self.label_copyright.pack()
        
        self.btn_toggle_logs = ctk.CTkButton(
            self.logs_frame,
            text="Show Logs",
            command=self.toggle_logs,
            height=32,
            width=140,
            fg_color=self.colors["accent"],
            text_color="#FFFFFF",
            hover_color=self.colors["accent_hover"],
            font=("Roboto", 12, "bold"),
            corner_radius=8,
            border_width=0
        )
        self.btn_toggle_logs.grid(row=0, column=0, pady=(0, 5))
        
        self.logs_visible = False
        # Use standard tkinter Text widget for colored logs (CTkTextbox doesn't support colors)
        import tkinter as tk
        self.logs_text = tk.Text(
            self.logs_frame,
            height=8,  # 8 lines (approximately 120 pixels)
            width=100,
            font=("Consolas", 10),
            bg=self.colors["entry_bg"],
            fg=self.colors["text"],
            relief="solid",
            borderwidth=2,
            wrap="word",
            state="disabled"  # Disable editing, enable programmatic insertion
        )
        
        # Configure color tags for different log levels
        self.logs_text.tag_config("info", foreground="#00CED1")  # Cyan
        self.logs_text.tag_config("success", foreground="#2ecc71")  # Green
        self.logs_text.tag_config("warning", foreground="#f39c12")  # Orange/Yellow
        self.logs_text.tag_config("error", foreground="#e74c3c")  # Red
        self.logs_text.tag_config("timeout", foreground="#9b59b6")  # Purple/Magenta
        self.logs_text.tag_config("separator", foreground="#7f8c8d")  # Gray for separators
        # Hidden by default

        # Variables
        self.queue_files = []
        self.output_folder = None
        self.abort_flag = False
        self.is_compressing = False  # Track compression state
        self.was_aborted = False  # Track if last run was aborted
        self.compression_thread = None  # Store compression thread reference
        self.current_processing_item = None  # Track current item being processed 


    def toggle_theme(self):
        if self.current_mode == "Light":
            self.current_mode = "Dark"
            ctk.set_appearance_mode("Dark")
            if self.img_moon: self.lbl_toggle.configure(image=self.img_moon)
        else:
            self.current_mode = "Light"
            ctk.set_appearance_mode("Light")
            if self.img_sun: self.lbl_toggle.configure(image=self.img_sun)
            
        self.colors = self.palettes[self.current_mode]
        self.update_ui_colors()

    def update_ui_colors(self):
        self.configure(fg_color=self.colors["bg"])
        self.main_container.configure(fg_color=self.colors["card"])
        
        # Text adjustments
        self.label_title.configure(text_color=self.colors["text"])
        self.label_subtitle.configure(text_color=self.colors["text_scd"])
        self.label_target.configure(text_color=self.colors["text_scd"])
        self.label_status.configure(text_color=self.colors["text_scd"])
        self.label_copyright.configure(text_color=self.colors["text_scd"])
        
        # Buttons & Inputs
        self.btn_select.configure(
            fg_color=self.colors["btn_bg"], 
            text_color=self.colors["text"],
            hover_color=self.colors["btn_hover"],
            border_color=self.colors["accent"]
        )
        self.btn_drive.configure(
            fg_color=self.colors["btn_bg"], 
            text_color=self.colors["text"],
            hover_color=self.colors["btn_hover"]
        )
        self.entry_size.configure(
            fg_color=self.colors["entry_bg"],
            text_color=self.colors["text"],
            border_color=self.colors["text_scd"]
        )
        self.entry_suffix.configure(
            fg_color=self.colors["entry_bg"],
            text_color=self.colors["text"],
            border_color=self.colors["text_scd"]
        )
        self.seg_speed.configure(
            fg_color=self.colors["entry_bg"],
            selected_color=self.colors["accent"],
            selected_hover_color=self.colors["accent_hover"],
            unselected_color=self.colors["entry_bg"],
            unselected_hover_color=self.colors["btn_hover"],
            text_color=self.colors["text"]
        )
        self.label_speed.configure(text_color=self.colors["text_scd"])
        
        # Toggle label needs no color update as it is an image, 
        # but we ensure bg matches card just in case of transparency issues
        self.lbl_toggle.configure(bg_color=self.colors["card"])
        
        # Update queue frame colors
        self.queue_frame.configure(
            label_text_color=self.colors["text"],
            fg_color=self.colors["entry_bg"],
            border_color=self.colors["text_scd"]
        )
        
        # Force Compress Button Colors
        self.btn_compress.configure(
             fg_color=self.colors["accent"],
             hover_color=self.colors["accent_hover"],
              text_color="#FFFFFF", # RE-ASSERT WHITE TEXT
              text_color_disabled="#FFFFFF" # FORCE WHITE EVEN WHEN DISABLED
        )
        # Refresh button doesn't need color update (uses fixed blue color)
        self.progressbar.configure(progress_color=self.colors["accent"])
        
        # Update logs text widget colors
        self.logs_text.config(
            bg=self.colors["entry_bg"],
            fg=self.colors["text"]
        )
        
        # Update queue items
        for item in self.queue_files:
            try:
                # Update Frame
                if item.get('frame'):
                    item['frame'].configure(
                        fg_color=self.colors["btn_bg"],
                        border_color=self.colors["accent"]
                    )
                
                # Update Labels
                if item.get('name_label'):
                    item['name_label'].configure(text_color=self.colors["text"])
                
                if item.get('size_label'):
                    item['size_label'].configure(text_color=self.colors["text_scd"])
                    
                if item.get('status_label'):
                    # Only update color if it's "Pending" (others have specific colors like green/red)
                    current_text = item['status_label'].cget("text")
                    if "Pending" in current_text or "Ready" in current_text:
                        item['status_label'].configure(text_color=self.colors["text_scd"])
                        
            except (tkinter.TclError, AttributeError):
                pass  # Widget might be destroyed

    def select_file(self):
        filenames = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv")])
        if filenames:
            self.add_files_to_queue(filenames)

    def add_files_to_queue(self, filenames):
        for f in filenames:
            # Check duplicates
            if any(q['path'] == f for q in self.queue_files):
                continue
                
            # Create Row Frame with clear borders
            row = ctk.CTkFrame(
                self.queue_frame,
                fg_color=self.colors["btn_bg"],
                corner_radius=8,
                border_width=2,  # Thicker border
                border_color=self.colors["accent"],
                height=60
            )
            row.pack(fill="x", pady=5, padx=(8, 20))  # Extra right padding to avoid scrollbar overlap
            row.pack_propagate(False)
            
            # Video icon
            lbl_icon = ctk.CTkLabel(
                row,
                text="🎬",
                font=("Roboto", 18),
                width=40,
                fg_color="transparent"
            )
            lbl_icon.pack(side="left", padx=(10, 5), pady=5)
            
            # File info container
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            # Filename
            name = os.path.basename(f)
            if len(name) > 40:
                name = name[:37] + "..."
            
            lbl_name = ctk.CTkLabel(
                info_frame,
                text=name,
                anchor="w",
                font=("Roboto", 14, "bold"),  # Larger font
                text_color=self.colors["text"],
                fg_color="transparent"
            )
            lbl_name.pack(anchor="w", fill="x")
            
            # File size
            try:
                size_mb = os.path.getsize(f) / (1024 * 1024)
                size_text = f"{size_mb:.2f} MB"
            except:
                size_text = "Unknown size"
            
            lbl_size = ctk.CTkLabel(
                info_frame,
                text=size_text,
                anchor="w",
                font=("Roboto", 11),  # Larger font
                text_color=self.colors["text_scd"],
                fg_color="transparent"
            )
            lbl_size.pack(anchor="w", fill="x")
            
            # Status Label
            lbl_status = ctk.CTkLabel(
                row,
                text="⏳ Pending",
                font=("Roboto", 12),  # Larger font
                text_color=self.colors["text_scd"],
                width=90,
                fg_color="transparent"
            )
            lbl_status.pack(side="left", padx=5, pady=5)
            
            # Remove Button
            btn_rem = ctk.CTkButton(
                row,
                text="✕",
                width=40,  # Bigger button
                height=40,  # Bigger button
                fg_color="transparent",
                text_color="#e74c3c",
                hover_color="#fab1a0",
                font=("Roboto", 18, "bold"),  # Larger font
                corner_radius=6,
                border_width=1,
                border_color="#e74c3c",
                command=lambda p=f, r=row: self.remove_file(p, r)
            )
            btn_rem.pack(side="right", padx=10, pady=5)
            
            self.queue_files.append({
                'path': f,
                'frame': row,
                'status_label': lbl_status,
                'name_label': lbl_name,
                'size_label': lbl_size
            })
            
        # Enable compress button if files exist
        if self.queue_files:
            self.btn_compress.configure(state="normal")
            self.label_status.configure(text=f"Queue: {len(self.queue_files)} videos ready.")
            self.btn_select.configure(fg_color=self.colors["card"], text="ADD MORE FILES")

    def remove_file(self, path, frame):
        frame.destroy()
        self.queue_files = [x for x in self.queue_files if x['path'] != path]
        if not self.queue_files:
            self.btn_compress.configure(state="disabled")
            self.label_status.configure(text="Queue empty.")
            self.btn_select.configure(fg_color=self.colors["btn_bg"], text="SELECT LOCAL FILE")

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder = folder
            folder_name = os.path.basename(folder) if folder else "..."
            if len(folder_name) > 30:
                folder_name = folder_name[:27] + "..."
            self.label_output_folder.configure(text=f"Output: {folder_name}")
        else:
            self.output_folder = None
            self.label_output_folder.configure(text="Output: Same as source")

    def toggle_compression(self):
        """Single button that toggles between start and abort"""
        if self.is_compressing:
            # Currently compressing - abort immediately
            self.abort_compression()
            # Wait a moment then show START OVER
            self.after(500, lambda: self.compression_finished(0, len(self.queue_files), 0))
        elif self.was_aborted:
            # Was aborted - reset and start over from beginning
            self.log_message("Starting over from beginning...", "info")
            self.was_aborted = False  # Clear flag first
            self.abort_flag = False  # Clear abort flag
            self.is_compressing = False  # Clear compressing flag
            self.current_processing_item = None  # Clear current item
            self.reset_queue()
            # Small delay to ensure UI updates, then start
            self.after(200, self.start_compression)
        else:
            # Not compressing - start
            self.start_compression()
    
    def start_compression(self):
        if not self.queue_files:
             return
             
        # Get settings
        try:
            target_size = float(self.entry_size.get())
        except ValueError:
            self.label_status.configure(text="Invalid size.")
            return

        self.abort_flag = False
        self.is_compressing = True
        self.was_aborted = False  # Reset abort flag
        
        # Change button to abort mode
        self.btn_compress.configure(
            text="⏹ ABORT",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.toggle_compression
        )
        
        self.progressbar.set(0)
        # Get preset based on selection
        speed_mode = self.seg_speed.get()
        ffmpeg_preset = "faster" if speed_mode == "Fast" else "medium"
        
        self.log_message(f"Starting batch compression of {len(self.queue_files)} videos (Mode: {speed_mode})...", "info")
        
        # Start Thread (store reference for abort)
        self.compression_thread = threading.Thread(target=self.run_batch_compression, args=(target_size, ffmpeg_preset), daemon=True)
        self.compression_thread.start()

    def run_batch_compression(self, target_size, preset="faster"):
        compressor = VideoCompressor(target_size_mb=target_size)
        total_files = len(self.queue_files)
        success_count = 0
        error_count = 0
        
        for index, item in enumerate(self.queue_files):
            # Check abort flag - immediate exit
            if self.abort_flag:
                self.log_message("Compression aborted by user - stopping immediately.", "warning")
                self.main_container.after(0, lambda: self.label_status.configure(text="Aborted by user."))
                # Mark current item as pending if it was processing
                if self.current_processing_item:
                    self.update_queue_item_status(self.current_processing_item, "Pending", "text")
                break
                
            # Check if item still exists and is valid (might have been removed during refresh)
            if item not in self.queue_files:
                continue  # Item was removed during processing, skip it
            
            # Verify item widgets still exist
            try:
                if not item.get('status_label') or not item.get('frame'):
                    continue  # Widgets destroyed, skip
                # Check if already done
                if item['status_label'].cget("text") == "✅ Done":
                    success_count += 1
                    continue
            except (tkinter.TclError, AttributeError, KeyError):
                continue  # Widget destroyed or invalid, skip this item
            
            file_path = item['path']
            
            # Set current processing item
            self.current_processing_item = item
            
            # Update status UI for this item
            self.update_queue_item_status(item, "Processing...", "orange")
            filename = os.path.basename(file_path)
            self.main_container.after(0, lambda f=filename, i=index, t=total_files: 
                self.label_status.configure(text=f"Compressing {i+1}/{t}: {f}..."))
            self.log_message(f"[{index+1}/{total_files}] Processing: {filename}", "info")
            
            # Output path
            suffix = self.entry_suffix.get() or "_compressed"
            if self.output_folder:
                basename = os.path.basename(file_path)
                name, ext = os.path.splitext(basename)
                output_path = os.path.join(self.output_folder, f"{name}{suffix}{ext}")
            else:
                dirname = os.path.dirname(file_path)
                basename = os.path.basename(file_path)
                name, ext = os.path.splitext(basename)
                output_path = os.path.join(dirname, f"{name}{suffix}{ext}")
            
            # Process with timeout and error handling
            result = False
            try:
                # Use threading with timeout for each video
                result_queue = []
                exception_queue = []
                
                # First, get video duration to calculate expected processing time
                duration = None
                try:
                    # Quick duration check using ffprobe
                    result = subprocess.run(
                        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                         '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        duration = float(result.stdout.strip())
                except:
                    pass
                
                # Calculate dynamic timeout based on duration
                if duration and duration > 0:
                    # Expected time = duration * 2 + 60s overhead
                    expected_time = (duration * 2.0) + 60
                    # Add 2 minute buffer
                    dynamic_timeout = expected_time + 120
                    # Cap at 15 minutes absolute max
                    dynamic_timeout = min(dynamic_timeout, 900)
                else:
                    # Fallback to 5 minutes if duration unknown
                    dynamic_timeout = 300
                
                def compress_with_timeout():
                    try:
                        # Pass the calculated max_processing_time to compressor
                        res = compressor.compress_video(
                            file_path, 
                            output_path, 
                            max_processing_time=dynamic_timeout,
                            preset=preset
                        )
                        result_queue.append(res)
                    except Exception as e:
                        exception_queue.append(e)
                
                # Start compression in a thread with dynamic timeout
                compress_thread = threading.Thread(target=compress_with_timeout, daemon=True)
                compress_thread.start()
                
                # Wait with dynamic timeout based on video duration
                compress_thread.join(timeout=dynamic_timeout)
                
                # Check if thread is still alive (timed out)
                if compress_thread.is_alive():
                    timeout_minutes = dynamic_timeout / 60
                    self.log_message(f"⏱️ Timeout: {filename} exceeded calculated processing time ({timeout_minutes:.1f} min). Skipping...", "timeout")
                    self.update_queue_item_status(item, "Timeout", "red")
                    error_count += 1
                    # Try to continue - thread will die as daemon
                elif exception_queue:
                    # Exception occurred
                    error = exception_queue[0]
                    self.update_queue_item_status(item, "Error", "red")
                    error_count += 1
                    self.log_message(f"❌ Error: {filename} - {str(error)}", "error")
                    print(f"Error processing {filename}: {error}")
                elif result_queue:
                    # Got result
                    result = result_queue[0]
                    if result:
                        self.update_queue_item_status(item, "Done", "green")
                        success_count += 1
                        self.log_message(f"✅ Success: {filename}", "success")
                    else:
                        self.update_queue_item_status(item, "Error", "red")
                        error_count += 1
                        self.log_message(f"❌ Failed: {filename} (compression returned False)", "error")
                else:
                    # No result (shouldn't happen)
                    self.update_queue_item_status(item, "Error", "red")
                    error_count += 1
                    self.log_message(f"❌ Failed: {filename} (unknown error)", "error")
                    
            except Exception as e:
                # Handle errors gracefully - skip and continue
                self.update_queue_item_status(item, "Error", "red")
                error_count += 1
                self.log_message(f"❌ Error: {filename} - {str(e)}", "error")
                print(f"Error processing {filename}: {e}")
            
            # Clear current processing item
            self.current_processing_item = None
            
            # Check abort flag again after processing
            if self.abort_flag:
                self.log_message("Compression aborted - stopping batch.", "warning")
                break
            
            # Update overall progress
            progress = (index + 1) / total_files
            self.main_container.after(0, lambda p=progress: self.progressbar.set(p))
        
        # Clear current processing item
        self.current_processing_item = None
        
        # Check if aborted to determine final state
        if self.abort_flag:
            self.was_aborted = True
            self.main_container.after(0, lambda s=success_count, t=total_files, e=error_count: 
                self.compression_finished(s, t, e))
        else:
            self.main_container.after(0, lambda s=success_count, t=total_files, e=error_count: 
                self.compression_finished(s, t, e))

    def update_queue_item_status(self, item, status_text, color_key="text"):
        # Helper to update label in thread-safe way (using after)
        # Check if item still exists in queue (might have been removed/refreshed)
        if item not in self.queue_files:
            return  # Item was removed, skip update
        
        # Verify the frame and status_label still exist
        try:
            # Check if frame still exists
            if not item.get('frame') or not item.get('status_label'):
                return
            # Try to access the widget to see if it's still valid
            item['status_label'].winfo_exists()
        except (tkinter.TclError, AttributeError, KeyError):
            return  # Widget was destroyed, skip update
        
        # Add emoji indicators
        status_icons = {
            "Processing...": "⚙️",
            "Done": "✅",
            "Error": "❌",
            "Pending": "⏳",
            "Timeout": "⏱️",
        }
        
        icon = status_icons.get(status_text, "")
        display_text = f"{icon} {status_text}" if icon else status_text
        
        color = self.colors["text"]
        if color_key == "orange": color = self.colors["accent"]
        if color_key == "green": color = "#2ecc71"
        if color_key == "red": color = "#e74c3c"
        
        # Safe update with error handling
        def safe_update():
            try:
                # Double-check item still exists
                if item in self.queue_files and item.get('status_label'):
                    item['status_label'].configure(text=display_text, text_color=color)
            except (tkinter.TclError, AttributeError, KeyError):
                pass  # Widget destroyed, ignore
        
        self.main_container.after(0, safe_update)

    def compression_finished(self, success_count, total, error_count=0):
        self.is_compressing = False
        
        # Check if was aborted
        if self.was_aborted:
            # Show START OVER button
            self.btn_compress.configure(
                text="START OVER",
                fg_color="#3498db",  # Blue color
                hover_color="#2980b9",
                state="normal",
                command=self.toggle_compression
            )
            self.log_message("Ready to start over from beginning.", "info")
        else:
            # Reset button to compress mode
            self.btn_compress.configure(
                text="COMPRESS NOW",
                fg_color=self.colors["accent"],
                hover_color=self.colors["accent_hover"],
                state="normal",
                command=self.toggle_compression
            )
        
        # Build status message
        if error_count > 0:
            status_msg = f"Batch Finished: {success_count} succeeded, {error_count} failed out of {total} videos."
            self.log_message(f"Batch complete: {success_count}/{total} succeeded, {error_count} errors", "warning" if error_count > 0 else "success")
        else:
            status_msg = f"Batch Finished: {success_count}/{total} videos compressed successfully!"
            self.log_message(f"Batch complete: All {success_count} videos compressed successfully!", "success")
            
        self.label_status.configure(text=status_msg)
        if success_count == total:
            self.progressbar.configure(progress_color="#2ecc71")
    
    def abort_compression(self):
        """Immediately abort compression and reset"""
        self.abort_flag = True
        self.is_compressing = False
        
        # Immediately show START OVER button
        self.btn_compress.configure(
            text="START OVER",
            fg_color="#3498db",
            hover_color="#2980b9",
            state="normal",
            command=self.toggle_compression  # Make sure command is set
        )
        self.log_message("Abort requested - stopping immediately...", "warning")
        
        # Reset current processing item if any
        if self.current_processing_item:
            self.update_queue_item_status(self.current_processing_item, "Pending", "text")
            self.current_processing_item = None
        
    def toggle_logs(self):
        if self.logs_visible:
            self.logs_text.grid_forget()
            self.btn_toggle_logs.configure(text="Show Logs")
            self.logs_visible = False
        else:
            self.logs_text.grid(row=1, column=0, pady=(5, 0))
            self.btn_toggle_logs.configure(text="Hide Logs")
            self.logs_visible = True
            
    def log_message(self, message, level="info"):
        """
        Add message to logs with colors and formatting
        
        Args:
            message: The log message
            level: Log level - "info", "success", "warning", "error", "timeout"
        """
        timestamp = datetime.datetime.now().strftime("%I:%M:%S %p")
        
        # Create separator lines
        single_separator = "─" * 80
        double_separator = "═" * 80
        
        # Format log entry with timestamp and level indicator
        level_icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "timeout": "⏱️",
        }
        icon = level_icons.get(level, "ℹ️")
        
        # Use double separator for important messages (success, error, timeout)
        if level in ["success", "error", "timeout"]:
            separator = double_separator
        else:
            separator = single_separator
        
        # Enable text widget for editing
        self.logs_text.config(state="normal")
        
        # Insert separator before log entry (except for first entry)
        current_text = self.logs_text.get("1.0", "end-1c")
        if current_text.strip():
            self.logs_text.insert("end", f"{separator}\n", "separator")
        
        # Format log entry with colored text
        log_entry = f"{icon} [{timestamp}] {message}\n"
        
        # Insert log entry with color tag
        self.logs_text.insert("end", log_entry, level)
        
        # Disable text widget to prevent editing
        self.logs_text.config(state="disabled")
        
        # Also print to console with colors
        self._print_colored_console(message, level, timestamp, separator)
        
        self.logs_text.see("end")  # Auto-scroll to bottom
    
    def _print_colored_console(self, message, level, timestamp, separator):
        """Print colored message to console with enhanced formatting"""
        try:
            from colorama import Fore, Style, init
            init(autoreset=True)
            
            color_map = {
                "info": Fore.CYAN,
                "success": Fore.GREEN,
                "warning": Fore.YELLOW,
                "error": Fore.RED,
                "timeout": Fore.MAGENTA,
            }
            
            color = color_map.get(level, Fore.WHITE)
            print(f"\n{color}{separator}{Style.RESET_ALL}")
            print(f"{color}[{timestamp}] {message}{Style.RESET_ALL}")
        except ImportError:
            # Fallback if colorama not available
            print(f"\n{separator}")
            print(f"[{timestamp}] {message}")
    
    def reset_queue(self):
        """Reset all videos in queue to pending state"""
        self.was_aborted = False
        self.abort_flag = False
        self.is_compressing = False
        self.progressbar.set(0)
        self.progressbar.configure(progress_color=self.colors["accent"])
        
        for item in self.queue_files:
            self.update_queue_item_status(item, "Pending", "text")
        
        if self.queue_files:
            self.btn_compress.configure(
                text="COMPRESS NOW",
                fg_color=self.colors["accent"],
                hover_color=self.colors["accent_hover"],
                state="normal",
                command=self.toggle_compression
            )
            self.label_status.configure(text=f"Queue reset: {len(self.queue_files)} videos ready.")
        else:
            self.btn_compress.configure(state="disabled")
            self.label_status.configure(text="Queue empty.")
        
        self.log_message("Queue reset - all videos set to pending.", "info")
    
    def refresh_app(self):
        """Refresh/reset the entire application state"""
        self.log_message("Refreshing application...", "info")
        
        # Stop any ongoing compression
        if self.is_compressing:
            self.abort_flag = True
            self.is_compressing = False
        
        # Clear all flags
        self.was_aborted = False
        self.abort_flag = False
        self.current_processing_item = None  # Clear current item reference to prevent updates to destroyed widgets
        
        # Clear queue - destroy frames safely
        queue_copy = list(self.queue_files)  # Make a copy to avoid modification during iteration
        for item in queue_copy:
            try:
                if item.get('frame'):
                    item['frame'].destroy()
            except (tkinter.TclError, AttributeError, KeyError):
                pass  # Already destroyed or invalid
        self.queue_files = []  # Clear the list after destroying all items
        
        # Reset UI elements
        self.progressbar.set(0)
        self.progressbar.configure(progress_color=self.colors["accent"], mode="determinate")
        self.label_status.configure(text="Ready")
        
        # Reset buttons
        self.btn_compress.configure(
            text="COMPRESS NOW",
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            state="disabled",
            command=self.toggle_compression
        )
        self.btn_select.configure(
            fg_color=self.colors["btn_bg"],
            text="SELECT LOCAL FILE"
        )
        
        # Reset settings
        self.output_folder = None
        self.label_output_folder.configure(text="Output: Same as source")
        self.entry_size.delete(0, "end")
        self.entry_size.insert(0, "10")
        self.entry_suffix.delete(0, "end")
        self.entry_suffix.insert(0, "_compressed")
        
        # Clear logs
        self.logs_text.config(state="normal")
        self.logs_text.delete("1.0", "end")
        self.logs_text.config(state="disabled")
        self.log_message("Application refreshed - ready for new session.", "success")
        
        print("Application refreshed successfully.")

    # Placeholder to keep old method signature if needed, or remove it.
    # run_compression was the old method, replaced by run_batch_compression.


    def import_from_drive(self):
        if gdown is None:
            self.label_status.configure(text="Error: gdown module misplaced.", text_color="red")
            return
            
        dialog = ctk.CTkInputDialog(text="Paste Google Drive Link:", title="Import from Drive")
        url = dialog.get_input()
        if url:
            self.refresh_app()  # Refresh state before new import
            self.label_status.configure(text="Downloading from Drive...", text_color=self.colors["accent"])
            self.progressbar.configure(mode="indeterminate")
            self.progressbar.start()
            self.btn_select.configure(state="disabled")
            self.btn_drive.configure(state="disabled")
            
            threading.Thread(target=self.download_drive_video, args=(url,), daemon=True).start()

    def download_drive_video(self, url):
        try:
            # Determine base path for downloads
            if getattr(sys, 'frozen', False):
                # If running as executable, use the folder containing the exe
                base_path = os.path.dirname(sys.executable)
            else:
                # If running as script, use the project root (parent of src)
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            download_dir = os.path.join(base_path, "downloads")
            
            # Create downloads folder if not exists
            # Clean up previous downloads (delete entire folder content)
            try:
                if os.path.exists(download_dir):
                    shutil.rmtree(download_dir)
                os.makedirs(download_dir, exist_ok=True)
            except Exception as e:
                print(f"Warning cleaning downloads: {e}")
                # Ensure directory exists even if cleanup failed
                os.makedirs(download_dir, exist_ok=True)
            
            downloaded_files = []
            
            # Store original CWD and switch to download_dir
            # This ensures gdown saves files exactly where we want them
            original_cwd = os.getcwd()
            try:
                os.chdir(download_dir)
                
                if "/folders/" in url or "drive.google.com/drive/u/0/folders" in url:
                    self.after(0, lambda: self.label_status.configure(text="Detected Drive Folder. Downloading batch..."))
                    # Download Folder - use "." since we are already in the dir
                    # Use quiet=True to prevent attempting to write to stdout in EXE
                    results = gdown.download_folder(url, output=".", quiet=True, use_cookies=False)
                    if results:
                        # results contains relative paths (filenames)
                        downloaded_files = [os.path.abspath(f) for f in results]
                else:
                    # Single File
                    print(f"Downloading file from {url}...")
                    # Download to current directory (download_dir)
                    # Use quiet=True to prevent attempting to write to stdout in EXE
                    filename = gdown.download(url, quiet=True, fuzzy=True, output=None)
                    
                    if filename:
                        # Get absolute path
                        filepath = os.path.abspath(filename)
                        downloaded_files.append(filepath)
                        
            finally:
                # Always restore original CWD
                os.chdir(original_cwd)

            if downloaded_files:
                self.after(0, lambda: self.drive_download_finished(downloaded_files))
            else:
                self.after(0, lambda: self.drive_download_failed("No files downloaded. Check link permissions."))
                
        except Exception as e:
            print(f"Download Error: {e}")
            self.after(0, lambda: self.drive_download_failed(str(e)))

    def drive_download_finished(self, filepaths):
        self.progressbar.stop()
        self.progressbar.configure(mode="determinate")
        self.progressbar.set(0)
        self.btn_select.configure(state="normal")
        self.btn_drive.configure(state="normal")
        
        valid_files = []
        if isinstance(filepaths, list):
            for f in filepaths:
                if f and os.path.exists(f):
                    valid_files.append(f)
        elif isinstance(filepaths, str) and os.path.exists(filepaths):
             valid_files.append(filepaths)
             
        if valid_files:
            self.add_files_to_queue(valid_files)
            self.label_status.configure(text=f"Download Complete! {len(valid_files)} files added.")
            self.btn_drive.configure(fg_color=self.colors["btn_bg"], text="IMPORT FROM DRIVE")
        else:
            self.label_status.configure(text="Download failed or no files found.", text_color="red")
            self.btn_drive.configure(fg_color=self.colors["card"], text="CHANGE LINK")

    def drive_download_failed(self, error_msg):
        self.progressbar.stop()
        self.progressbar.configure(mode="determinate")
        self.progressbar.set(0)
        self.btn_select.configure(state="normal")
        self.btn_drive.configure(state="normal")
        print(f"Drive Error: {error_msg}")
        self.label_status.configure(text="Download Failed. Check link/perms.", text_color="red")

    def _set_window_icon(self):
        """Set the window icon for both title bar and Windows taskbar"""
        try:
            # Get project root directory (parent of src/)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            icon_ico = os.path.join(project_root, "assets", "ITG-Small-Logo.ico")
            
            # Set the AppUserModelID for Windows taskbar
            # This ensures the icon shows up correctly in the taskbar and groups windows properly
            myappid = 'ITG.VideoCompressor.App.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            
            # Set the window icon
            if os.path.exists(icon_ico):
                self.iconbitmap(icon_ico)
                
            
            # Set the window icon
            if os.path.exists(icon_ico):
                self.iconbitmap(icon_ico)
                
        except Exception:
            # User requested no logs for icon handling
            pass

    def on_closing(self):
        """Handle window closing to ensure everything shuts down"""
        try:
            # Signal any running threads to stop
            self.abort_flag = True
            
            # Destroy the window
            self.destroy()
            
            # Force kill the process and all threads
            # os._exit(0) is required because sys.exit() only raises an exception
            # and might be caught or ignored by background threads.
            os._exit(0)
        except Exception as e:
            print(f"Error on close: {e}")
            os._exit(1)

if __name__ == "__main__":
    app = App()
    app.mainloop()
