import os
import sys
import shutil
import threading
try:
    import gdown
except ImportError:
    gdown = None

class DriveImporter:
    def __init__(self, status_callback, finish_callback, fail_callback):
        self.status_callback = status_callback
        self.finish_callback = finish_callback
        self.fail_callback = fail_callback

    def check_requirements(self):
        return gdown is not None

    def start_download(self, url):
        threading.Thread(target=self._download_worker, args=(url,), daemon=True).start()

    def _download_worker(self, url):
        try:
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                if not os.path.exists(os.path.join(base_path, "main.py")):
                     base_path = os.getcwd() 

            download_dir = os.path.join(base_path, "downloads")
            
            try:
                if os.path.exists(download_dir):
                    shutil.rmtree(download_dir)
                os.makedirs(download_dir, exist_ok=True)
            except Exception as e:
                print(f"Warning cleaning downloads: {e}")
                os.makedirs(download_dir, exist_ok=True)
            
            downloaded_files = []
            original_cwd = os.getcwd()
            
            try:
                os.chdir(download_dir)
                
                if "/folders/" in url or "drive.google.com/drive/u/0/folders" in url:
                    self.status_callback("Detected Drive Folder. Downloading batch...")
                    results = gdown.download_folder(url, output=".", quiet=True, use_cookies=False)
                    if results:
                        downloaded_files = [os.path.abspath(f) for f in results]
                else:
                    self.status_callback("Downloading single file...")
                    print(f"Downloading file from {url}...")
                    filename = gdown.download(url, quiet=True, fuzzy=True, output=None)
                    if filename:
                        downloaded_files.append(os.path.abspath(filename))
            finally:
                os.chdir(original_cwd)

            if downloaded_files:
                valid_files = [f for f in downloaded_files if os.path.exists(f)]
                if valid_files:
                     self.finish_callback(valid_files)
                else:
                     self.fail_callback("No valid files found after download.")
            else:
                self.fail_callback("No files downloaded. Check link permissions.")
                
        except Exception as e:
            print(f"Download Error: {e}")
            self.fail_callback(str(e))
