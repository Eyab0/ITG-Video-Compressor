import customtkinter as ctk

class Header(ctk.CTkFrame):
    def __init__(self, master, theme_manager, asset_manager, toggle_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme_manager = theme_manager
        self.asset_manager = asset_manager
        self.toggle_callback = toggle_callback
        
        self.grid_columnconfigure(0, weight=1)
        
        # --- Theme Toggle ---
        self.img_sun, self.img_moon = self.asset_manager.load_toggle_icons()
        
        self.lbl_toggle = ctk.CTkLabel(master, text="") # Placed on master to use absolute positioning or relative to master if needed
        # Wait, original app placed it on main_container. Let's place it inside this frame if possible, 
        # or we follow the original design which used place(relx=0.95). 
        # Ideally, it should be part of the header frame.
        # But for exact reproduction of UI, let's keep it here but we might need to use place() on THIS frame.
        
        self.lbl_toggle = ctk.CTkLabel(self, text="")
        self.update_toggle_icon()
            
        self.lbl_toggle.bind("<Button-1>", lambda e: self.toggle_callback())
        self.lbl_toggle.place(relx=0.95, rely=0.03, anchor="ne") # This might need adjustment relative to this frame
        
        self.lbl_toggle.bind("<Enter>", lambda e: self.lbl_toggle.configure(cursor="hand2"))
        self.lbl_toggle.bind("<Leave>", lambda e: self.lbl_toggle.configure(cursor="arrow"))

        # --- Logo & Title ---
        self.header_content = ctk.CTkFrame(self, fg_color="transparent")
        self.header_content.pack(side="top", anchor="center")
        
        # Logo
        self.logo_image = self.asset_manager.load_logo()
        if self.logo_image:
            self.logo_label = ctk.CTkLabel(self.header_content, text="", image=self.logo_image)
            self.logo_label.pack(side="top", pady=(0, 10))
        else:
            self.logo_label = ctk.CTkLabel(self.header_content, text="ITG", font=("Helvetica", 42, "bold"), text_color=self.theme_manager.colors["accent"])
            self.logo_label.pack(side="top", pady=(0, 10))

        # Title
        self.label_title = ctk.CTkLabel(
            self.header_content, 
            text="ITG Video Compressor", 
            font=("Roboto", 32, "bold"),
            text_color=self.theme_manager.colors["text"]
        )
        self.label_title.pack(side="top", pady=(0, 5))
        
        # Subtitle
        self.label_subtitle = ctk.CTkLabel(
            self.header_content, 
            text="Compress videos for the QA Team", 
            font=("Roboto", 15),
            text_color=self.theme_manager.colors["text_scd"]
        )
        self.label_subtitle.pack(side="top")

    def update_toggle_icon(self):
        if self.theme_manager.current_mode == "Light":
            if self.img_sun: self.lbl_toggle.configure(image=self.img_sun)
        else:
            if self.img_moon: self.lbl_toggle.configure(image=self.img_moon)
            
    def update_colors(self):
        self.label_title.configure(text_color=self.theme_manager.colors["text"])
        self.label_subtitle.configure(text_color=self.theme_manager.colors["text_scd"])
        self.update_toggle_icon()
        self.lbl_toggle.configure(bg_color=self.theme_manager.colors["card"])
