# Quick Start: Building the Executable

## Simple 3-Step Process

### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

### Step 2: Build the Executable

**Option A: Use the batch file (Easiest)**
```bash
build.bat
```

**Option B: Use the Python script**
```bash
py build_exe.py
```

**Option C: Manual command**
```bash
pyinstaller --name=ITG_Video_Compressor --onefile --windowed --add-data="assets;assets" main.py
```

### Step 3: Find Your Executable

After building (takes 2-5 minutes), your executable will be in:
```
dist/ITG_Video_Compressor.exe
```

## What You Get

- **Single .exe file** (~100-200MB)
- **No Python required** for end users
- **All dependencies included**
- **Portable** - can run from anywhere

## Important: FFmpeg

⚠️ **The executable does NOT include FFmpeg.**

Users must install FFmpeg separately:
- Download: https://ffmpeg.org/download.html
- Add to system PATH
- See `DISTRIBUTION_README.md` for user instructions

## Distribution

To distribute to users:
1. Give them `ITG_Video_Compressor.exe`
2. Give them `DISTRIBUTION_README.md` (instructions)
3. Tell them to install FFmpeg first

That's it! 🎉

