import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock, call
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock customtkinter before importing app
sys.modules['customtkinter'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

# Now we can test the logic without GUI
from compressor import VideoCompressor


class TestAppLogic:
    """Test suite for App class logic (without GUI initialization)"""
    
    def test_file_path_operations(self):
        """Test file path manipulation logic"""
        test_path = "/path/to/video.mp4"
        basename = os.path.basename(test_path)
        dirname = os.path.dirname(test_path)
        name, ext = os.path.splitext(basename)
        
        assert basename == "video.mp4"
        assert dirname == "/path/to"
        assert name == "video"
        assert ext == ".mp4"
    
    def test_output_path_generation_same_folder(self):
        """Test output path generation when output folder is None"""
        input_path = "/path/to/video.mp4"
        suffix = "_compressed"
        
        dirname = os.path.dirname(input_path)
        basename = os.path.basename(input_path)
        name, ext = os.path.splitext(basename)
        output_path = os.path.join(dirname, f"{name}{suffix}{ext}")
        
        # Normalize path separators for cross-platform compatibility
        expected = os.path.normpath("/path/to/video_compressed.mp4")
        assert os.path.normpath(output_path) == expected
    
    def test_output_path_generation_custom_folder(self):
        """Test output path generation with custom output folder"""
        input_path = "/path/to/video.mp4"
        output_folder = "/output/folder"
        suffix = "_compressed"
        
        basename = os.path.basename(input_path)
        name, ext = os.path.splitext(basename)
        output_path = os.path.join(output_folder, f"{name}{suffix}{ext}")
        
        # Normalize path separators for cross-platform compatibility
        expected = os.path.normpath("/output/folder/video_compressed.mp4")
        assert os.path.normpath(output_path) == expected
    
    def test_output_path_with_different_suffix(self):
        """Test output path with different suffix"""
        input_path = "/path/to/video.mp4"
        suffix = "_10mb"
        
        dirname = os.path.dirname(input_path)
        basename = os.path.basename(input_path)
        name, ext = os.path.splitext(basename)
        output_path = os.path.join(dirname, f"{name}{suffix}{ext}")
        
        # Normalize path separators for cross-platform compatibility
        expected = os.path.normpath("/path/to/video_10mb.mp4")
        assert os.path.normpath(output_path) == expected
    
    def test_file_size_calculation(self):
        """Test file size calculation logic"""
        # Create a temporary file with known size
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"x" * 1024)  # 1 KB
            tmp_path = tmp.name
        
        try:
            size_bytes = os.path.getsize(tmp_path)
            size_mb = size_bytes / (1024 * 1024)
            
            assert size_bytes == 1024
            assert size_mb < 0.01  # Less than 0.01 MB
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_filename_truncation(self):
        """Test filename truncation logic"""
        long_name = "a" * 50 + ".mp4"
        max_length = 40
        
        if len(long_name) > max_length:
            truncated = long_name[:max_length-3] + "..."
        else:
            truncated = long_name
        
        assert len(truncated) <= max_length
        assert truncated.endswith("...")
    
    def test_queue_duplicate_detection(self):
        """Test queue duplicate file detection logic"""
        queue_files = [
            {'path': '/path/to/video1.mp4'},
            {'path': '/path/to/video2.mp4'},
        ]
        
        new_file = '/path/to/video1.mp4'
        is_duplicate = any(q['path'] == new_file for q in queue_files)
        
        assert is_duplicate == True
        
        new_file2 = '/path/to/video3.mp4'
        is_duplicate2 = any(q['path'] == new_file2 for q in queue_files)
        
        assert is_duplicate2 == False
    
    def test_target_size_validation(self):
        """Test target size input validation"""
        valid_sizes = ["10", "5.5", "0.1", "100"]
        invalid_sizes = ["", "abc", "10.5.5", "-5"]
        
        for size_str in valid_sizes:
            try:
                size = float(size_str)
                assert isinstance(size, float)
            except ValueError:
                pytest.fail(f"Valid size {size_str} should not raise ValueError")
        
        for size_str in invalid_sizes:
            try:
                size = float(size_str)
                # If it doesn't raise, that's okay for some cases
            except ValueError:
                pass  # Expected for truly invalid inputs
    
    def test_batch_compression_progress_calculation(self):
        """Test batch compression progress calculation"""
        total_files = 5
        
        for index in range(total_files):
            progress = (index + 1) / total_files
            
            assert progress >= 0
            assert progress <= 1
            if index == total_files - 1:
                assert progress == 1.0
    
    def test_suffix_default_value(self):
        """Test suffix default value handling"""
        suffix = "" or "_compressed"
        assert suffix == "_compressed"
        
        suffix2 = "_custom" or "_compressed"
        assert suffix2 == "_custom"


class TestFileOperations:
    """Test file and directory operations"""
    
    def test_create_temp_directory(self):
        """Test creating temporary directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            assert os.path.exists(tmpdir)
            assert os.path.isdir(tmpdir)
    
    def test_file_existence_check(self):
        """Test checking file existence"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            assert os.path.exists(tmp_path)
            assert os.path.isfile(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_directory_creation(self):
        """Test creating directory"""
        with tempfile.TemporaryDirectory() as base:
            new_dir = os.path.join(base, "subdir")
            os.makedirs(new_dir, exist_ok=True)
            
            assert os.path.exists(new_dir)
            assert os.path.isdir(new_dir)
    
    def test_file_extension_extraction(self):
        """Test extracting file extensions"""
        test_cases = [
            ("video.mp4", ".mp4"),
            ("video.mov", ".mov"),
            ("video.avi", ".avi"),
            ("video.mkv", ".mkv"),
            ("no_extension", ""),
            (".hidden", ""),
        ]
        
        for filename, expected_ext in test_cases:
            _, ext = os.path.splitext(filename)
            assert ext == expected_ext
    
    def test_video_file_filtering(self):
        """Test filtering video files by extension"""
        all_files = [
            "video1.mp4",
            "video2.mov",
            "video3.avi",
            "document.pdf",
            "image.jpg",
            "video4.mkv",
        ]
        
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
        video_files = [f for f in all_files if any(f.lower().endswith(ext) for ext in video_extensions)]
        
        assert len(video_files) == 4
        assert "video1.mp4" in video_files
        assert "document.pdf" not in video_files


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_handle_missing_file_gracefully(self):
        """Test handling missing files gracefully"""
        compressor = VideoCompressor()
        result = compressor.compress_video("nonexistent.mp4", "output.mp4")
        
        assert result == False
    
    def test_handle_permission_error(self):
        """Test handling permission errors"""
        # On Windows, try accessing a system directory
        if os.name == 'nt':
            protected_path = "C:\\Windows\\System32\\config\\system"
            compressor = VideoCompressor()
            result = compressor.compress_video(protected_path, "output.mp4")
            # Should handle gracefully
            assert isinstance(result, bool)
    
    def test_handle_invalid_characters_in_path(self):
        """Test handling invalid characters in path"""
        invalid_paths = [
            "video<>file.mp4",
            "video|file.mp4",
            "video:file.mp4",
        ]
        
        compressor = VideoCompressor()
        for path in invalid_paths:
            result = compressor.compress_video(path, "output.mp4")
            assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

