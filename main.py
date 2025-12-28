#!/usr/bin/env python
"""
ITG Video Compressor - Main Entry Point
"""

import sys
import os

# Handle both development and PyInstaller bundled executable
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
    # In PyInstaller, src folder should be at the root of _MEIPASS
    src_path = os.path.join(base_path, 'src')
    # Also check if src is directly in base_path
    if not os.path.exists(src_path):
        src_path = base_path
else:
    # Running as script
    base_path = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(base_path, 'src')

# Add src to path
if src_path not in sys.path:
    sys.path.insert(0, src_path)
# Also add base_path
if base_path not in sys.path:
    sys.path.insert(0, base_path)

# Import after path is set
from app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()

