# PyInstaller hook for moviepy
# This helps PyInstaller find all moviepy modules

from PyInstaller.utils.hooks import collect_submodules

# Collect all moviepy submodules
hiddenimports = collect_submodules('moviepy')

