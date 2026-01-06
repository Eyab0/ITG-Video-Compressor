# Project Structure Overview

This document provides a clear overview of the ITG Video Compressor project structure.

## 📂 Directory Tree

```
vid-comp/
│
├── 📄 main.py                    # Application entry point
├── 📄 build.bat                  # Quick build script (Windows)
├── 📄 requirements.txt           # Python dependencies
├── 📄 README.md                  # Main project documentation
├── 📄 LICENSE                    # License file
├── 📄 .gitignore                 # Git ignore rules
│
├── 📁 src/                       # Source code package
│   ├── __init__.py
│   ├── app.py                    # Main application GUI (Assembly)
│   ├── compressor.py             # Video compression logic
│   ├── ui/                       # UI Components
│   │   ├── __init__.py
│   │   ├── styles.py             # Theme/Colors
│   │   └── widgets/              # Reusable widgets
│   │       ├── __init__.py
│   │       ├── action_bar.py
│   │       ├── file_list.py
│   │       ├── header.py
│   │       ├── settings.py
│   │       └── status_panel.py
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── assets.py             # Asset management
│       └── drive_importer.py     # Google Drive logic
│
├── 📁 tests/                     # Test suite (56 tests)
│   ├── __init__.py
│   ├── test_compressor.py        # Unit tests (23 tests)
│   ├── test_app.py               # App logic tests (20 tests)
│   └── test_integration.py       # Integration tests (13 tests)
│
├── 📁 assets/                    # Application assets
│   ├── ITG-Logo.png
│   ├── toggle_sun.png
│   └── toggle_moon.png
│
├── 📁 build_scripts/             # Build and packaging
│   ├── README.md
│   ├── build_exe.py              # Main Python build script
│   ├── build.bat                 # Windows batch build script
│   └── build_spec.spec           # PyInstaller spec file
│
├── 📁 docs/                      # Documentation
│   ├── README.md
│   ├── build_instructions.md     # Detailed build guide
│   ├── DISTRIBUTION_README.md    # User instructions
│   └── QUICK_START_BUILD.md      # Quick build guide
│
├── 📁 build/                     # Build artifacts (gitignored)
└── 📁 dist/                      # Distribution folder (gitignored)
    └── ITG_Video_Compressor.exe
```

## 📋 File Categories

### Core Application Files
- `main.py` - Entry point that launches the application
- `src/app.py` - Main GUI application
- `src/compressor.py` - Video compression logic

### Configuration Files
- `requirements.txt` - Python package dependencies
- `.gitignore` - Git ignore rules
- `LICENSE` - License information

### Build & Distribution
- `build.bat` - Quick build script (run from root)
- `build_scripts/` - All build-related scripts and configs
- `build/` - Temporary build files (auto-generated, gitignored)
- `dist/` - Final executable output (auto-generated, gitignored)

### Documentation
- `README.md` - Main project documentation
- `docs/` - Additional documentation files

### Testing
- `tests/` - Complete test suite with 56 tests

### Assets
- `assets/` - Images and UI resources

## 🎯 Quick Reference

### Running the Application
```bash
python main.py
```

### Running Tests
```bash
pytest tests/ -v
```

### Building Executable
```bash
build.bat
# or
python build_scripts\build_exe.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## 📝 Notes

- **Build artifacts** (`build/`, `dist/`) are gitignored
- **Documentation** is organized in `docs/` folder
- **Build scripts** are organized in `build_scripts/` folder
- **Source code** is in `src/` package
- **Tests** are in `tests/` package
- **Assets** are in `assets/` folder

This structure follows Python best practices and keeps the project organized and maintainable.

