# Building the Executable

## Quick Start

1. **Install PyInstaller** (if not already installed):
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**:
   ```bash
   py build_exe.py
   ```
   
   Or manually:
   ```bash
   pyinstaller --name=ITG_Video_Compressor --onefile --windowed --add-data="assets;assets" main.py
   ```

3. **Find your executable**:
   - Location: `dist/ITG_Video_Compressor.exe`
   - This is a standalone file that can be distributed

## Important Notes

### FFmpeg Dependency
⚠️ **IMPORTANT**: The executable will NOT include FFmpeg. Users must have FFmpeg installed on their system.

**For distribution, you have two options:**

1. **Option A: Include FFmpeg with the executable**
   - Download FFmpeg static build
   - Include it in a folder with the executable
   - Update the app to look for FFmpeg in the same folder

2. **Option B: Provide installation instructions**
   - Tell users to install FFmpeg separately
   - Provide a link to FFmpeg download page

### File Size
- The executable will be large (100-200MB) because it includes:
  - Python interpreter
  - All Python dependencies
  - CustomTkinter
  - MoviePy
  - All required libraries

### Testing
Before distributing:
1. Test the executable on a clean Windows machine (without Python installed)
2. Verify FFmpeg works
3. Test video compression
4. Test all features

## Distribution Checklist

- [ ] Build executable using `build_exe.py`
- [ ] Test executable on clean machine
- [ ] Create FFmpeg installation guide or bundle FFmpeg
- [ ] Create user instructions
- [ ] Test all features
- [ ] Package everything needed (executable + FFmpeg if bundled)

## Alternative: Create Installer

You can use tools like:
- **Inno Setup** (free) - Create Windows installer
- **NSIS** (free) - Create Windows installer
- **Advanced Installer** (paid) - Professional installer

These can bundle the executable + FFmpeg + create a proper installer.

