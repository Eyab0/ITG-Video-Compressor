import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock, call

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from compressor import VideoCompressor


class TestVideoCompressor:
    """Comprehensive test suite for VideoCompressor class"""
    
    # ========== Initialization Tests ==========
    
    def test_init_default_values(self):
        """Test VideoCompressor initialization with default values"""
        compressor = VideoCompressor()
        assert compressor.target_size_mb == 9
        assert compressor.safe_bitrate_kbps == 800
        assert compressor.max_size_bytes == 9 * 1024 * 1024
    
    def test_init_custom_values(self):
        """Test VideoCompressor initialization with custom values"""
        compressor = VideoCompressor(target_size_mb=10, safe_bitrate_kbps=1000)
        assert compressor.target_size_mb == 10
        assert compressor.safe_bitrate_kbps == 1000
        assert compressor.max_size_bytes == 10 * 1024 * 1024
    
    def test_init_zero_size(self):
        """Test initialization with zero target size"""
        compressor = VideoCompressor(target_size_mb=0)
        assert compressor.target_size_mb == 0
        assert compressor.max_size_bytes == 0
    
    def test_init_negative_size(self):
        """Test initialization with negative target size"""
        compressor = VideoCompressor(target_size_mb=-5)
        assert compressor.target_size_mb == -5
        assert compressor.max_size_bytes == -5 * 1024 * 1024
    
    def test_init_very_large_size(self):
        """Test initialization with very large target size"""
        compressor = VideoCompressor(target_size_mb=1000)
        assert compressor.target_size_mb == 1000
        assert compressor.max_size_bytes == 1000 * 1024 * 1024
    
    def test_init_zero_bitrate(self):
        """Test initialization with zero bitrate"""
        compressor = VideoCompressor(safe_bitrate_kbps=0)
        assert compressor.safe_bitrate_kbps == 0
    
    def test_init_high_bitrate(self):
        """Test initialization with high bitrate"""
        compressor = VideoCompressor(safe_bitrate_kbps=5000)
        assert compressor.safe_bitrate_kbps == 5000
    
    # ========== Compression Tests ==========
    
    def test_compress_video_invalid_path(self):
        """Test compression with invalid input path"""
        compressor = VideoCompressor()
        result = compressor.compress_video("nonexistent_video.mp4", "output.mp4")
        assert result == False
    
    def test_compress_video_nonexistent_output_dir(self):
        """Test compression with nonexistent output directory"""
        compressor = VideoCompressor()
        result = compressor.compress_video("test.mp4", "/nonexistent/path/output.mp4")
        assert isinstance(result, bool)
    
    def test_compress_video_empty_path(self):
        """Test compression with empty path"""
        compressor = VideoCompressor()
        result = compressor.compress_video("", "output.mp4")
        assert result == False
    
    def test_compress_video_none_path(self):
        """Test compression with None path"""
        compressor = VideoCompressor()
        # None path will raise TypeError, which is expected behavior
        with pytest.raises(TypeError):
            compressor.compress_video(None, "output.mp4")
    
    @patch('compressor.subprocess.run')
    @patch('compressor.VideoFileClip')
    @patch('os.path.getsize')
    @patch('os.path.exists')
    def test_compress_video_success(self, mock_exists, mock_getsize, mock_videofileclip, mock_subprocess):
        """Test successful video compression"""
        # Setup mocks
        mock_exists.return_value = True
        mock_getsize.return_value = 5 * 1024 * 1024  # 5 MB
        mock_clip = MagicMock()
        mock_clip.duration = 60.0  # 60 seconds video
        mock_videofileclip.return_value = mock_clip
        # Mock ffprobe to fail (will use MoviePy instead)
        mock_subprocess.side_effect = FileNotFoundError()
        
        compressor = VideoCompressor(target_size_mb=10)
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            input_path = tmp.name
            output_path = input_path.replace('.mp4', '_compressed.mp4')
        
        try:
            # Mock output file creation
            with patch('os.path.exists') as mock_output_exists:
                mock_output_exists.side_effect = lambda p: p == input_path or p == output_path
                result = compressor.compress_video(input_path, output_path)
            
            assert result == True
            mock_videofileclip.assert_called()
            mock_clip.write_videofile.assert_called_once()
            mock_clip.close.assert_called()
            
            # Verify write_videofile parameters
            call_args = mock_clip.write_videofile.call_args
            assert call_args[0][0] == output_path
            assert call_args[1]['codec'] == 'libx264'
            assert call_args[1]['audio_codec'] == 'aac'
            assert 'bitrate' in call_args[1]  # Bitrate is now calculated dynamically
            assert call_args[1]['threads'] == 4
            assert call_args[1]['preset'] == 'medium'  # Changed from ultrafast
        finally:
            if os.path.exists(input_path):
                os.unlink(input_path)
    
    @patch('compressor.subprocess.run')
    @patch('compressor.VideoFileClip')
    @patch('os.path.getsize')
    @patch('os.path.exists')
    def test_compress_video_size_warning(self, mock_exists, mock_getsize, mock_videofileclip, mock_subprocess):
        """Test compression when output exceeds target size"""
        mock_exists.return_value = True
        mock_clip = MagicMock()
        mock_clip.duration = 60.0  # 60 seconds video
        mock_videofileclip.return_value = mock_clip
        # Mock ffprobe to fail
        mock_subprocess.side_effect = FileNotFoundError()
        # First call for input file size, second for output file size (15 MB)
        mock_getsize.side_effect = [5 * 1024 * 1024, 15 * 1024 * 1024]
        
        compressor = VideoCompressor(target_size_mb=10)
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            input_path = tmp.name
            output_path = input_path.replace('.mp4', '_compressed.mp4')
        
        try:
            # Mock output file creation
            with patch('os.path.exists') as mock_output_exists:
                mock_output_exists.side_effect = lambda p: p == input_path or p == output_path
                result = compressor.compress_video(input_path, output_path)
            assert result == True
            assert mock_getsize.call_count >= 1
        finally:
            if os.path.exists(input_path):
                os.unlink(input_path)
    
    @patch('compressor.VideoFileClip')
    def test_compress_video_exception_handling(self, mock_videofileclip):
        """Test compression error handling"""
        mock_videofileclip.side_effect = Exception("Video processing error")
        
        compressor = VideoCompressor()
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            input_path = tmp.name
            output_path = input_path.replace('.mp4', '_compressed.mp4')
        
        try:
            result = compressor.compress_video(input_path, output_path)
            assert result == False
        finally:
            if os.path.exists(input_path):
                os.unlink(input_path)
    
    @patch('compressor.subprocess.run')
    @patch('compressor.VideoFileClip')
    @patch('os.path.getsize')
    @patch('os.path.exists')
    def test_compress_video_custom_bitrate(self, mock_exists, mock_getsize, mock_videofileclip, mock_subprocess):
        """Test compression with custom bitrate (note: bitrate is now calculated dynamically)"""
        mock_exists.return_value = True
        mock_clip = MagicMock()
        mock_clip.duration = 60.0  # 60 seconds video
        mock_videofileclip.return_value = mock_clip
        mock_getsize.return_value = 5 * 1024 * 1024
        # Mock ffprobe to fail
        mock_subprocess.side_effect = FileNotFoundError()
        
        compressor = VideoCompressor(target_size_mb=10, safe_bitrate_kbps=1200)
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            input_path = tmp.name
            output_path = input_path.replace('.mp4', '_compressed.mp4')
        
        try:
            # Mock output file creation
            with patch('os.path.exists') as mock_output_exists:
                mock_output_exists.side_effect = lambda p: p == input_path or p == output_path
                result = compressor.compress_video(input_path, output_path)
            assert result == True
            
            # Bitrate is now calculated dynamically based on duration and target size
            # For 60s video and 10MB target: (10 * 8 * 1024 * 0.9) / 60 ≈ 1228 kbps
            call_args = mock_clip.write_videofile.call_args
            assert 'bitrate' in call_args[1]
            # Bitrate should be calculated, not use safe_bitrate_kbps directly
            bitrate_str = call_args[1]['bitrate']
            assert bitrate_str.endswith('k')
        finally:
            if os.path.exists(input_path):
                os.unlink(input_path)
    
    def test_compress_video_progress_callback_parameter(self):
        """Test that progress_callback parameter is accepted (even if not used)"""
        compressor = VideoCompressor()
        
        def dummy_callback(progress):
            pass
        
        # Should not raise error even if callback is provided
        result = compressor.compress_video("nonexistent.mp4", "output.mp4", progress_callback=dummy_callback)
        assert isinstance(result, bool)
    
    # ========== Path Handling Tests ==========
    
    def test_compress_video_relative_paths(self):
        """Test compression with relative paths"""
        compressor = VideoCompressor()
        result = compressor.compress_video("./relative/path/video.mp4", "./output.mp4")
        assert isinstance(result, bool)
    
    def test_compress_video_absolute_paths(self):
        """Test compression with absolute paths"""
        compressor = VideoCompressor()
        if os.name == 'nt':  # Windows
            result = compressor.compress_video("C:\\path\\to\\video.mp4", "C:\\path\\to\\output.mp4")
        else:  # Unix
            result = compressor.compress_video("/path/to/video.mp4", "/path/to/output.mp4")
        assert isinstance(result, bool)
    
    def test_compress_video_special_characters_in_path(self):
        """Test compression with special characters in path"""
        compressor = VideoCompressor()
        result = compressor.compress_video("video (1).mp4", "output (1).mp4")
        assert isinstance(result, bool)
    
    def test_compress_video_long_filename(self):
        """Test compression with very long filename"""
        compressor = VideoCompressor()
        long_name = "a" * 200 + ".mp4"
        result = compressor.compress_video(long_name, "output.mp4")
        assert isinstance(result, bool)
    
    # ========== Size Calculation Tests ==========
    
    def test_max_size_bytes_calculation(self):
        """Test max_size_bytes calculation for various sizes"""
        test_cases = [
            (1, 1024 * 1024),
            (10, 10 * 1024 * 1024),
            (100, 100 * 1024 * 1024),
            (0.5, int(0.5 * 1024 * 1024)),
        ]
        
        for size_mb, expected_bytes in test_cases:
            compressor = VideoCompressor(target_size_mb=size_mb)
            assert compressor.max_size_bytes == expected_bytes
    
    # ========== Edge Cases ==========
    
    def test_multiple_compressor_instances(self):
        """Test creating multiple compressor instances"""
        comp1 = VideoCompressor(target_size_mb=5)
        comp2 = VideoCompressor(target_size_mb=10)
        
        assert comp1.target_size_mb == 5
        assert comp2.target_size_mb == 10
        assert comp1.max_size_bytes != comp2.max_size_bytes
    
    def test_compress_same_input_output_path(self):
        """Test compression with same input and output path"""
        compressor = VideoCompressor()
        result = compressor.compress_video("video.mp4", "video.mp4")
        # Should handle gracefully (may fail or overwrite)
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
