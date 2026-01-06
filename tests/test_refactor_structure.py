import pytest
import sys
import os
from unittest.mock import MagicMock

# Define proper Mock classes to avoid MagicMock inheritance issues
class MockCTkBase:
    def __init__(self, *args, **kwargs): pass
    def configure(self, **kwargs): pass
    def geometry(self, *args, **kwargs): pass
    def resizable(self, *args, **kwargs): pass
    def after(self, *args, **kwargs): pass
    def protocol(self, *args, **kwargs): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def iconbitmap(self, *args, **kwargs): pass
    def destroy(self, *args, **kwargs): pass
    def mainloop(self, *args, **kwargs): pass
    def title(self, *args, **kwargs): pass
    
    # Widget methods
    def grid(self, **kwargs): pass
    def pack(self, **kwargs): pass
    def place(self, **kwargs): pass
    def bind(self, *args, **kwargs): pass

class MockCTk(MockCTkBase):
    pass

class MockCTkFrame(MockCTkBase):
    pass
    
class MockCTkScrollableFrame(MockCTkBase):
    def __init__(self, *args, **kwargs):
        self._scrollbar = MagicMock()
        super().__init__(*args, **kwargs)

class MockCTkButton(MockCTkBase):
    def cget(self, key): return "mock"

class MockCTkLabel(MockCTkBase):
    def cget(self, key): return "mock"

# Setup mocks
mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
mock_ctk.CTkFrame = MockCTkFrame
mock_ctk.CTkScrollableFrame = MockCTkScrollableFrame
mock_ctk.CTkButton = MockCTkButton
mock_ctk.CTkLabel = MockCTkLabel
# Mock other widgets generic
# ...

sys.modules['customtkinter'] = mock_ctk
sys.modules['tkinter'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['gdown'] = MagicMock()

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import App

class TestRefactorStructure:
    """Verify the application structure after refactoring"""
    
    def test_app_structure_and_integration(self):
        """Test that App initializes correctly and components are integrated"""
        app = App()
        
        # Verify Managers
        assert hasattr(app, 'theme_manager'), "App should have theme_manager"
        assert hasattr(app, 'asset_manager'), "App should have asset_manager"
        
        # Verify UI Components (check type or existence)
        assert hasattr(app, 'header'), "App should have header"
        assert app.header is not None
        
        assert hasattr(app, 'file_list'), "App should have file_list"
        assert hasattr(app, 'settings_panel'), "App should have settings_panel"
        assert hasattr(app, 'action_bar'), "App should have action_bar"
        assert hasattr(app, 'status_panel'), "App should have status_panel"
        
        # Verify Integration (Managers passed down)
        # Since we use custom Mock classes, attributes are set normally
        assert app.header.theme_manager == app.theme_manager
        assert app.file_list.theme_manager == app.theme_manager
        assert app.settings_panel.theme_manager == app.theme_manager
        
        # Verify methods exist
        assert hasattr(app, 'toggle_theme')
        assert hasattr(app, 'import_from_drive')
