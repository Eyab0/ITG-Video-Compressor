@echo off
REM Simple batch file to build the executable
echo ========================================
echo Building ITG Video Compressor Executable
echo ========================================
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

echo.
echo Starting build process...
echo This may take several minutes...
echo.

REM Change to project root directory
cd /d "%~dp0.."

REM Run the build script
python build_scripts\build_exe.py

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Your executable is in the 'dist' folder:
echo dist\ITG_Video_Compressor.exe
echo.
pause

