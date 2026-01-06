import customtkinter as ctk
from tkinter import filedialog
import os

class SettingsPanel(ctk.CTkFrame):
    def __init__(self, master, theme_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme_manager = theme_manager
        self.output_folder = None
        
        self.grid_columnconfigure(0, weight=1)
        
        self.inner = ctk.CTkFrame(self, fg_color="transparent")
        self.inner.pack(anchor="center")

        # Target Size
        self.label_target = ctk.CTkLabel(self.inner, text="Target Size (MB)", text_color=self.theme_manager.colors["text_scd"], font=("Roboto", 14))
        self.label_target.pack(side="left", padx=(0, 10))
        
        self.entry_size = ctk.CTkEntry(
            self.inner, width=80, justify="center", fg_color=self.theme_manager.colors["entry_bg"],
            text_color=self.theme_manager.colors["text"], border_color=self.theme_manager.colors["text_scd"], border_width=2
        )
        self.entry_size.insert(0, "10")
        self.entry_size.pack(side="left", padx=(0, 20))
        
        # Suffix
        self.label_suffix = ctk.CTkLabel(self.inner, text="Suffix", text_color=self.theme_manager.colors["text_scd"], font=("Roboto", 14))
        self.label_suffix.pack(side="left", padx=(0, 10))
        
        self.entry_suffix = ctk.CTkEntry(
            self.inner, width=120, justify="center", fg_color=self.theme_manager.colors["entry_bg"],
            text_color=self.theme_manager.colors["text"], border_color=self.theme_manager.colors["text_scd"], border_width=2,
            placeholder_text="_compressed", font=("Roboto", 13)
        )
        self.entry_suffix.insert(0, "_compressed")
        self.entry_suffix.pack(side="left", padx=(0, 20))
        
        # Mode
        self.label_speed = ctk.CTkLabel(self.inner, text="Mode", text_color=self.theme_manager.colors["text_scd"], font=("Roboto", 14))
        self.label_speed.pack(side="left", padx=(0, 10))
        
        self.seg_speed = ctk.CTkSegmentedButton(
            self.inner, values=["Fast", "Balanced"], width=140, fg_color=self.theme_manager.colors["entry_bg"],
            selected_color=self.theme_manager.colors["accent"], selected_hover_color=self.theme_manager.colors["accent_hover"],
            unselected_color=self.theme_manager.colors["entry_bg"], unselected_hover_color=self.theme_manager.colors["btn_hover"],
            text_color=self.theme_manager.colors["text"], font=("Roboto", 13, "bold")
        )
        self.seg_speed.set("Fast")
        self.seg_speed.pack(side="left", padx=(0, 20))
        
        # Output Folder
        self.btn_output_folder = ctk.CTkButton(
            self.inner, text="Output Folder", command=self.select_output_folder, width=160, height=32,
            fg_color=self.theme_manager.colors["accent"], text_color="#FFFFFF", hover_color=self.theme_manager.colors["accent_hover"],
            font=("Roboto", 13, "bold"), corner_radius=8
        )
        self.btn_output_folder.pack(side="left")
        
        self.label_output_folder = ctk.CTkLabel(
            self, text="Output: Same as source", text_color=self.theme_manager.colors["text_scd"], font=("Roboto", 13)
        )
        self.label_output_folder.pack(pady=(5, 0))

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder = folder
            folder_name = os.path.basename(folder) if folder else "..."
            if len(folder_name) > 30: folder_name = folder_name[:27] + "..."
            self.label_output_folder.configure(text=f"Output: {folder_name}")
        else:
            self.output_folder = None
            self.label_output_folder.configure(text="Output: Same as source")

    def get_settings(self):
        return {
            'target_size': self.entry_size.get(),
            'suffix': self.entry_suffix.get(),
            'mode': self.seg_speed.get(),
            'output_folder': self.output_folder
        }

    def reset(self):
        self.output_folder = None
        self.label_output_folder.configure(text="Output: Same as source")
        self.entry_size.delete(0, "end")
        self.entry_size.insert(0, "10")
        self.entry_suffix.delete(0, "end")
        self.entry_suffix.insert(0, "_compressed")

    def update_colors(self):
        self.label_target.configure(text_color=self.theme_manager.colors["text_scd"])
        self.entry_size.configure(
            fg_color=self.theme_manager.colors["entry_bg"],
            text_color=self.theme_manager.colors["text"],
            border_color=self.theme_manager.colors["text_scd"]
        )
        self.label_suffix.configure(text_color=self.theme_manager.colors["text_scd"])
        self.entry_suffix.configure(
            fg_color=self.theme_manager.colors["entry_bg"],
            text_color=self.theme_manager.colors["text"],
            border_color=self.theme_manager.colors["text_scd"]
        )
        self.label_speed.configure(text_color=self.theme_manager.colors["text_scd"])
        self.seg_speed.configure(
            fg_color=self.theme_manager.colors["entry_bg"],
            selected_color=self.theme_manager.colors["accent"],
            selected_hover_color=self.theme_manager.colors["accent_hover"],
            unselected_color=self.theme_manager.colors["entry_bg"],
            unselected_hover_color=self.theme_manager.colors["btn_hover"],
            text_color=self.theme_manager.colors["text"]
        )
        self.btn_output_folder.configure(
            fg_color=self.theme_manager.colors["accent"],
            hover_color=self.theme_manager.colors["accent_hover"]
        )
        self.label_output_folder.configure(text_color=self.theme_manager.colors["text_scd"])
