import os
import customtkinter as ctk
from tkinter import filedialog
import shutil
import threading
try:
    import gdown
except ImportError:
    gdown = None

class FileList(ctk.CTkFrame):
    def __init__(self, master, theme_manager, on_queue_change, on_drive_import, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme_manager = theme_manager
        self.on_queue_change = on_queue_change # Callback when queue changes
        self.on_drive_import = on_drive_import # Callback for drive import (starts thread in App)
        
        self.queue_files = [] # List of dicts
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- File Selection Buttons ---
        self.file_frame = ctk.CTkFrame(self, fg_color="transparent", border_width=0)
        self.file_frame.grid(row=0, column=0, columnspan=2, padx=50, pady=(0, 20), sticky="ew")
        self.file_frame.grid_columnconfigure(0, weight=1)
        self.file_frame.grid_columnconfigure(1, weight=1)

        self.btn_select = ctk.CTkButton(
            self.file_frame, 
            text="SELECT LOCAL FILE", 
            command=self.select_file, 
            height=50,
            fg_color=self.theme_manager.colors["btn_bg"], 
            border_width=2,
            border_color=self.theme_manager.colors["accent"],
            text_color=self.theme_manager.colors["text"], 
            hover_color=self.theme_manager.colors["btn_hover"], 
            font=("Roboto", 17, "bold"),
            corner_radius=12
        )
        self.btn_select.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="ew")

        self.btn_drive = ctk.CTkButton(
            self.file_frame, 
            text="IMPORT FROM DRIVE", 
            command=self.request_drive_import, 
            height=50,
            fg_color=self.theme_manager.colors["btn_bg"], 
            border_width=2,
            border_color="#4285F4", 
            text_color=self.theme_manager.colors["text"], 
            hover_color=self.theme_manager.colors["btn_hover"], 
            font=("Roboto", 17, "bold"),
            corner_radius=12
        )
        self.btn_drive.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="ew")
        
        # --- Queue List ---
        self.queue_frame = ctk.CTkScrollableFrame(
            self, 
            label_text="Selected Videos Queue",
            label_text_color=self.theme_manager.colors["text"],
            label_font=("Roboto", 15, "bold"),
            height=320,
            fg_color=self.theme_manager.colors["entry_bg"],
            border_width=3,
            border_color=self.theme_manager.colors["text_scd"],
            corner_radius=10,
            scrollbar_button_color=self.theme_manager.colors["accent"],
            scrollbar_button_hover_color=self.theme_manager.colors["accent_hover"]
        )
        self.queue_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20), padx=50, sticky="nsew")
        
        # Configure scrollbar
        try:
            self.queue_frame._scrollbar.configure(width=14)
            self.queue_frame._scrollbar.grid_configure(padx=(0, 6), pady=6)
        except:
            pass
            
    def select_file(self):
        filenames = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv")])
        if filenames:
            self.add_files(filenames)

    def add_files(self, filenames):
        for f in filenames:
            # Check duplicates
            if any(q['path'] == f for q in self.queue_files):
                continue
                
            self._create_queue_item(f)
            
        self.on_queue_change(self.queue_files)
        self.update_buttons_state()

    def _create_queue_item(self, f):
        row = ctk.CTkFrame(
            self.queue_frame,
            fg_color=self.theme_manager.colors["btn_bg"],
            corner_radius=8,
            border_width=2,
            border_color=self.theme_manager.colors["accent"],
            height=60
        )
        row.pack(fill="x", pady=5, padx=(8, 20))
        row.pack_propagate(False)
        
        # Icon
        ctk.CTkLabel(row, text="🎬", font=("Roboto", 18), width=40, fg_color="transparent").pack(side="left", padx=(10, 5), pady=5)
        
        # Info
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        name = os.path.basename(f)
        if len(name) > 40: name = name[:37] + "..."
        
        lbl_name = ctk.CTkLabel(info_frame, text=name, anchor="w", font=("Roboto", 14, "bold"), text_color=self.theme_manager.colors["text"])
        lbl_name.pack(anchor="w", fill="x")
        
        try:
            size_mb = os.path.getsize(f) / (1024 * 1024)
            size_text = f"{size_mb:.2f} MB"
        except:
            size_text = "Unknown size"
            
        lbl_size = ctk.CTkLabel(info_frame, text=size_text, anchor="w", font=("Roboto", 11), text_color=self.theme_manager.colors["text_scd"])
        lbl_size.pack(anchor="w", fill="x")
        
        # Status
        lbl_status = ctk.CTkLabel(row, text="⏳ Pending", font=("Roboto", 12), text_color=self.theme_manager.colors["text_scd"], width=90)
        lbl_status.pack(side="left", padx=5, pady=5)
        
        # Remove
        ctk.CTkButton(
            row, text="✕", width=40, height=40, fg_color="transparent", text_color="#e74c3c", hover_color="#fab1a0",
            font=("Roboto", 18, "bold"), corner_radius=6, border_width=1, border_color="#e74c3c",
            command=lambda p=f, r=row: self.remove_file(p, r)
        ).pack(side="right", padx=10, pady=5)
        
        self.queue_files.append({
            'path': f,
            'frame': row,
            'status_label': lbl_status,
            'name_label': lbl_name,
            'size_label': lbl_size
        })

    def remove_file(self, path, frame):
        frame.destroy()
        self.queue_files = [x for x in self.queue_files if x['path'] != path]
        self.on_queue_change(self.queue_files)
        self.update_buttons_state()

    def clear_queue(self):
        # Destroy frames safely
        queue_copy = list(self.queue_files)
        for item in queue_copy:
            try:
                if item.get('frame'):
                    item['frame'].destroy()
            except:
                pass
        self.queue_files = []
        self.on_queue_change(self.queue_files)
        self.update_buttons_state()

    def update_buttons_state(self):
        # Could expose method to enable/disable buttons from outside
        if not self.queue_files:
            self.btn_select.configure(fg_color=self.theme_manager.colors["btn_bg"], text="SELECT LOCAL FILE")
        else:
            self.btn_select.configure(fg_color=self.theme_manager.colors["card"], text="ADD MORE FILES")

    def request_drive_import(self):
        if self.on_drive_import:
            self.on_drive_import()
            
    def update_colors(self):
        self.btn_select.configure(
            fg_color=self.theme_manager.colors["btn_bg"], 
            text_color=self.theme_manager.colors["text"],
            hover_color=self.theme_manager.colors["btn_hover"],
            border_color=self.theme_manager.colors["accent"]
        )
        self.btn_drive.configure(
            fg_color=self.theme_manager.colors["btn_bg"], 
            text_color=self.theme_manager.colors["text"],
            hover_color=self.theme_manager.colors["btn_hover"]
        )
        self.queue_frame.configure(
            label_text_color=self.theme_manager.colors["text"],
            fg_color=self.theme_manager.colors["entry_bg"],
            border_color=self.theme_manager.colors["text_scd"]
        )
        # Update items
        for item in self.queue_files:
            try:
                item['frame'].configure(fg_color=self.theme_manager.colors["btn_bg"], border_color=self.theme_manager.colors["accent"])
                item['name_label'].configure(text_color=self.theme_manager.colors["text"])
                item['size_label'].configure(text_color=self.theme_manager.colors["text_scd"])
            except: pass
        
        self.update_buttons_state()
