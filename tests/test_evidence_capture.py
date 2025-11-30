"""
Tests for the Evidence Capture System.

Tests screenshot and screen recording capabilities for evidence gathering.
"""

import os
import shutil
import sys
import tempfile
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Initialize pygame before importing evidence_capture
import pygame

pygame.init()

from evidence_capture import EvidenceCapture


class TestEvidenceCaptureInitialization:
    """Tests for EvidenceCapture initialization."""

    def test_initialization_creates_instance(self):
        """Test that EvidenceCapture initializes correctly."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            assert evidence is not None
            assert evidence.is_recording is False
            assert evidence.recording_start_time == 0.0
            assert evidence.recording_frames == []
            assert evidence.last_frame_time == 0.0
            assert evidence.flash_alpha == 0
            assert evidence._screenshot_pending is False

    def test_initialization_sets_class_constants(self):
        """Test that class constants are set correctly."""
        assert EvidenceCapture.EVIDENCE_DIR == ".kiro/evidence"
        assert EvidenceCapture.SCREENSHOTS_DIR == ".kiro/evidence/screenshots"
        assert EvidenceCapture.RECORDINGS_DIR == ".kiro/evidence/recordings"
        assert EvidenceCapture.MAX_RECORDING_SECONDS == 60
        assert EvidenceCapture.RECORDING_FPS == 30
        assert EvidenceCapture.FLASH_DURATION == 0.15

    def test_ensure_directories_called_on_init(self):
        """Test that _ensure_directories is called during initialization."""
        with patch.object(EvidenceCapture, "_ensure_directories") as mock_ensure:
            EvidenceCapture()
            mock_ensure.assert_called_once()


class TestEvidenceCaptureDirectories:
    """Tests for directory management."""

    def test_ensure_directories_creates_folders(self):
        """Test that _ensure_directories creates the required folders."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Temporarily override the class constants
            original_screenshots = EvidenceCapture.SCREENSHOTS_DIR
            original_recordings = EvidenceCapture.RECORDINGS_DIR

            try:
                EvidenceCapture.SCREENSHOTS_DIR = os.path.join(tmpdir, "screenshots")
                EvidenceCapture.RECORDINGS_DIR = os.path.join(tmpdir, "recordings")

                evidence = EvidenceCapture()

                assert os.path.exists(EvidenceCapture.SCREENSHOTS_DIR)
                assert os.path.exists(EvidenceCapture.RECORDINGS_DIR)
            finally:
                EvidenceCapture.SCREENSHOTS_DIR = original_screenshots
                EvidenceCapture.RECORDINGS_DIR = original_recordings


class TestFilenameGeneration:
    """Tests for filename generation."""

    def test_generate_filename_format(self):
        """Test that generated filenames follow the expected format."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            filename = evidence._generate_filename("png")

            assert filename.startswith("ZB_")
            assert filename.endswith(".png")
            # Format: ZB_YYYYMMDD_HHMMSS.ext
            assert len(filename) == 22  # ZB_ + 8 + _ + 6 + .png

    def test_generate_filename_different_extensions(self):
        """Test filename generation with different extensions."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            png_filename = evidence._generate_filename("png")
            gif_filename = evidence._generate_filename("gif")

            assert png_filename.endswith(".png")
            assert gif_filename.endswith(".gif")


class TestScreenshotCapture:
    """Tests for screenshot functionality."""

    def test_take_screenshot_success(self):
        """Test successful screenshot capture."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            # Create a mock screen surface with get_size method
            mock_screen = Mock(spec=pygame.Surface)
            mock_screen.get_size.return_value = (1280, 720)

            with patch("pygame.image.save") as mock_save:
                with patch("evidence_capture.pygame.Surface") as mock_surface_class:
                    mock_rgb_surface = Mock()
                    mock_surface_class.return_value = mock_rgb_surface
                    with patch.object(
                        evidence, "_generate_filename", return_value="ZB_test.png"
                    ):
                        result = evidence.take_screenshot(mock_screen)

                        assert result == "ZB_test.png"
                        assert evidence.flash_alpha == 255
                        mock_save.assert_called_once()

    def test_take_screenshot_triggers_flash(self):
        """Test that taking a screenshot triggers the flash effect."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            mock_screen = Mock(spec=pygame.Surface)
            mock_screen.get_size.return_value = (1280, 720)

            assert evidence.flash_alpha == 0

            with patch("pygame.image.save"):
                with patch("evidence_capture.pygame.Surface") as mock_surface_class:
                    mock_rgb_surface = Mock()
                    mock_surface_class.return_value = mock_rgb_surface
                    evidence.take_screenshot(mock_screen)

            assert evidence.flash_alpha == 255

    def test_take_screenshot_failure_returns_none(self):
        """Test that screenshot failure returns None."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            mock_screen = Mock(spec=pygame.Surface)
            mock_screen.get_size.return_value = (1280, 720)

            with patch(
                "evidence_capture.pygame.Surface",
                side_effect=Exception("Surface failed"),
            ):
                result = evidence.take_screenshot(mock_screen)

                assert result is None

    def test_take_screenshot_converts_to_rgb(self):
        """Test that screenshot converts screen to RGB surface before saving."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            mock_screen = Mock(spec=pygame.Surface)
            mock_screen.get_size.return_value = (1280, 720)

            with patch("pygame.image.save") as mock_save:
                with patch("evidence_capture.pygame.Surface") as mock_surface_class:
                    mock_rgb_surface = Mock()
                    mock_surface_class.return_value = mock_rgb_surface
                    with patch.object(
                        evidence, "_generate_filename", return_value="ZB_test.png"
                    ):
                        evidence.take_screenshot(mock_screen)

                        # Verify RGB surface was created with screen dimensions
                        mock_surface_class.assert_called_once_with((1280, 720))
                        # Verify black background was filled
                        mock_rgb_surface.fill.assert_called_once_with((0, 0, 0))
                        # Verify screen was blitted onto RGB surface
                        mock_rgb_surface.blit.assert_called_once_with(
                            mock_screen, (0, 0)
                        )
                        # Verify RGB surface was saved (not original screen)
                        mock_save.assert_called_once()
                        saved_surface = mock_save.call_args[0][0]
                        assert saved_surface == mock_rgb_surface


class TestDeferredScreenshot:
    """Tests for deferred screenshot functionality."""

    def test_request_screenshot_sets_pending_flag(self):
        """Test that request_screenshot sets the pending flag."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            assert evidence._screenshot_pending is False

            evidence.request_screenshot()

            assert evidence._screenshot_pending is True

    def test_process_pending_screenshot_when_not_pending(self):
        """Test that process_pending_screenshot returns None when no screenshot pending."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            mock_screen = Mock(spec=pygame.Surface)

            assert evidence._screenshot_pending is False

            result = evidence.process_pending_screenshot(mock_screen)

            assert result is None
            assert evidence._screenshot_pending is False

    def test_process_pending_screenshot_when_pending(self):
        """Test that process_pending_screenshot takes screenshot when pending."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            mock_screen = Mock(spec=pygame.Surface)
            mock_screen.get_size.return_value = (1280, 720)

            # Request a screenshot
            evidence.request_screenshot()
            assert evidence._screenshot_pending is True

            with patch("evidence_capture.pygame.image.save"):
                with patch("evidence_capture.pygame.Surface") as mock_surface_class:
                    mock_rgb_surface = Mock()
                    mock_surface_class.return_value = mock_rgb_surface
                    with patch.object(
                        evidence, "_generate_filename", return_value="ZB_test.png"
                    ):
                        result = evidence.process_pending_screenshot(mock_screen)

                        assert result == "ZB_test.png"
                        assert evidence._screenshot_pending is False
                        assert evidence.flash_alpha == 255

    def test_process_pending_screenshot_clears_flag_on_failure(self):
        """Test that process_pending_screenshot clears flag even on failure."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            mock_screen = Mock(spec=pygame.Surface)
            mock_screen.get_size.return_value = (1280, 720)

            evidence.request_screenshot()
            assert evidence._screenshot_pending is True

            with patch(
                "evidence_capture.pygame.Surface",
                side_effect=Exception("Surface failed"),
            ):
                result = evidence.process_pending_screenshot(mock_screen)

                assert result is None
                assert evidence._screenshot_pending is False

    def test_deferred_screenshot_workflow(self):
        """Test complete deferred screenshot workflow."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            mock_screen = Mock(spec=pygame.Surface)
            mock_screen.get_size.return_value = (1280, 720)

            # Step 1: Request screenshot (during input handling)
            evidence.request_screenshot()
            assert evidence._screenshot_pending is True
            assert evidence.flash_alpha == 0  # No flash yet

            # Step 2: Process pending screenshot (after render completes)
            with patch("evidence_capture.pygame.image.save"):
                with patch("evidence_capture.pygame.Surface") as mock_surface_class:
                    mock_rgb_surface = Mock()
                    mock_surface_class.return_value = mock_rgb_surface
                    with patch.object(
                        evidence, "_generate_filename", return_value="ZB_deferred.png"
                    ):
                        result = evidence.process_pending_screenshot(mock_screen)

                        assert result == "ZB_deferred.png"
                        assert evidence._screenshot_pending is False
                        assert evidence.flash_alpha == 255  # Flash triggered

    def test_multiple_request_screenshot_calls(self):
        """Test that multiple request_screenshot calls don't cause issues."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            # Multiple requests should just keep the flag True
            evidence.request_screenshot()
            evidence.request_screenshot()
            evidence.request_screenshot()

            assert evidence._screenshot_pending is True


class TestRecordingControl:
    """Tests for recording start/stop functionality."""

    def test_start_recording(self):
        """Test starting a recording."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            evidence.start_recording(10.0)

            assert evidence.is_recording is True
            assert evidence.recording_start_time == 10.0
            assert evidence.recording_frames == []
            assert evidence.last_frame_time == 10.0

    def test_start_recording_when_already_recording(self):
        """Test that starting recording when already recording does nothing."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            evidence.start_recording(10.0)
            evidence.start_recording(20.0)  # Should be ignored

            assert evidence.recording_start_time == 10.0  # Original time preserved

    def test_stop_recording_when_not_recording(self):
        """Test stopping recording when not recording returns None."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            result = evidence.stop_recording()

            assert result is None

    def test_stop_recording_with_no_frames(self):
        """Test stopping recording with no frames captured."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            evidence.is_recording = True
            evidence.recording_frames = []

            result = evidence.stop_recording()

            assert result is None
            assert evidence.is_recording is False

    def test_toggle_recording_starts_when_not_recording(self):
        """Test toggle_recording starts recording when not recording."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            result = evidence.toggle_recording(10.0)

            assert result is None  # No filename returned when starting
            assert evidence.is_recording is True

    def test_toggle_recording_stops_when_recording(self):
        """Test toggle_recording stops recording when recording."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            evidence.is_recording = True
            evidence.recording_frames = []  # No frames

            result = evidence.toggle_recording(20.0)

            assert evidence.is_recording is False


class TestFrameCapture:
    """Tests for frame capture during recording."""

    def test_capture_frame_when_not_recording(self):
        """Test that capture_frame does nothing when not recording."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            mock_screen = Mock(spec=pygame.Surface)

            evidence.capture_frame(mock_screen, 10.0)

            assert len(evidence.recording_frames) == 0

    def test_capture_frame_respects_fps_limit(self):
        """Test that frames are captured at the correct FPS."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            evidence.is_recording = True
            evidence.recording_start_time = 0.0
            evidence.last_frame_time = 0.0

            mock_screen = Mock(spec=pygame.Surface)
            mock_screen.copy.return_value = Mock(spec=pygame.Surface)

            # First frame should be captured (time >= last_frame_time + interval)
            # At time 0.0, last_frame_time is 0.0, interval is ~0.033
            # 0.0 - 0.0 = 0.0 which is NOT >= 0.033, so first frame at 0.0 won't capture
            # We need to start at a time that satisfies the condition
            evidence.capture_frame(mock_screen, 0.034)  # First capture
            # This should NOT be captured (too soon after 0.034)
            evidence.capture_frame(mock_screen, 0.05)
            # This should be captured (enough time passed: 0.07 - 0.034 = 0.036 > 0.033)
            evidence.capture_frame(mock_screen, 0.07)

            assert len(evidence.recording_frames) == 2

    def test_capture_frame_auto_stops_at_max_duration(self):
        """Test that recording auto-stops at max duration."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            evidence.is_recording = True
            evidence.recording_start_time = 0.0
            evidence.last_frame_time = 0.0

            mock_screen = Mock(spec=pygame.Surface)

            # Simulate time past max duration
            evidence.capture_frame(mock_screen, 61.0)  # > 60 seconds

            assert evidence.is_recording is False


class TestRecordingDuration:
    """Tests for recording duration calculation."""

    def test_get_recording_duration_when_not_recording(self):
        """Test duration is 0 when not recording."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            duration = evidence.get_recording_duration(100.0)

            assert duration == 0.0

    def test_get_recording_duration_when_recording(self):
        """Test duration calculation when recording."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            evidence.is_recording = True
            evidence.recording_start_time = 10.0

            duration = evidence.get_recording_duration(25.0)

            assert duration == 15.0


class TestFlashEffect:
    """Tests for screenshot flash effect."""

    def test_update_flash_decreases_alpha(self):
        """Test that update_flash decreases flash_alpha over time."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            evidence.flash_alpha = 255

            evidence.update_flash(0.05)  # 50ms

            assert evidence.flash_alpha < 255
            assert evidence.flash_alpha > 0

    def test_update_flash_reaches_zero(self):
        """Test that flash_alpha reaches zero after FLASH_DURATION."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            evidence.flash_alpha = 255

            # Update for longer than FLASH_DURATION
            evidence.update_flash(0.2)

            assert evidence.flash_alpha == 0

    def test_update_flash_does_nothing_when_zero(self):
        """Test that update_flash does nothing when alpha is already 0."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            evidence.flash_alpha = 0

            evidence.update_flash(0.1)

            assert evidence.flash_alpha == 0


class TestRenderFlash:
    """Tests for flash rendering."""

    def test_render_flash_when_alpha_positive(self):
        """Test that render_flash draws overlay when alpha > 0."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            evidence.flash_alpha = 128

            mock_screen = Mock(spec=pygame.Surface)
            mock_screen.get_size.return_value = (1280, 720)

            with patch("pygame.Surface") as mock_surface_class:
                mock_flash_surface = Mock()
                mock_surface_class.return_value = mock_flash_surface

                evidence.render_flash(mock_screen)

                mock_flash_surface.fill.assert_called_once_with((255, 255, 255))
                mock_flash_surface.set_alpha.assert_called_once_with(128)
                mock_screen.blit.assert_called_once()

    def test_render_flash_does_nothing_when_alpha_zero(self):
        """Test that render_flash does nothing when alpha is 0."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            evidence.flash_alpha = 0

            mock_screen = Mock(spec=pygame.Surface)

            evidence.render_flash(mock_screen)

            mock_screen.blit.assert_not_called()


class TestRenderRecordingIndicator:
    """Tests for recording indicator rendering."""

    def test_render_recording_indicator_when_not_recording(self):
        """Test that indicator is not rendered when not recording."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            evidence.is_recording = False

            mock_screen = Mock(spec=pygame.Surface)

            evidence.render_recording_indicator(mock_screen, 10.0)

            # Should not draw anything
            mock_screen.blit.assert_not_called()

    def test_render_recording_indicator_when_recording(self):
        """Test that indicator is rendered when recording."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()
            evidence.is_recording = True
            evidence.recording_start_time = 0.0

            mock_screen = Mock(spec=pygame.Surface)
            mock_screen.get_width.return_value = 1280

            with patch("pygame.draw.circle"):
                with patch("pygame.font.Font") as mock_font_class:
                    mock_font = Mock()
                    mock_font.render.return_value = Mock(spec=pygame.Surface)
                    mock_font_class.return_value = mock_font

                    evidence.render_recording_indicator(mock_screen, 10.0)

                    # Should render REC text and timer
                    assert mock_font.render.call_count >= 2


class TestSaveRecording:
    """Tests for saving recordings."""

    def test_save_recording_clears_frames(self):
        """Test that _save_recording clears frames after saving."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            # Create mock frames
            mock_frame = Mock(spec=pygame.Surface)
            mock_frame.get_size.return_value = (100, 100)
            evidence.recording_frames = [mock_frame]

            with patch("pygame.image.tostring", return_value=b"\x00" * 30000):
                with patch.object(
                    evidence, "_save_frames_as_pngs", return_value="test_folder/"
                ):
                    evidence._save_recording()

                    assert evidence.recording_frames == []


class TestSaveFramesAsPngs:
    """Tests for PNG fallback saving."""

    def test_save_frames_as_pngs_creates_folder(self):
        """Test that _save_frames_as_pngs creates a folder for frames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_recordings = EvidenceCapture.RECORDINGS_DIR

            try:
                EvidenceCapture.RECORDINGS_DIR = tmpdir

                with patch.object(EvidenceCapture, "_ensure_directories"):
                    evidence = EvidenceCapture()

                    mock_frame = Mock(spec=pygame.Surface)
                    evidence.recording_frames = [mock_frame]

                    with patch("pygame.image.save"):
                        result = evidence._save_frames_as_pngs()

                        assert result.startswith("ZB_")
                        assert result.endswith("/")
            finally:
                EvidenceCapture.RECORDINGS_DIR = original_recordings


class TestIntegration:
    """Integration tests for the evidence capture system."""

    def test_full_screenshot_workflow(self):
        """Test complete screenshot workflow."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            mock_screen = Mock(spec=pygame.Surface)
            mock_screen.get_size.return_value = (1280, 720)

            # Take screenshot
            with patch("evidence_capture.pygame.image.save"):
                with patch("evidence_capture.pygame.Surface") as mock_surface_class:
                    mock_rgb_surface = Mock()
                    mock_surface_class.return_value = mock_rgb_surface
                    filename = evidence.take_screenshot(mock_screen)

                    assert filename is not None
                    assert evidence.flash_alpha == 255

            # Update flash
            evidence.update_flash(0.2)
            assert evidence.flash_alpha == 0

    def test_full_recording_workflow(self):
        """Test complete recording workflow."""
        with patch.object(EvidenceCapture, "_ensure_directories"):
            evidence = EvidenceCapture()

            mock_screen = Mock(spec=pygame.Surface)
            mock_screen.copy.return_value = Mock(spec=pygame.Surface)

            # Start recording
            result = evidence.toggle_recording(0.0)
            assert result is None
            assert evidence.is_recording is True

            # Capture some frames - need to space them at least 1/30 seconds apart
            # Frame interval is 1/30 = 0.0333 seconds
            # Start at 0.034 to ensure first frame captures (0.034 - 0.0 >= 0.033)
            for i in range(5):
                evidence.capture_frame(mock_screen, 0.034 + i * 0.034)

            assert len(evidence.recording_frames) == 5

            # Stop recording
            with patch.object(evidence, "_save_recording", return_value="test.gif"):
                result = evidence.toggle_recording(1.0)

                assert evidence.is_recording is False


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
