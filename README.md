# ITG Video Compressor

<div align="center">

**An ITG Software Internal Tool**

A modern, professional video compression application built with Python and CustomTkinter.  
**Designed specifically for the ITG Software QA Team** to efficiently compress videos while maintaining quality.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![ITG Software](https://img.shields.io/badge/ITG-Software-orange.svg)
![QA Team](https://img.shields.io/badge/For-QA%20Team-green.svg)

</div>

---

## 🏢 About ITG Software

**ITG Video Compressor** is an internal tool developed by **Eyab Ghifari** for **ITG Software** and designed specifically for use by our Quality Assurance (QA) team. This application streamlines the video compression workflow, allowing QA team members to quickly prepare test videos for sharing, reporting, and documentation purposes.

### Developer

**Developed by:** Eyab Ghifari  
**For:** ITG Software QA Team  
**Copyright:** © 2025 Eyab Ghifari

### Purpose

This tool is specifically designed to help the QA team:
- Compress large video files to manageable sizes for sharing
- Batch process multiple test case videos
- Maintain video quality while reducing file size
- Streamline the video preparation workflow for bug reports and test documentation

### Target Users

- **Primary**: ITG Software QA Team Members
- **Internal Use Only**: This tool is intended for internal ITG Software use

## 📋 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
- [Testing](#-testing)
- [Test Coverage](#-test-coverage)
- [Project Structure](#-project-structure)
- [Architecture & Design](#-architecture--design)
- [Technical Details](#-technical-details)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Changelog](#-changelog)

## ✨ Features

- **Modern UI**: Clean, professional interface with light/dark theme support
- **Native Windows Taskbar Integration**: Custom taskbar icon and proper window grouping
- **Batch Processing**: Compress multiple videos in a single queue
- **Size Target**: Compress videos to a specific target size (default 10MB)
- **Format Support**: Supports common video formats (MP4, MOV, AVI, MKV)
- **Speed vs Quality**: Choose between "Fast" (faster processing) or "Balanced" (better quality) modes
- **Google Drive Integration**: Import videos directly from Google Drive links
- **Custom Output**: Choose custom output folders and file suffixes
- **Progress Tracking**: Real-time progress bar and detailed colored logs
- **Queue Management**: Add, remove, and manage multiple videos with improved visual feedback
- **Logs Viewer**: integrated in-app logs console to view processing details without checking a terminal
- **Error Handling**: Graceful error handling with detailed status messages
- **Smart Timeout**: Dynamic timeout calculation based on video duration
- **Colored Logs**: Color-coded log messages (success, error, warning, timeout, skip)
- **Status Tracking**: Real-time status updates for each video (Pending, Processing, Done, Error, Timeout)

## 🔧 Requirements

### System Requirements
- **Python 3.8+** (Python 3.13 recommended)
- **FFmpeg**: Must be installed and added to your system PATH
  - [Download FFmpeg](https://ffmpeg.org/download.html)
  - [FFmpeg Installation Guide](https://www.ffmpeg.org/download.html)
  - *If FFmpeg is not installed, video compression will fail*

### Python Dependencies
All dependencies are listed in `requirements.txt`:
- `customtkinter` - Modern UI framework
- `moviepy` - Video processing
- `Pillow` - Image processing
- `gdown` - Google Drive integration
- `colorama` - Colored terminal output
- `pytest` - Testing framework

## 📦 Installation

1. **Clone or download this repository**
   ```bash
   cd vid-comp
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Or using Python's module:
   ```bash
   py -m pip install -r requirements.txt
   ```

3. **Verify FFmpeg installation**
   ```bash
   ffmpeg -version
   ```
   If this command fails, install FFmpeg and add it to your PATH.

4. **Verify installation**
   ```bash
   py main.py
   ```

## 🚀 Usage

### Basic Usage

1. **Launch the application**
   ```bash
   py main.py
   ```
   Or alternatively:
   ```bash
   python main.py
   ```

2. **Select video files**
   - Click **"SELECT LOCAL FILE"** to choose videos from your computer
   - Or click **"IMPORT FROM DRIVE"** to import from Google Drive

3. **Configure settings**
   - **Target Size**: Set the desired output size in MB (default: 10MB)
   - **Mode**: Choose between **Fast** (default, faster processing) or **Balanced** (better quality)
   - **Suffix**: Customize the output filename suffix (default: `_compressed`)
   - **Output Folder**: Choose a custom output folder (optional, defaults to source folder)

4. **Start compression**
   - Click **"COMPRESS NOW"** to begin processing
   - Monitor progress in the progress bar and status messages
   - View detailed logs by clicking **"Show Logs"**

5. **Access compressed videos**
   - Compressed videos are saved in the output folder (or source folder if not specified)
   - Filename format: `original_name_suffix.mp4`

### Advanced Features

- **Batch Processing**: Add multiple videos to the queue and compress them all at once
- **Queue Management**: Remove videos from the queue before compression
- **Theme Toggle**: Switch between light and dark themes using the toggle button
- **Abort & Resume**: Abort compression mid-process and start over if needed

## 🧪 Testing

This project includes a comprehensive test suite with **56 test cases** covering all major functionality.

### Running Tests

**Run all tests:**
```bash
py -m pytest tests/ -v
```

**Run specific test file:**
```bash
py -m pytest tests/test_compressor.py -v
py -m pytest tests/test_app.py -v
py -m pytest tests/test_integration.py -v
```

**Run specific test class:**
```bash
py -m pytest tests/test_integration.py::TestRealVideoCompression -v -s
```

**Run with coverage report:**
```bash
py -m pytest --cov=src.compressor --cov=src.app tests/ -v
```

**Run tests with output:**
```bash
py -m pytest -v -s
```

### Test Files

- **`tests/test_compressor.py`** - Unit tests for VideoCompressor class (23 tests)
- **`tests/test_app.py`** - Tests for application logic and file operations (20 tests)
- **`tests/test_integration.py`** - Integration tests including real video compression (13 tests)

## 📊 Test Coverage

### VideoCompressor Tests (23 tests)

#### Initialization Tests (7 tests)
- ✅ Default values initialization
- ✅ Custom values initialization
- ✅ Zero size initialization
- ✅ Negative size initialization
- ✅ Very large size initialization
- ✅ Zero bitrate initialization
- ✅ High bitrate initialization

#### Compression Tests (10 tests)
- ✅ Invalid path handling
- ✅ Nonexistent output directory handling
- ✅ Empty path handling
- ✅ None path error handling
- ✅ Successful compression workflow
- ✅ Size warning when exceeding target
- ✅ Exception handling
- ✅ Custom bitrate settings
- ✅ Progress callback parameter
- ✅ Same input/output path handling

#### Path Handling Tests (4 tests)
- ✅ Relative paths
- ✅ Absolute paths
- ✅ Special characters in paths
- ✅ Long filenames

#### Additional Tests (2 tests)
- ✅ Max size bytes calculation
- ✅ Multiple compressor instances

### App Logic Tests (20 tests)

#### File Path Operations (4 tests)
- ✅ File path manipulation
- ✅ Output path generation (same folder)
- ✅ Output path generation (custom folder)
- ✅ Output path with different suffixes

#### File Operations (5 tests)
- ✅ File size calculation
- ✅ Filename truncation
- ✅ Queue duplicate detection
- ✅ Target size validation
- ✅ Batch compression progress calculation

#### File System Tests (5 tests)
- ✅ Temporary directory creation
- ✅ File existence checking
- ✅ Directory creation
- ✅ File extension extraction
- ✅ Video file filtering

#### Error Handling (3 tests)
- ✅ Missing file graceful handling
- ✅ Permission error handling
- ✅ Invalid characters in paths

#### Utility Tests (3 tests)
- ✅ Suffix default value handling
- ✅ Various utility functions

### Integration Tests (13 tests)

#### Workflow Tests (6 tests)
- ✅ Full compression workflow (mocked)
- ✅ Batch processing simulation
- ✅ Different target sizes
- ✅ Different bitrates
- ✅ Output path variations
- ✅ Concurrent compressor instances

#### Edge Cases (6 tests)
- ✅ Very small target size
- ✅ Very large target size
- ✅ Fractional target size
- ✅ Unicode characters in paths
- ✅ Spaces in paths
- ✅ Special characters in paths

#### Real Video Tests (3 tests)
- ✅ Real video file compression
- ✅ Real video with different target sizes
- ✅ Real video file information extraction

### Test Statistics

- **Total Tests**: 56
- **Test Files**: 3
- **Test Classes**: 8
- **Coverage Areas**:
  - VideoCompressor class: 100%
  - File operations: 100%
  - Path handling: 100%
  - Error handling: 100%
  - Integration workflows: 100%

### Real Video Testing

The test suite includes tests that use actual video files:
- **Test Video**: `GH - iPhone Test Case.mp4` (~40.75 MB)
- **Location**: `C:\Users\EyabGhifari\Desktop\test\`
- **Tests**: Real compression with various target sizes

To run real video tests:
```bash
py -m pytest tests/test_integration.py::TestRealVideoCompression -v -s
```

## 🏗️ Architecture & Design

For a deep dive into the system's modular architecture, design patterns, and data flow, please read our **[Architecture Documentation](PROJECT_ARCHITECTURE.md)**.

## 📁 Project Structure

```
vid-comp/
│
├── main.py                    # Application entry point
├── build.bat                  # Quick build script (Windows)
├── requirements.txt           # Python dependencies
├── README.md                  # Main project documentation
├── LICENSE                    # License file
├── .gitignore                # Git ignore rules
│
├── src/                       # Source code package
│   ├── __init__.py           # Package initialization
│   ├── app.py                # Main application GUI
│   └── compressor.py         # VideoCompressor class
│
├── tests/                     # Test suite
│   ├── __init__.py           # Test package initialization
│   ├── test_compressor.py    # VideoCompressor unit tests (23 tests)
│   ├── test_app.py           # Application logic tests (20 tests)
│   └── test_integration.py   # Integration tests (13 tests)
│
├── assets/                    # Application assets
│   ├── ITG-Logo.png          # Application logo
│   ├── toggle_sun.png        # Light theme toggle icon
│   └── toggle_moon.png       # Dark theme toggle icon
│
├── build_scripts/            # Build and packaging scripts
│   ├── README.md             # Build scripts documentation
│   ├── build_exe.py          # Main Python build script
│   ├── build.bat             # Windows batch build script
│   └── build_spec.spec       # PyInstaller spec file
│
├── docs/                     # Documentation
│   ├── README.md             # Documentation index
│   ├── build_instructions.md # Detailed build instructions
│   ├── DISTRIBUTION_README.md # User instructions for distribution
│   └── QUICK_START_BUILD.md  # Quick build guide
│
├── build/                    # Build artifacts (generated, gitignored)
└── dist/                     # Distribution folder (generated, gitignored)
    └── ITG_Video_Compressor.exe
```

### Directory Overview

- **`src/`** - Source code package
  - `app.py` - Main Application Controller (Assembly)
  - `compressor.py` - Core video compression logic
  - **`ui/`** - User Interface Components
    - `styles.py` - Theme and Color management
    - `widgets/` - Reusable UI components (Header, FileList, etc.)
  - **`utils/`** - Utility modules
    - `assets.py` - Resource management
    - `drive_importer.py` - Google Drive integration

- **`tests/`** - Test suite (57 tests total)
  - `test_compressor.py` - Logic tests
  - `test_app.py` - Controller tests
  - `test_integration.py` - Full workflow tests
  - `test_refactor_structure.py` - Architecture verification

- **Documentation**
  - `PROJECT_ARCHITECTURE.md` - Technical deep-dive
  - `CONTRIBUTING.md` - Developer guidelines
  - `CHANGELOG.md` - Version history

- **Root files**
  - `main.py` - Entry point to launch the application
  - `build.bat` - Quick build script (runs from root)
  - `requirements.txt` - Python package dependencies
  - `README.md` - Main project documentation
  - `LICENSE` - License information

## 🔍 Technical Details

### Compression Settings

The application uses optimized FFmpeg settings for video compression:
- **Codec**: H.264 (libx264)
- **Audio Codec**: AAC
- **Bitrate**: Dynamically calculated based on video duration and target size
  - **Formula**: `(Target Size MB × 8 × 1024 × 0.9) / Video Duration (seconds)`
  - **Allocation**: 90% for video, 10% for audio
  - **Minimum**: 400 kbps (quality protection)
  - **Maximum**: 5000 kbps (file size protection)
- **Audio Bitrate**: 128 kbps (fixed)
- **Preset**: medium (balanced quality/speed)
- **Threads**: 4 (multi-threaded processing)

### Processing Status & Outcomes

The application tracks each video's processing status. Here's what each status means:

#### ✅ **Done** - Successful Compression
- **When it happens**: Video was successfully compressed and saved
- **Why it happens**: 
  - Video file was valid and readable
  - Compression completed within the calculated timeout
  - Output file was created successfully
  - Final file size is within acceptable range (target ± 10%)
- **What to expect**: Compressed video file saved with the specified suffix

#### ⏱️ **Timeout** - Processing Timeout
- **When it happens**: Video processing exceeded the calculated maximum time
- **Why it happens**:
  - Video is very long (processing time = video duration × 2 + overhead)
  - Video file is corrupted or has encoding issues
  - System resources are limited (CPU/memory)
  - Video has complex encoding that takes longer to process
- **Calculation**: 
  - Expected time = (Video Duration × 2) + 60 seconds overhead
  - Maximum timeout = Expected time + 2 minutes buffer
  - Absolute maximum = 15 minutes per video
- **What happens**: Video is skipped, processing continues with next video
- **Example**: A 5-minute video gets ~13 minutes max, a 10-minute video gets 15 minutes max

#### ❌ **Error** - Compression Failed
- **When it happens**: Compression process encountered an error
- **Why it happens**:
  - Video file is corrupted or invalid
  - Video has no duration or invalid duration (0 or negative)
  - Video file is too small (< 1KB) - likely not a valid video
  - Cannot read video metadata (missing codec info, etc.)
  - FFmpeg encoding error during compression
  - Insufficient disk space for output file
  - Permission errors (cannot write to output location)
  - Video format not supported or codec issues
- **What happens**: Error is logged, video is marked as failed, processing continues
- **Common causes**:
  - Browser-downloaded videos with missing metadata
  - Corrupted video files
  - Unsupported video codecs
  - Disk space issues

#### ⏳ **Pending** - Waiting to Process
- **When it happens**: Video is in queue but not yet processed
- **Why it happens**: Normal state before processing begins
- **What happens**: Video will be processed when its turn comes

#### ⚙️ **Processing...** - Currently Compressing
- **When it happens**: Video is currently being compressed
- **Why it happens**: Normal state during active compression
- **What happens**: Compression is in progress, wait for completion

### Dynamic Timeout Calculation

The application uses intelligent timeout calculation based on video duration:

1. **Duration Detection**: Uses `ffprobe` first (more reliable), falls back to MoviePy
2. **Expected Time Calculation**: `(Video Duration × 2) + 60 seconds overhead`
3. **Timeout Buffer**: Adds 2 minutes (120 seconds) buffer for variations
4. **Maximum Cap**: Absolute maximum of 15 minutes (900 seconds) per video
5. **Examples**:
   - 1-minute video: ~5 minutes timeout
   - 3-minute video: ~9 minutes timeout
   - 5-minute video: ~13 minutes timeout
   - 10-minute video: 15 minutes timeout (capped)

### Error Handling & Recovery

The application includes robust error handling:

- **Invalid Videos**: Automatically detected and skipped
- **Browser Downloads**: Special handling for videos with missing metadata
- **Timeout Protection**: Prevents infinite hangs on problematic videos
- **Graceful Degradation**: Continues processing remaining videos even if one fails
- **Detailed Logging**: All errors and status changes are logged with timestamps

### Architecture

- **GUI Framework**: CustomTkinter (modern Tkinter wrapper)
- **Video Processing**: MoviePy (FFmpeg wrapper)
- **Threading**: Separate thread for compression to keep UI responsive
- **Error Handling**: Comprehensive try-catch blocks with user-friendly messages

### Performance

- **Batch Processing**: Processes videos sequentially in a queue
- **Progress Tracking**: Real-time progress updates
- **Memory Management**: Proper cleanup of video clips after processing
- **Abort Functionality**: Can safely abort compression mid-process

## 🐛 Troubleshooting

### Common Issues

**Issue: "FFmpeg not found"**
- **Solution**: Install FFmpeg and add it to your system PATH
- Verify with: `ffmpeg -version`

**Issue: "Compression fails silently"**
- **Solution**: Check the logs by clicking "Show Logs" button
- Verify video file is not corrupted
- Ensure sufficient disk space

**Issue: "Video file too large after compression"**
- **Solution**: Reduce the target size or bitrate
- Some videos may not compress below certain sizes while maintaining quality

**Issue: "Permission errors"**
- **Solution**: Ensure you have write permissions in the output folder
- Try running as administrator if needed

**Issue: "Import from Drive fails"**
- **Solution**: Verify the Google Drive link is publicly accessible
- Check internet connection
- Ensure `gdown` package is installed

### Getting Help

1. Check the logs in the application (click "Show Logs")
2. Run tests to verify installation: `py -m pytest tests/ -v`
3. Check FFmpeg installation: `ffmpeg -version`
4. Verify all dependencies: `pip list`

## 🤝 Contributing

We welcome contributions! Please read our **[Contributing Guidelines](CONTRIBUTING.md)** for details on our code of conduct and the process for submitting pull requests.

### For ITG Software Developers

To contribute to this project:

1. Read **[CONTRIBUTING.md](CONTRIBUTING.md)** carefully.
2. Get approval from the ITG Software Development Team Lead
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for your changes
4. Ensure all tests pass (`py -m pytest tests/ -v`)
5. Follow ITG Software coding standards
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch and create an internal Pull Request
8. Get code review approval before merging

### Code Style

- Follow PEP 8 Python style guide
- Follow ITG Software internal coding standards
- Add docstrings to all functions and classes
- Write tests for new features (maintain 100% test coverage)
- Update README if adding new features
- Ensure all tests pass before submitting PR

## � Changelog

See **[CHANGELOG.md](CHANGELOG.md)** for a complete version history of the project.

## �📝 License & Copyright

### ITG Software Proprietary License

**Copyright © 2025 Eyab Ghifari | ITG Software. All Rights Reserved.**

**Developer:** Eyab Ghifari  
**Company:** ITG Software

This software and associated documentation files (the "Software") are the proprietary and confidential property of ITG Software. The Software is provided for internal use only by ITG Software employees and authorized personnel.

#### License Terms

1. **Internal Use Only**: This Software is licensed for internal use within ITG Software only.
2. **No Redistribution**: You may not copy, modify, distribute, sell, or lease any part of this Software.
3. **No Reverse Engineering**: You may not reverse engineer, decompile, or disassemble the Software.
4. **Confidentiality**: The Software contains proprietary information and trade secrets of ITG Software.
5. **Termination**: This license is effective until terminated. ITG Software reserves the right to terminate this license at any time.

#### Third-Party Licenses

This Software uses the following third-party libraries, each with their respective licenses:

- **CustomTkinter** - [MIT License](https://github.com/TomSchimansky/CustomTkinter/blob/master/LICENSE)
- **MoviePy** - [MIT License](https://github.com/Zulko/moviepy/blob/master/LICENSE.txt)
- **Pillow (PIL)** - [HPND License](https://github.com/python-pillow/Pillow/blob/main/LICENSE)
- **gdown** - [MIT License](https://github.com/wkentaro/gdown/blob/master/LICENSE)
- **colorama** - [BSD License](https://github.com/tartley/colorama/blob/master/LICENSE.txt)
- **pytest** - [MIT License](https://github.com/pytest-dev/pytest/blob/main/LICENSE)
- **FFmpeg** - [LGPL/GPL License](https://ffmpeg.org/legal.html)

For questions regarding licensing, please contact ITG Software Legal Department.

## 🙏 Acknowledgments

This tool was developed by **ITG Software** for internal use by our Quality Assurance team.

### Third-Party Libraries

We gratefully acknowledge the following open-source projects:

- **CustomTkinter** - Modern UI framework ([MIT License](https://github.com/TomSchimansky/CustomTkinter))
- **MoviePy** - Video processing library ([MIT License](https://github.com/Zulko/moviepy))
- **FFmpeg** - Video encoding/decoding ([LGPL/GPL License](https://ffmpeg.org/legal.html))
- **Pillow** - Image processing library ([HPND License](https://github.com/python-pillow/Pillow))
- **gdown** - Google Drive integration ([MIT License](https://github.com/wkentaro/gdown))
- **pytest** - Testing framework ([MIT License](https://github.com/pytest-dev/pytest))

## 📦 Distribution & Building Executable

### Creating a Standalone Executable

To distribute the application as a standalone `.exe` file (no Python installation required):

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**:
   
   **Easiest method** (from project root):
   ```bash
   build.bat
   ```
   
   Or use Python:
```bash
   python build_scripts\build_exe.py
   ```
   
   Or manually:
   ```bash
   pyinstaller --name=ITG_Video_Compressor --onefile --windowed --add-data="assets;assets" main.py
   ```

3. **Find your executable**:
   - Location: `dist/ITG_Video_Compressor.exe`
   - This is a single file that can be distributed

### Important Notes for Distribution

⚠️ **FFmpeg Requirement**: The executable does NOT include FFmpeg. Users must install FFmpeg separately.

**Options:**
- **Option A**: Provide FFmpeg installation instructions (see `docs/DISTRIBUTION_README.md`)
- **Option B**: Bundle FFmpeg with the executable (requires additional setup)

### Distribution Package

When distributing, include:
1. `ITG_Video_Compressor.exe` (from `dist/` folder)
2. `docs/DISTRIBUTION_README.md` (user instructions)
3. FFmpeg installation guide or bundled FFmpeg

See `docs/build_instructions.md` for detailed build instructions.

## 📧 Support & Contact

### For ITG Software QA Team

- **Internal Support**: Contact the ITG Software Development Team
- **Issues**: Report issues through internal ITG Software channels
- **Feature Requests**: Submit feature requests to the ITG Software Development Team

### ITG Software

**ITG Software** - Internal Development Tools  
*This is proprietary software developed for internal use by ITG Software.*

---

<div align="center">

**Made with ❤️ by Eyab Ghifari for ITG Software QA Team**

**© 2025 Eyab Ghifari | ITG Software. All Rights Reserved.**

</div>
