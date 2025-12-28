# ITG Video Compressor - Distribution Package

## For End Users

### System Requirements

- **Windows 10/11** (64-bit)
- **FFmpeg** must be installed and added to system PATH
  - Download: https://ffmpeg.org/download.html
  - Installation guide: https://www.ffmpeg.org/download.html

### Installation

1. **Install FFmpeg** (if not already installed):
   - Download FFmpeg from https://ffmpeg.org/download.html
   - Extract to a folder (e.g., `C:\ffmpeg`)
   - Add FFmpeg to your system PATH:
     - Open System Properties → Environment Variables
     - Add `C:\ffmpeg\bin` to your PATH
   - Verify installation: Open Command Prompt and type `ffmpeg -version`

2. **Run the Application**:
   - Double-click `ITG_Video_Compressor.exe`
   - No installation needed - it's a portable application

### Usage

1. Click **"SELECT LOCAL FILE"** to choose videos
2. Or click **"IMPORT FROM DRIVE"** to import from Google Drive
3. Adjust target size if needed (default: 10MB)
4. Click **"COMPRESS NOW"** to start
5. Compressed videos will be saved in the same folder (or custom output folder)

### Troubleshooting

**"FFmpeg not found" error:**
- Make sure FFmpeg is installed
- Verify FFmpeg is in your system PATH
- Test by running `ffmpeg -version` in Command Prompt

**Application won't start:**
- Make sure you have Windows 10/11 (64-bit)
- Try running as Administrator
- Check Windows Defender isn't blocking it

**Compression fails:**
- Check the logs by clicking "Show Logs"
- Verify video file is not corrupted
- Ensure sufficient disk space

### Support

For ITG Software QA Team members:
- Contact ITG Software Development Team
- Report issues through internal channels

---

**© 2025 Eyab Ghifari | ITG Software**

