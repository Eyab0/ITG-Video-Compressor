import os
import sys
from PIL import Image
import customtkinter as ctk

class AssetManager:
    """Manages loading and accessing application assets."""
    
    def __init__(self):
        self.project_root = self._get_project_root()
        self.assets_dir = os.path.join(self.project_root, "assets")
        self.img_sun = None
        self.img_moon = None
        self.logo_image_object = None # The ctk image
        
    def _get_project_root(self):
        # Handle both development and PyInstaller bundled executable
        # The logic below assumes src/utils/assets.py is 2 levels deep from project root
        # But we need to be careful with PyInstaller.
        # In original app.py: os.path.dirname(os.path.dirname(os.path.abspath(__file__))) was root from src/app.py
        # Here: src/utils/assets.py -> parent is utils -> parent is src -> parent is root. So 3 levels up.
        
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            # If standard PyInstaller structure, root is sys._MEIPASS
            base_path = sys._MEIPASS
            return base_path
        else:
            # Running as script
            # current file: src/utils/assets.py
            # 1 up: src/utils
            # 2 up: src
            # 3 up: root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

    def load_toggle_icons(self):
        try:
            sun_path = os.path.join(self.assets_dir, "toggle_sun.png")
            moon_path = os.path.join(self.assets_dir, "toggle_moon.png")
            
            if os.path.exists(sun_path):
                self.img_sun = ctk.CTkImage(Image.open(sun_path), size=(100, 40))
                
            if os.path.exists(moon_path):
                self.img_moon = ctk.CTkImage(Image.open(moon_path), size=(100, 40))
                
        except Exception as e:
            print(f"Error loading toggle assets: {e}")
            
        return self.img_sun, self.img_moon

    def load_logo(self):
        try:
            image_path = os.path.join(self.assets_dir, "ITG-Logo.png")
            if os.path.exists(image_path):
                pil_image = Image.open(image_path)
                # maintain aspect ratio
                ratio = pil_image.width / pil_image.height
                new_height = 80
                new_width = int(new_height * ratio)
                
                self.logo_image_object = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(new_width, new_height))
                return self.logo_image_object
        except Exception as e:
            print(f"Could not load logo: {e}")
        return None

    def get_icon_path(self):
        return os.path.join(self.assets_dir, "ITG-Small-Logo.ico")
