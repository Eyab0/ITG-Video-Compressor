import customtkinter as ctk

class ThemeManager:
    """Manages application theme and color palettes."""
    
    def __init__(self):
        self.current_mode = "Light"
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
        self.colors = self.palettes[self.current_mode]

    def set_theme(self, mode):
        if mode in self.palettes:
            self.current_mode = mode
            self.colors = self.palettes[mode]
            ctk.set_appearance_mode(mode)
            
    def toggle_theme(self):
        new_mode = "Dark" if self.current_mode == "Light" else "Light"
        self.set_theme(new_mode)
        return new_mode
