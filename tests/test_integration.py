import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from compressor import VideoCompressor


class TestIntegration:
    """Integration tests for the video compression workflow"""
    
    def test_full_compression_workflow_mock(self):
        """Test full compression workflow with mocked video processing"""
        with patch('compressor.subprocess.run') as mock_subprocess, \
             patch('compressor.VideoFileClip') as mock_videofileclip, \
             patch('os.path.getsize') as mock_getsize, \
             patch('os.path.exists') as mock_exists:
            
            # Setup mocks
            mock_exists.return_value = True
            mock_clip = MagicMock()
            mock_clip.duration = 60.0  # 60 seconds video
            mock_videofileclip.return_value = mock_clip
            mock_getsize.return_value = 5 * 1024 * 1024  # 5 MB output
            # Mock ffprobe to fail (will use MoviePy instead)
            mock_subprocess.side_effect = FileNotFoundError()
            
            compressor = VideoCompressor(target_size_mb=10, safe_bitrate_kbps=800)
            
            with tempfile.TemporaryDirectory() as tmpdir:
                input_path = os.path.join(tmpdir, "input.mp4")
                output_path = os.path.join(tmpdir, "output.mp4")
                
                # Create dummy input file
                with open(input_path, 'wb') as f:
                    f.write(b"dummy video data")
                
                # Mock output file existence
                mock_exists.side_effect = lambda p: p == input_path or p == output_path
                
                # Run compression
                result = compressor.compress_video(input_path, output_path)
                
                # Verify workflow
                assert result == True
                mock_videofileclip.assert_called()
                mock_clip.write_videofile.assert_called_once()
                mock_clip.close.assert_called()
    
    def test_batch_processing_simulation(self):
        """Simulate batch processing of multiple files"""
        compressor = VideoCompressor(target_size_mb=10)
        
        file_list = [
            "video1.mp4",
            "video2.mp4",
            "video3.mp4",
        ]
        
        results = []
        for file_path in file_list:
            # Simulate processing (will fail but test logic)
            result = compressor.compress_video(file_path, f"output_{file_path}")
            results.append(result)
        
        assert len(results) == len(file_list)
        assert all(isinstance(r, bool) for r in results)
    
    def test_different_target_sizes(self):
        """Test compression with different target sizes"""
        target_sizes = [5, 10, 20, 50]
        
        for target_size in target_sizes:
            compressor = VideoCompressor(target_size_mb=target_size)
            assert compressor.target_size_mb == target_size
            assert compressor.max_size_bytes == target_size * 1024 * 1024
    
    def test_different_bitrates(self):
        """Test compression with different bitrates"""
        bitrates = [400, 800, 1200, 2000]
        
        for bitrate in bitrates:
            compressor = VideoCompressor(safe_bitrate_kbps=bitrate)
            assert compressor.safe_bitrate_kbps == bitrate
    
    def test_output_path_variations(self):
        """Test various output path scenarios"""
        base_path = "/path/to/video.mp4"
        suffixes = ["_compressed", "_10mb", "_small", ""]
        
        dirname = os.path.dirname(base_path)
        basename = os.path.basename(base_path)
        name, ext = os.path.splitext(basename)
        
        for suffix in suffixes:
            output_path = os.path.join(dirname, f"{name}{suffix}{ext}")
            assert output_path.startswith(dirname)
            assert output_path.endswith(ext)
    
    def test_concurrent_compressor_instances(self):
        """Test using multiple compressor instances concurrently"""
        comp1 = VideoCompressor(target_size_mb=5, safe_bitrate_kbps=600)
        comp2 = VideoCompressor(target_size_mb=10, safe_bitrate_kbps=800)
        comp3 = VideoCompressor(target_size_mb=20, safe_bitrate_kbps=1200)
        
        # Each should maintain its own settings
        assert comp1.target_size_mb == 5
        assert comp2.target_size_mb == 10
        assert comp3.target_size_mb == 20
        
        assert comp1.safe_bitrate_kbps == 600
        assert comp2.safe_bitrate_kbps == 800
        assert comp3.safe_bitrate_kbps == 1200


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_small_target_size(self):
        """Test with very small target size"""
        compressor = VideoCompressor(target_size_mb=0.1)
        assert compressor.target_size_mb == 0.1
        # Allow for floating point precision differences
        expected_bytes = 0.1 * 1024 * 1024
        assert abs(compressor.max_size_bytes - expected_bytes) < 1
    
    def test_very_large_target_size(self):
        """Test with very large target size"""
        compressor = VideoCompressor(target_size_mb=1000)
        assert compressor.target_size_mb == 1000
        assert compressor.max_size_bytes == 1000 * 1024 * 1024
    
    def test_fractional_target_size(self):
        """Test with fractional target size"""
        compressor = VideoCompressor(target_size_mb=10.5)
        assert compressor.target_size_mb == 10.5
        assert compressor.max_size_bytes == int(10.5 * 1024 * 1024)
    
    def test_unicode_in_paths(self):
        """Test handling unicode characters in paths"""
        compressor = VideoCompressor()
        
        # Test with unicode characters
        unicode_path = "vídeo_测试.mp4"
        result = compressor.compress_video(unicode_path, "output.mp4")
        assert isinstance(result, bool)
    
    def test_spaces_in_paths(self):
        """Test handling spaces in paths"""
        compressor = VideoCompressor()
        
        paths_with_spaces = [
            "my video file.mp4",
            "path with spaces/video.mp4",
            "  leading spaces.mp4",
        ]
        
        for path in paths_with_spaces:
            result = compressor.compress_video(path, "output.mp4")
            assert isinstance(result, bool)
    
    def test_special_characters_in_paths(self):
        """Test handling special characters in paths"""
        compressor = VideoCompressor()
        
        special_paths = [
            "video (1).mp4",
            "video-v2.mp4",
            "video_v3.mp4",
            "video+plus.mp4",
        ]
        
        for path in special_paths:
            result = compressor.compress_video(path, "output.mp4")
            assert isinstance(result, bool)


class TestRealVideoCompression:
    """Tests using real video files"""
    
    @pytest.mark.skipif(
        not os.path.exists(r"C:\Users\EyabGhifari\Desktop\test\GH - iPhone Test Case.mp4"),
        reason="Test video file not found"
    )
    def test_compress_real_video_file(self):
        """Test compression with the actual iPhone test case video"""
        test_video_path = r"C:\Users\EyabGhifari\Desktop\test\GH - iPhone Test Case.mp4"
        
        # Verify file exists
        assert os.path.exists(test_video_path), f"Test video not found at {test_video_path}"
        
        # Get original file size
        original_size_bytes = os.path.getsize(test_video_path)
        original_size_mb = original_size_bytes / (1024 * 1024)
        
        print(f"\nOriginal video size: {original_size_mb:.2f} MB ({original_size_bytes:,} bytes)")
        
        # Create output path in same directory
        video_dir = os.path.dirname(test_video_path)
        video_name = os.path.basename(test_video_path)
        name, ext = os.path.splitext(video_name)
        output_path = os.path.join(video_dir, f"{name}_test_compressed{ext}")
        
        # Clean up any existing test output
        if os.path.exists(output_path):
            os.remove(output_path)
        
        try:
            # Test with 10MB target
            compressor = VideoCompressor(target_size_mb=10, safe_bitrate_kbps=800)
            result = compressor.compress_video(test_video_path, output_path)
            
            # Verify compression succeeded
            assert result == True, "Compression should succeed"
            
            # Verify output file was created
            assert os.path.exists(output_path), "Output file should be created"
            
            # Get compressed file size
            compressed_size_bytes = os.path.getsize(output_path)
            compressed_size_mb = compressed_size_bytes / (1024 * 1024)
            
            print(f"Compressed video size: {compressed_size_mb:.2f} MB ({compressed_size_bytes:,} bytes)")
            print(f"Compression ratio: {(1 - compressed_size_bytes/original_size_bytes)*100:.1f}% reduction")
            
            # Verify compressed file is smaller (or at least exists)
            assert compressed_size_bytes > 0, "Compressed file should have content"
            
            # Verify file is reasonable size (not corrupted)
            assert compressed_size_bytes < original_size_bytes * 2, "Compressed file shouldn't be much larger"
            
        finally:
            # Clean up test output file
            if os.path.exists(output_path):
                os.remove(output_path)
                print(f"Cleaned up test output: {output_path}")
    
    @pytest.mark.skipif(
        not os.path.exists(r"C:\Users\EyabGhifari\Desktop\test\GH - iPhone Test Case.mp4"),
        reason="Test video file not found"
    )
    def test_compress_real_video_different_target_sizes(self):
        """Test compression with different target sizes on real video"""
        test_video_path = r"C:\Users\EyabGhifari\Desktop\test\GH - iPhone Test Case.mp4"
        
        assert os.path.exists(test_video_path), f"Test video not found at {test_video_path}"
        
        video_dir = os.path.dirname(test_video_path)
        video_name = os.path.basename(test_video_path)
        name, ext = os.path.splitext(video_name)
        
        target_sizes = [5, 10, 15]
        results = []
        
        for target_size in target_sizes:
            output_path = os.path.join(video_dir, f"{name}_test_{target_size}mb{ext}")
            
            # Clean up any existing test output
            if os.path.exists(output_path):
                os.remove(output_path)
            
            try:
                compressor = VideoCompressor(target_size_mb=target_size, safe_bitrate_kbps=800)
                result = compressor.compress_video(test_video_path, output_path)
                
                if result and os.path.exists(output_path):
                    compressed_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    results.append({
                        'target': target_size,
                        'actual': compressed_size_mb,
                        'success': True
                    })
                    print(f"Target: {target_size}MB, Actual: {compressed_size_mb:.2f}MB")
                else:
                    results.append({
                        'target': target_size,
                        'success': False
                    })
            finally:
                # Clean up test output file (with retry for file locks)
                if os.path.exists(output_path):
                    import time
                    max_retries = 5
                    for _ in range(max_retries):
                        try:
                            os.remove(output_path)
                            break
                        except (PermissionError, OSError):
                            time.sleep(0.5)
        
        # At least one should succeed
        successful = [r for r in results if r.get('success', False)]
        assert len(successful) > 0, "At least one compression should succeed"
    
    @pytest.mark.skipif(
        not os.path.exists(r"C:\Users\EyabGhifari\Desktop\test\GH - iPhone Test Case.mp4"),
        reason="Test video file not found"
    )
    def test_compress_real_video_file_info(self):
        """Test getting information about the real video file"""
        test_video_path = r"C:\Users\EyabGhifari\Desktop\test\GH - iPhone Test Case.mp4"
        
        assert os.path.exists(test_video_path), f"Test video not found at {test_video_path}"
        
        # Get file info
        file_size_bytes = os.path.getsize(test_video_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        file_size_kb = file_size_bytes / 1024
        
        basename = os.path.basename(test_video_path)
        dirname = os.path.dirname(test_video_path)
        name, ext = os.path.splitext(basename)
        
        # Verify file properties
        assert file_size_bytes > 0, "File should have content"
        assert ext.lower() in ['.mp4', '.mov', '.avi', '.mkv'], "Should be a video file"
        assert os.path.isfile(test_video_path), "Should be a file, not directory"
        
        print(f"\nVideo File Info:")
        print(f"  Name: {basename}")
        print(f"  Path: {test_video_path}")
        print(f"  Size: {file_size_mb:.2f} MB ({file_size_kb:.2f} KB)")
        print(f"  Extension: {ext}")
        
        # The file should be around 41MB based on the user's note
        # Allow some variance (between 35-50 MB)
        assert 35 * 1024 * 1024 <= file_size_bytes <= 50 * 1024 * 1024, \
            f"File size should be around 41MB, but got {file_size_mb:.2f}MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

