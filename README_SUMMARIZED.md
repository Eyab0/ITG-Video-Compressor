# ITG Video Compressor - Quick Summary

**Developed by:** Eyab Ghifari | **For:** ITG Software QA Team  
**Copyright:** © 2025 Eyab Ghifari | ITG Software

---

## 🚀 Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Run**: `python main.py`
3. **Add videos**: Click "SELECT LOCAL FILE" or "IMPORT FROM DRIVE"
4. **Set target size**: Default 10MB (adjustable)
5. **Compress**: Click "COMPRESS NOW"

---

## ✨ Main Features

- ✅ Batch compress multiple videos
- ✅ Target size compression (default: 10MB)
- ✅ Google Drive import
- ✅ Light/Dark theme
- ✅ Real-time progress & colored logs
- ✅ Smart timeout (prevents hanging)

---

## 📊 Processing Status

| Status | Meaning | When It Happens | Why It Happens |
|--------|---------|-----------------|----------------|
| ✅ **Done** | Success | Video compressed successfully | Valid video, completed within timeout, output created |
| ⏱️ **Timeout** | Too slow | Processing exceeded calculated time limit | Video too long, corrupted, or system resources limited |
| ❌ **Error** | Failed | Invalid file, corruption, or encoding error | Corrupted video, no duration, too small, codec issues, disk space |
| ⏳ **Pending** | Waiting | In queue, not processed yet | Normal state before processing begins |
| ⚙️ **Processing** | Active | Currently compressing | Normal state during active compression |

---

## ⏱️ Timeout System

- **Calculation**: `(Video Duration × 2) + 60s overhead + 2min buffer`
- **Maximum**: 15 minutes per video (absolute cap)
- **Examples**:
  - 1 min video → 5 min timeout
  - 3 min video → 9 min timeout
  - 5 min video → 13 min timeout

---

## ❌ Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| **Invalid duration** | Corrupted video or missing metadata | Use different video file or re-download |
| **File too small** | Not a valid video file | Check file type and size |
| **Timeout** | Video processing too slow | Video skipped automatically, try shorter videos |
| **Permission error** | No write access to folder | Check folder permissions or run as admin |
| **FFmpeg not found** | Missing FFmpeg installation | Install FFmpeg and add to system PATH |
| **Browser download issues** | Missing metadata in downloaded video | App handles this automatically with ffprobe fallback |
| **Disk space** | Insufficient space for output | Free up disk space |

---

## 🔧 Requirements

- Python 3.8+
- FFmpeg (must be in PATH)
- Dependencies: `pip install -r requirements.txt`

---

## 📦 Build Executable

```bash
python build_scripts\build_exe.py
```

Output: `dist\ITG_Video_Compressor.exe`

---

## 🧪 Run Tests

```bash
py -m pytest tests/ -v
```

---

## 📝 Notes

- **Browser downloads**: App handles videos with missing metadata
- **All videos**: Processes all videos regardless of size or duration
- **Logs**: Click "Show Logs" to see detailed colored output
- **Refresh**: Use "🔄 REFRESH" button to reset everything
- **Abort**: Click "⏹ ABORT" to stop current compression

---

**For detailed documentation, see [README.md](README.md)**

