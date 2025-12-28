"""
Build script for creating executable with PyInstaller
Run this script to build the executable: py build_exe.py
"""

import PyInstaller.__main__
import os

# Get the project root directory (parent of build_scripts/)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
assets_dir = os.path.join(project_root, 'assets')
src_dir = os.path.join(project_root, 'src')
main_script = os.path.join(project_root, 'main.py')

# PyInstaller arguments
args = [
    main_script,                  # Main script (full path)
    '--name=ITG Video Compressor',  # Name of the executable
    '--onefile',                 # Create a single executable file
    '--windowed',                # No console window (GUI only)
    f'--icon={os.path.join(assets_dir, "ITG-Small-Logo.ico")}',  # Set icon for executable
    
    # Add data files (assets) - Windows uses semicolon, Unix uses colon
    f'--add-data={assets_dir};assets' if os.name == 'nt' else f'--add-data={assets_dir}:assets',
    
    # Add src folder as data so it's included in the bundle
    f'--add-data={src_dir};src' if os.name == 'nt' else f'--add-data={src_dir}:src',
    
    # Add src to Python path so PyInstaller can find modules during analysis
    f'--paths={src_dir}',
    
    # Add hooks directory for custom hooks
    f'--additional-hooks-dir={script_dir}',
    
    # Hidden imports - explicitly tell PyInstaller about our modules
    '--hidden-import=app',
    '--hidden-import=compressor',
    '--hidden-import=customtkinter',
    '--hidden-import=PIL',
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=moviepy',
    '--hidden-import=moviepy.editor',
    '--hidden-import=moviepy.video',
    '--hidden-import=moviepy.audio',
    '--hidden-import=imageio',
    '--hidden-import=imageio.plugins',
    '--hidden-import=imageio.plugins.ffmpeg',
    '--hidden-import=imageio_ffmpeg',
    '--hidden-import=imageio_ffmpeg.get_ffmpeg_exe',
    '--hidden-import=imageio_ffmpeg.get_ffmpeg_exe',
    '--hidden-import=soupsieve',  # Required for gdown/beautifulsoup
    '--collect-all=gdown',        # Collect all gdown data/dependencies
    '--collect-all=certifi',      # Required for SSL requests
    '--collect-all=pysocks',      # Often needed for requests
    '--collect-all=imageio',      # Collect everything including metadata
    '--collect-all=moviepy',      # Collect everything including metadata
    '--collect-submodules=imageio',
    '--collect-submodules=moviepy',
    
    # Exclude unnecessary modules to reduce size
    '--exclude-module=matplotlib',
    '--exclude-module=numpy.distutils',
    '--exclude-module=scipy',
    '--exclude-module=pytest',
    '--exclude-module=test',
    
    # Clean build folder before building
    '--clean',
    
    # Output directory (relative to project root)
    f'--distpath={os.path.join(project_root, "dist")}',
    f'--workpath={os.path.join(project_root, "build")}',
]

print("Building executable...")
print("This may take a few minutes...")
PyInstaller.__main__.run(args)

print("\n" + "="*50)
print("Build complete!")
print("="*50)
print(f"\nExecutable location: {os.path.join(project_root, 'dist', 'ITG_Video_Compressor.exe')}")
print("\nNote: The executable will be large (~100-200MB) because it includes Python and all dependencies.")
print("You can distribute this single .exe file to users.")

