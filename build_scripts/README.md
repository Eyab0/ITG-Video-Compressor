# Build Scripts

This folder contains all scripts and configuration files for building the executable.

## Files

- **`build_exe.py`** - Main Python build script
- **`build.bat`** - Windows batch file for building
- **`build_spec.spec`** - PyInstaller spec file (advanced configuration)

## Usage

### From Project Root

Run from the project root directory:
```bash
build.bat
```

Or:
```bash
python build_scripts\build_exe.py
```

### From This Folder

If running from this folder, use:
```bash
cd ..
python build_scripts\build_exe.py
```

## Output

The executable will be created in:
- `dist/ITG Video Compressor.exe` (relative to project root)

Build artifacts will be in:
- `build/` (temporary build files)

