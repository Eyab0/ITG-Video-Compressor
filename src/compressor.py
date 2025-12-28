import os
import sys
import subprocess
import time

# Workaround for PyInstaller metadata issue with imageio
# This prevents the PackageNotFoundError when running as executable
if getattr(sys, 'frozen', False):
    # Running as PyInstaller executable - patch importlib.metadata
    try:
        import importlib.metadata
        # Monkey-patch to handle missing metadata gracefully
        _original_from_name = importlib.metadata.distribution
        
        def _patched_distribution(name):
            try:
                return _original_from_name(name)
            except importlib.metadata.PackageNotFoundError:
                # Return a minimal distribution object
                class MinimalDist:
                    version = "unknown"
                    def read_text(self, name): return None
                return MinimalDist()
        
        importlib.metadata.distribution = _patched_distribution
    except Exception:
        pass  # If patching fails, continue anyway

from moviepy.editor import VideoFileClip
from colorama import init, Fore

init(autoreset=True)

class VideoCompressor:
    def __init__(self, target_size_mb=9, safe_bitrate_kbps=800):
        """
        Initialize the compressor with target size and bitrate.
        
        Args:
            target_size_mb: Maximum target size in MB (default 9)
            safe_bitrate_kbps: Safe bitrate in kbps (default 800)
        """
        self.target_size_mb = target_size_mb
        self.safe_bitrate_kbps = safe_bitrate_kbps
        self.max_size_bytes = target_size_mb * 1024 * 1024

    def compress_video(self, input_path, output_path, progress_callback=None, max_processing_time=None, preset="medium"):
        """
        Compress video using MoviePy with calculated bitrate to achieve target size.
        
        Args:
            input_path: Path to input video
            output_path: Path to save compressed video
            progress_callback: Optional callback for progress updates
            max_processing_time: Maximum allowed processing time in seconds (calculated from duration if None)
            preset: FFmpeg preset (e.g. 'medium', 'faster', 'veryfast')
            
        Returns:
            True if successful, False otherwise
        """
        video_name = os.path.basename(input_path)
        print(Fore.CYAN + f"\n🎬 Compressing: {video_name}")
        
        clip = None
        try:
            # Try to load video with timeout protection
            # First, check if file exists and is readable
            if not os.path.exists(input_path):
                print(Fore.RED + f"⚠️ Error: {video_name} - File not found.")
                return False
            
            # Try to get file size - if it's 0 or very small, it's likely invalid
            file_size = os.path.getsize(input_path)
            if file_size < 1024:  # Less than 1KB is suspicious
                print(Fore.RED + f"⚠️ Error: {video_name} - File too small ({file_size} bytes). Likely invalid video.")
                return False
            
            # Try to load the video clip with timeout
            # For browser downloads, sometimes metadata is missing but video is valid
            duration = None
            clip = None
            
            # First, try to get duration using ffprobe (more reliable for browser downloads)
            try:
                result = subprocess.run(
                    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                     '-of', 'default=noprint_wrappers=1:nokey=1', input_path],
                    capture_output=True,
                    text=True,
                    timeout=10  # 10 second timeout
                )
                if result.returncode == 0 and result.stdout.strip():
                    duration = float(result.stdout.strip())
                    print(Fore.CYAN + f"📹 Got duration from ffprobe: {duration:.2f}s")
            except (subprocess.TimeoutExpired, ValueError, FileNotFoundError, subprocess.SubprocessError) as e:
                print(Fore.YELLOW + f"⚠️ Could not get duration from ffprobe: {e}. Trying MoviePy...")
            
            # If ffprobe failed, try MoviePy
            if duration is None:
                try:
                    clip = VideoFileClip(input_path)
                    duration = clip.duration
                except Exception as load_error:
                    print(Fore.RED + f"⚠️ Error: {video_name} - Cannot load video file: {load_error}")
                    return False
            
            # Validate duration
            if duration is None:
                print(Fore.RED + f"⚠️ Error: {video_name} has no duration (None). Skipping.")
                if clip:
                    clip.close()
                return False
            
            if duration <= 0:
                print(Fore.RED + f"⚠️ Error: {video_name} has invalid duration ({duration} seconds). Skipping.")
                if clip:
                    clip.close()
                return False
            
            if duration < 0.1:  # Less than 100ms
                print(Fore.RED + f"⚠️ Error: {video_name} is too short ({duration:.2f} seconds). Minimum 0.1 seconds required.")
                if clip:
                    clip.close()
                return False
            
            # Calculate expected processing time based on video duration
            # Processing typically takes 1.5-2x the video duration, plus overhead
            # For compression: encoding is CPU-intensive, so longer videos take proportionally longer
            processing_factor = 2.0  # Processing takes roughly 2x the video duration
            overhead_seconds = 60    # Fixed overhead for setup, file I/O, etc.
            expected_processing_time = (duration * processing_factor) + overhead_seconds
            
            # Add buffer time (2 minutes = 120 seconds) to allow for variations
            buffer_seconds = 120
            max_allowed_time = expected_processing_time + buffer_seconds
            
            # Cap maximum at 15 minutes (900 seconds) to prevent extremely long waits
            absolute_max_time = 900
            if max_allowed_time > absolute_max_time:
                max_allowed_time = absolute_max_time
            
            duration_minutes = duration / 60
            expected_minutes = expected_processing_time / 60
            max_minutes = max_allowed_time / 60
            
            # Enhanced logging with colors and formatting
            print(Fore.CYAN + "═" * 80)
            print(Fore.CYAN + f"📹 Video duration: {duration_minutes:.1f} minutes ({duration:.1f} seconds)")
            print(Fore.CYAN + f"⏱️ Expected processing: {expected_minutes:.1f} minutes | Max allowed: {max_minutes:.1f} minutes (with {buffer_seconds/60:.1f} min buffer)")
            print(Fore.CYAN + "─" * 80)
            
            # Use provided max_processing_time or calculated one
            if max_processing_time is None:
                max_processing_time = max_allowed_time
            
            # If we got duration from ffprobe but don't have clip yet, load it now
            if clip is None:
                try:
                    clip = VideoFileClip(input_path)
                except Exception as load_error:
                    print(Fore.RED + f"⚠️ Error: {video_name} - Cannot load video file: {load_error}")
                    return False
            
            # Calculate bitrate needed to achieve target size
            # Formula: bitrate (kbps) = (target_size_mb * 8 * 1024) / duration (seconds)
            # We reserve ~10% for audio, so video gets ~90%
            target_size_bits = self.target_size_mb * 8 * 1024 * 1024  # Convert MB to bits
            video_bitrate_bps = (target_size_bits * 0.9) / duration  # 90% for video
            video_bitrate_kbps = int(video_bitrate_bps / 1000)
            
            # Audio bitrate (typically 128 kbps is good quality)
            audio_bitrate_kbps = 128
            
            # Ensure minimum bitrate for quality (at least 400 kbps for video)
            if video_bitrate_kbps < 400:
                video_bitrate_kbps = 400
                print(Fore.YELLOW + f"⚠️ Warning: Calculated bitrate too low, using minimum 400 kbps")
            
            # Ensure maximum reasonable bitrate (prevent huge files)
            max_bitrate_kbps = 5000
            if video_bitrate_kbps > max_bitrate_kbps:
                video_bitrate_kbps = max_bitrate_kbps
                print(Fore.YELLOW + f"⚠️ Warning: Calculated bitrate too high, capping at {max_bitrate_kbps} kbps")
            
            print(Fore.CYAN + f"📊 Video duration: {duration:.2f}s | Target: {self.target_size_mb}MB | Calculated bitrate: {video_bitrate_kbps}k")
            print(Fore.CYAN + "─" * 80)
            
            # Write video file (timeout is handled at thread level in app.py)
            start_time = time.time()
            try:
                clip.write_videofile(
                    output_path,
                    codec="libx264",
                    audio_codec="aac",
                    bitrate=f"{video_bitrate_kbps}k",
                    audio_bitrate=f"{audio_bitrate_kbps}k",
                    threads=4,
                    preset=preset,  # Use user-selected preset
                    verbose=False,  # Suppress moviepy output
                    logger=None
                )
            except Exception as write_error:
                elapsed = time.time() - start_time
                print(Fore.RED + f"⚠️ Error: {video_name} - Write failed after {elapsed:.0f}s: {write_error}")
                if clip:
                    clip.close()
                return False
            
            clip.close()

            # Check final size
            if not os.path.exists(output_path):
                print(Fore.RED + f"⚠️ Error: Output file was not created")
                return False
                
            final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            if final_size_mb > self.target_size_mb * 1.1:  # Allow 10% tolerance
                print(Fore.YELLOW + f"⚠️ Warning: {video_name} is {final_size_mb:.2f} MB (target was {self.target_size_mb} MB)")
            else:
                print(Fore.GREEN + f"✅ Done: {video_name} ({final_size_mb:.2f} MB / {self.target_size_mb} MB target)")

            return True

        except Exception as e:
            print(Fore.RED + f"⚠️ Error compressing {video_name}: {e}")
            import traceback
            traceback.print_exc()
            # Make sure to close clip if it was opened
            if clip:
                try:
                    clip.close()
                except:
                    pass
            return False
        finally:
            # Ensure clip is always closed
            if clip:
                try:
                    clip.close()
                except:
                    pass
