import customtkinter as ctk
import os
import sys
import threading
import subprocess
import ctypes
import tkinter as tk

# Import components
from ui.styles import ThemeManager
from utils.assets import AssetManager
from ui.widgets.header import Header
from ui.widgets.file_list import FileList
from ui.widgets.settings import SettingsPanel
from ui.widgets.action_bar import ActionBar
from ui.widgets.status_panel import StatusPanel
from utils.drive_importer import DriveImporter
from compressor import VideoCompressor

# Fix for PyInstaller noconsole mode
class NullWriter:
    def write(self, text): pass
    def flush(self): pass

if sys.stdout is None: sys.stdout = NullWriter()
if sys.stderr is None: sys.stderr = NullWriter()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ITG Video Compressor")
        self.geometry("1200x950")
        self.resizable(True, True)
        
        # Managers
        self.theme_manager = ThemeManager()
        self.asset_manager = AssetManager()
        
        self.configure(fg_color=self.theme_manager.colors["bg"])
        
        # Setup Window Icon
        self.icon_image = None
        self.after(100, self._set_window_icon)
        
        # State
        self.abort_flag = False
        self.is_compressing = False
        self.was_aborted = False
        self.current_processing_item = None
        self.compression_thread = None

        # Protocol
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Container
        self.main_container = ctk.CTkFrame(
            self, 
            fg_color=self.theme_manager.colors["card"], 
            corner_radius=20,
            border_width=0
        )
        self.main_container.grid(row=0, column=0, padx=45, pady=40, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Grid rows for components
        self.main_container.grid_rowconfigure(0, weight=0) # Header
        self.main_container.grid_rowconfigure(1, weight=1) # FileList (expands)
        self.main_container.grid_rowconfigure(2, weight=0) # Settings
        self.main_container.grid_rowconfigure(3, weight=0) # Actions
        self.main_container.grid_rowconfigure(4, weight=0) # Status

        # --- Components ---
        
        # 1. Header
        self.header = Header(
            self.main_container, 
            self.theme_manager, 
            self.asset_manager, 
            self.toggle_theme
        )
        self.header.grid(row=0, column=0, pady=(40, 10), sticky="ew")

        # 2. File List
        self.file_list = FileList(
            self.main_container,
            self.theme_manager,
            on_queue_change=self.on_queue_changed,
            on_drive_import=self.import_from_drive
        )
        self.file_list.grid(row=1, column=0, pady=(10, 10), sticky="nsew")

        # 3. Settings
        self.settings_panel = SettingsPanel(
            self.main_container,
            self.theme_manager
        )
        self.settings_panel.grid(row=2, column=0, padx=100, pady=(0, 20), sticky="ew")

        # 4. Action Bar
        self.action_bar = ActionBar(
            self.main_container,
            self.theme_manager,
            on_compress=self.toggle_compression,
            on_refresh=self.refresh_app
        )
        self.action_bar.grid(row=3, column=0, pady=20)

        # 5. Status Panel
        self.status_panel = StatusPanel(
            self.main_container,
            self.theme_manager
        )
        self.status_panel.grid(row=4, column=0, padx=50, pady=(0, 10), sticky="ew")

    # --- Actions ---

    def toggle_theme(self):
        self.theme_manager.toggle_theme()
        # Propagate color updates to all components
        self.configure(fg_color=self.theme_manager.colors["bg"])
        self.main_container.configure(fg_color=self.theme_manager.colors["card"])
        self.header.update_colors()
        self.file_list.update_colors()
        self.settings_panel.update_colors()
        self.action_bar.update_colors()
        self.status_panel.update_colors()

    def on_queue_changed(self, queue_files):
        count = len(queue_files)
        if count > 0:
            self.action_bar.btn_compress.configure(state="normal")
            self.status_panel.label_status.configure(text=f"Queue: {count} videos ready.")
        else:
            self.action_bar.btn_compress.configure(state="disabled")
            self.status_panel.label_status.configure(text="Queue empty.")

    def update_queue_item_status(self, item, status_text, color_key="text"):
        if item not in self.file_list.queue_files:
            return 
        
        status_icons = {"Processing...": "⚙️", "Done": "✅", "Error": "❌", "Pending": "⏳", "Timeout": "⏱️"}
        icon = status_icons.get(status_text, "")
        display_text = f"{icon} {status_text}" if icon else status_text
        
        color = self.theme_manager.colors["text"]
        if color_key == "orange": color = self.theme_manager.colors["accent"]
        if color_key == "green": color = "#2ecc71"
        if color_key == "red": color = "#e74c3c"
        
        def safe_update():
            try:
                if item in self.file_list.queue_files and item.get('status_label'):
                     item['status_label'].configure(text=display_text, text_color=color)
            except: pass
        
        self.after(0, safe_update)

    def import_from_drive(self):
        drive_importer = DriveImporter(
            status_callback=lambda msg: self.after(0, lambda: self.status_panel.label_status.configure(text=msg)),
            finish_callback=self._drive_import_finished,
            fail_callback=self._drive_import_failed
        )
        
        if not drive_importer.check_requirements():
            self.status_panel.label_status.configure(text="Error: gdown module misplaced.", text_color="red")
            return

        dialog = ctk.CTkInputDialog(text="Paste Google Drive Link:", title="Import from Drive")
        url = dialog.get_input()
        if url:
            self.refresh_app()
            self.status_panel.label_status.configure(text="Downloading from Drive...", text_color=self.theme_manager.colors["accent"])
            self.status_panel.progressbar.configure(mode="indeterminate")
            self.status_panel.progressbar.start()
            self.file_list.btn_select.configure(state="disabled")
            self.file_list.btn_drive.configure(state="disabled")
            
            drive_importer.start_download(url)

    def _drive_import_finished(self, files):
        self.after(0, lambda: self._handle_drive_success(files))

    def _handle_drive_success(self, files):
        self.status_panel.progressbar.stop()
        self.status_panel.progressbar.configure(mode="determinate")
        self.status_panel.progressbar.set(0)
        
        self.file_list.add_files(files)
        self.status_panel.label_status.configure(text=f"Download Complete! {len(files)} files added.")
        self.file_list.btn_drive.configure(text="IMPORT FROM DRIVE") # Reset text if changed
        
    def _drive_import_failed(self, error):
         self.after(0, lambda: self._handle_drive_fail(error))
    
    def _handle_drive_fail(self, error):
        self.status_panel.progressbar.stop()
        self.status_panel.progressbar.configure(mode="determinate")
        self.status_panel.progressbar.set(0)
        self.file_list.btn_select.configure(state="normal")
        self.file_list.btn_drive.configure(state="normal")
        self.status_panel.label_status.configure(text="Download Failed. Check link/perms.", text_color="red")
        self.file_list.btn_drive.configure(fg_color=self.theme_manager.colors["card"], text="CHANGE LINK")
        self.status_panel.log_message(f"Drive Error: {error}", "error")

    # --- Compression Logic ---
    
    def toggle_compression(self):
        if self.is_compressing:
            self.abort_compression()
            self.after(500, lambda: self.compression_finished(0, len(self.file_list.queue_files), 0))
        elif self.was_aborted:
            self.status_panel.log_message("Starting over from beginning...", "info")
            self.reset_queue()
            self.after(200, self.start_compression)
        else:
            self.start_compression()
            
    def start_compression(self):
        queue_files = self.file_list.queue_files
        if not queue_files: return
        
        settings = self.settings_panel.get_settings()
        try:
            target_size = float(settings['target_size'])
        except ValueError:
            self.status_panel.label_status.configure(text="Invalid size.")
            return

        self.abort_flag = False
        self.is_compressing = True
        self.was_aborted = False
        
        self.action_bar.btn_compress.configure(
            text="⏹ ABORT", fg_color="#e74c3c", hover_color="#c0392b"
        )
        
        self.status_panel.progressbar.set(0)
        
        speed_mode = settings['mode']
        ffmpeg_preset = "faster" if speed_mode == "Fast" else "medium"
        
        self.status_panel.log_message(f"Starting batch compression of {len(queue_files)} videos (Mode: {speed_mode})...", "info")
        
        self.compression_thread = threading.Thread(
            target=self.run_batch_compression, 
            args=(target_size, ffmpeg_preset, settings['suffix'], settings['output_folder']), 
            daemon=True
        )
        self.compression_thread.start()

    def run_batch_compression(self, target_size, preset, suffix, output_folder_override):
        compressor = VideoCompressor(target_size_mb=target_size)
        queue_files = self.file_list.queue_files 
        total_files = len(queue_files)
        success_count = 0
        error_count = 0
        
        for index, item in enumerate(queue_files):
            if self.abort_flag:
                self.status_panel.log_message("Compression aborted by user.", "warning")
                if self.current_processing_item:
                    self.update_queue_item_status(self.current_processing_item, "Pending", "text")
                break
                
            if item not in queue_files: continue
            
            try:
                if item.get('status_label'):
                    if "Done" in item['status_label'].cget("text"):
                        success_count += 1
                        continue
            except: continue
            
            file_path = item['path']
            self.current_processing_item = item
            self.update_queue_item_status(item, "Processing...", "orange")
            filename = os.path.basename(file_path)
            
            self.after(0, lambda f=filename, i=index, t=total_files: 
                self.status_panel.label_status.configure(text=f"Compressing {i+1}/{t}: {f}..."))
            self.status_panel.log_message(f"Processing: {filename}", "info")
            
            if output_folder_override:
                basename = os.path.basename(file_path)
                name, ext = os.path.splitext(basename)
                output_path = os.path.join(output_folder_override, f"{name}{suffix}{ext}")
            else:
                dirname = os.path.dirname(file_path)
                basename = os.path.basename(file_path)
                name, ext = os.path.splitext(basename)
                output_path = os.path.join(dirname, f"{name}{suffix}{ext}")
                
            try:
                res = compressor.compress_video(file_path, output_path, preset=preset)
                
                if res:
                    self.update_queue_item_status(item, "Done", "green")
                    success_count += 1
                    self.status_panel.log_message(f"✅ Success: {filename}", "success")
                else:
                     self.update_queue_item_status(item, "Error", "red")
                     error_count += 1
                     self.status_panel.log_message(f"❌ Failed: {filename}", "error")
                     
            except Exception as e:
                self.update_queue_item_status(item, "Error", "red")
                error_count += 1
                self.status_panel.log_message(f"❌ Error: {filename} - {e}", "error")
                
            self.current_processing_item = None
            progress = (index + 1) / total_files
            self.after(0, lambda p=progress: self.status_panel.progressbar.set(p))
            
        self.current_processing_item = None
        if self.abort_flag: self.was_aborted = True
        
        self.after(0, lambda: self.compression_finished(success_count, total_files, error_count))

    def abort_compression(self):
        self.abort_flag = True
        self.is_compressing = False
        self.status_panel.log_message("Abort requested...", "warning")
        
    def compression_finished(self, success_count, total, error_count):
        self.is_compressing = False
        
        if self.was_aborted:
            self.action_bar.btn_compress.configure(text="START OVER", fg_color="#3498db", hover_color="#2980b9", state="normal")
            self.status_panel.log_message("Ready to start over.", "info")
        else:
            self.action_bar.btn_compress.configure(
                text="COMPRESS NOW", 
                fg_color=self.theme_manager.colors["accent"], 
                hover_color=self.theme_manager.colors["accent_hover"],
                state="normal"
            )
            
        status_msg = f"Finished: {success_count}/{total} succeeded."
        if error_count > 0: status_msg += f" {error_count} errors."
        
        self.status_panel.label_status.configure(text=status_msg)
        if success_count == total and total > 0:
            self.status_panel.progressbar.configure(progress_color="#2ecc71")
            self.status_panel.log_message("Batch completed successfully!", "success")

    def reset_queue(self):
        self.was_aborted = False
        self.abort_flag = False
        self.is_compressing = False
        self.status_panel.progressbar.set(0)
        self.status_panel.progressbar.configure(progress_color=self.theme_manager.colors["accent"])
        
        for item in self.file_list.queue_files:
            self.update_queue_item_status(item, "Pending", "text")
            
        self.action_bar.btn_compress.configure(
            text="COMPRESS NOW", 
            fg_color=self.theme_manager.colors["accent"], 
            state="normal"
        )
        self.status_panel.label_status.configure(text=f"Queue reset: {len(self.file_list.queue_files)} ready.")
        self.status_panel.log_message("Queue reset.", "info")

    def refresh_app(self):
        self.status_panel.log_message("Refreshing...", "info")
        if self.is_compressing:
            self.abort_flag = True
            self.is_compressing = False
            
        self.was_aborted = False
        self.current_processing_item = None
        
        self.file_list.clear_queue()
        self.settings_panel.reset()
        
        self.status_panel.progressbar.set(0)
        self.status_panel.progressbar.configure(progress_color=self.theme_manager.colors["accent"], mode="determinate")
        self.status_panel.label_status.configure(text="Ready")
        self.action_bar.btn_compress.configure(state="disabled", text="COMPRESS NOW", fg_color=self.theme_manager.colors["accent"])
        
        self.status_panel.logs_text.config(state="normal")
        self.status_panel.logs_text.delete("1.0", "end")
        self.status_panel.logs_text.config(state="disabled")
        self.status_panel.log_message("Application refreshed.", "success")

    def _set_window_icon(self):
        try:
            icon_ico = self.asset_manager.get_icon_path()
            myappid = 'ITG.VideoCompressor.App.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            if os.path.exists(icon_ico):
                self.iconbitmap(icon_ico)
        except: pass

    def on_closing(self):
        self.abort_flag = True
        self.destroy()
        os._exit(0)

if __name__ == "__main__":
    app = App()
    app.mainloop()
