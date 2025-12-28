# PyInstaller hook for imageio
# This helps PyInstaller find all imageio modules and metadata

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all imageio submodules
hiddenimports = collect_submodules('imageio')

# Collect imageio data files (including metadata)
datas = collect_data_files('imageio')

