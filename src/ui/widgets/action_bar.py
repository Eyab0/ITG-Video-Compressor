import customtkinter as ctk

class ActionBar(ctk.CTkFrame):
    def __init__(self, master, theme_manager, on_compress, on_refresh, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme_manager = theme_manager
        self.on_compress = on_compress
        self.on_refresh = on_refresh
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        
        # Button container
        self.btn_container = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_container.grid(row=0, column=0, columnspan=2)
        
        self.btn_compress = ctk.CTkButton(
            self.btn_container, 
            text="COMPRESS NOW", 
            command=self.on_compress, 
            state="disabled", 
            fg_color=self.theme_manager.colors["accent"], 
            hover_color=self.theme_manager.colors["accent_hover"],
            text_color="#FFFFFF",
            text_color_disabled="#FFFFFF",
            height=55, 
            width=220,
            font=("Roboto", 18, "bold"),
            corner_radius=28
        )
        self.btn_compress.pack(side="left", padx=(0, 10))
        
        self.btn_refresh = ctk.CTkButton(
            self.btn_container,
            text="REFRESH",
            command=self.on_refresh,
            height=55,
            width=150,
            fg_color="#3498db",
            hover_color="#2980b9",
            text_color="#FFFFFF",
            font=("Roboto", 14, "bold"),
            corner_radius=28
        )
        self.btn_refresh.pack(side="left")

    def update_colors(self):
        # Specific overrides for compress button if not aborted/running
        current_text = self.btn_compress.cget("text")
        if current_text == "COMPRESS NOW":
            self.btn_compress.configure(
                 fg_color=self.theme_manager.colors["accent"],
                 hover_color=self.theme_manager.colors["accent_hover"],
                  text_color="#FFFFFF"
            )
        # REFRESH button uses fixed colors, no update needed
