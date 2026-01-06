import customtkinter as ctk
import tkinter as tk
import datetime

class StatusPanel(ctk.CTkFrame):
    def __init__(self, master, theme_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme_manager = theme_manager
        
        self.grid_columnconfigure(0, weight=1)
        
        # --- Progress Bar ---
        self.progressbar = ctk.CTkProgressBar(
            self, 
            progress_color=self.theme_manager.colors["accent"],
            height=12
        )
        self.progressbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.progressbar.set(0)
        
        # --- Status Label ---
        self.label_status = ctk.CTkLabel(
            self, 
            text="Ready", 
            text_color=self.theme_manager.colors["text_scd"],
            font=("Roboto", 14)
        )
        self.label_status.grid(row=1, column=0)
        
        # --- Logs Area ---
        self.logs_frame = ctk.CTkFrame(master, fg_color="transparent") # Placed on master (main container) usually at bottom
        # Wait, in original it's separate row. 
        # Let's keep logs inside THIS panel to be self-contained? 
        # Original: progress(row5), logs(row6), copyright(row7).
        # If StatusPanel is row 5, maybe logs should be inside it?
        # Let's put logs inside StatusPanel for better encapsulation.
        
        self.logs_container = ctk.CTkFrame(self, fg_color="transparent")
        self.logs_container.grid(row=2, column=0, pady=(10, 0))
        
        self.btn_toggle_logs = ctk.CTkButton(
            self.logs_container,
            text="Show Logs",
            command=self.toggle_logs,
            height=32,
            width=140,
            fg_color=self.theme_manager.colors["accent"],
            text_color="#FFFFFF",
            hover_color=self.theme_manager.colors["accent_hover"],
            font=("Roboto", 12, "bold"),
            corner_radius=8,
            border_width=0
        )
        self.btn_toggle_logs.grid(row=0, column=0, pady=(0, 5))
        
        self.logs_visible = False
        self.logs_text = tk.Text(
            self.logs_container,
            height=8,
            width=100,
            font=("Consolas", 10),
            bg=self.theme_manager.colors["entry_bg"],
            fg=self.theme_manager.colors["text"],
            relief="solid",
            borderwidth=2,
            wrap="word",
            state="disabled"
        )
        
        # Configure tags
        self.logs_text.tag_config("info", foreground="#00CED1")
        self.logs_text.tag_config("success", foreground="#2ecc71")
        self.logs_text.tag_config("warning", foreground="#f39c12")
        self.logs_text.tag_config("error", foreground="#e74c3c")
        self.logs_text.tag_config("timeout", foreground="#9b59b6")
        self.logs_text.tag_config("separator", foreground="#7f8c8d")

        # Copyright (Included here for convenience or separate?)
        # Let's include it at bottom of status panel
        self.label_copyright = ctk.CTkLabel(
            self,
            text="© 2025 Eyab Ghifari  |  ITG Software",
            text_color=self.theme_manager.colors["text_scd"],
            font=("Roboto", 10)
        )
        self.label_copyright.grid(row=3, column=0, pady=(15, 0))

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
        timestamp = datetime.datetime.now().strftime("%I:%M:%S %p")
        single_separator = "─" * 80
        double_separator = "═" * 80
        
        level_icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌", "timeout": "⏱️"}
        icon = level_icons.get(level, "ℹ️")
        
        separator = double_separator if level in ["success", "error", "timeout"] else single_separator
        
        self.logs_text.config(state="normal")
        
        current_text = self.logs_text.get("1.0", "end-1c")
        if current_text.strip():
            self.logs_text.insert("end", f"{separator}\n", "separator")
        
        log_entry = f"{icon} [{timestamp}] {message}\n"
        self.logs_text.insert("end", log_entry, level)
        self.logs_text.config(state="disabled")
        self.logs_text.see("end")
        
        # Also print to console
        self._print_colored_console(message, level, timestamp, separator)

    def _print_colored_console(self, message, level, timestamp, separator):
        try:
            from colorama import Fore, Style, init
            init(autoreset=True)
            color_map = {
                "info": Fore.CYAN, "success": Fore.GREEN, "warning": Fore.YELLOW,
                "error": Fore.RED, "timeout": Fore.MAGENTA
            }
            color = color_map.get(level, Fore.WHITE)
            print(f"\n{color}{separator}{Style.RESET_ALL}")
            print(f"{color}[{timestamp}] {message}{Style.RESET_ALL}")
        except ImportError:
            print(f"\n{separator}")
            print(f"[{timestamp}] {message}")

    def update_colors(self):
        self.label_status.configure(text_color=self.theme_manager.colors["text_scd"])
        self.label_copyright.configure(text_color=self.theme_manager.colors["text_scd"])
        self.progressbar.configure(progress_color=self.theme_manager.colors["accent"])
        self.logs_text.config(bg=self.theme_manager.colors["entry_bg"], fg=self.theme_manager.colors["text"])
