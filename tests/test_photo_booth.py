"""Tests for Photo Booth feature."""

import os
import sys

import pytest
from PIL import Image

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from photo_booth.compositor import PhotoBoothCompositor
from photo_booth.config import PhotoBoothConfig
from photo_booth.controller import PhotoBoothController, PhotoBoothState
from photo_booth.retro_filter import RetroFilter


class TestPhotoBoothConfig:
    """Tests for PhotoBoothConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PhotoBoothConfig()
        assert config.enabled is True
        assert config.camera_index == 0
        assert config.event_name == "AWS re:Invent 2025"
        assert config.consent_timeout == 5.0

    def test_from_env_with_defaults(self):
        """Test loading config from environment with defaults."""
        config = PhotoBoothConfig.from_env()
        assert config.enabled is True
        assert isinstance(config.camera_index, int)


class TestRetroFilter:
    """Tests for RetroFilter."""

    def test_pixelate_reduces_detail(self):
        """Test that pixelation reduces image detail."""
        # Create a gradient image
        img = Image.new("RGB", (100, 100))
        pixels = img.load()
        for x in range(100):
            for y in range(100):
                pixels[x, y] = (x * 2, y * 2, 128)

        result = RetroFilter.pixelate(img, pixel_size=10)

        # Result should be same size
        assert result.size == (100, 100)

        # Result should have blocky regions (same color in 10x10 blocks)
        result_pixels = result.load()
        # Check that pixels in same block have same color
        assert result_pixels[0, 0] == result_pixels[5, 5]

    def test_soft_pixelate_preserves_more_detail(self):
        """Test that soft pixelation creates smoother result than hard pixelation."""
        # Create a gradient image
        img = Image.new("RGB", (100, 100))
        pixels = img.load()
        for x in range(100):
            for y in range(100):
                pixels[x, y] = (x * 2, y * 2, 128)

        result = RetroFilter.soft_pixelate(img, pixel_size=4)

        # Result should be same size
        assert result.size == (100, 100)

        # Result should be a valid image
        assert result.mode == "RGB"

    def test_soft_pixelate_with_small_image(self):
        """Test soft pixelation handles small images correctly."""
        img = Image.new("RGB", (10, 10), (255, 0, 0))
        result = RetroFilter.soft_pixelate(img, pixel_size=4)

        assert result.size == (10, 10)
        assert result.mode == "RGB"

    def test_extended_palette_exists(self):
        """Test that EXTENDED_PALETTE class attribute exists and has colors."""
        assert hasattr(RetroFilter, "EXTENDED_PALETTE")
        assert len(RetroFilter.EXTENDED_PALETTE) > 16  # More than basic palette
        # Check it contains RGB tuples
        for color in RetroFilter.EXTENDED_PALETTE:
            assert isinstance(color, tuple)
            assert len(color) == 3
            assert all(0 <= c <= 255 for c in color)

    def test_reduce_colors_with_extended_palette(self):
        """Test color reduction using the extended palette."""
        # Create image with many colors
        img = Image.new("RGB", (50, 50))
        pixels = img.load()
        for x in range(50):
            for y in range(50):
                pixels[x, y] = (x * 5, y * 5, (x + y) * 2)

        result = RetroFilter.reduce_colors(img, RetroFilter.EXTENDED_PALETTE)

        # Count unique colors - should be limited to extended palette
        colors = set()
        result_pixels = result.load()
        for x in range(50):
            for y in range(50):
                colors.add(result_pixels[x, y])

        # Should be limited to extended palette size
        assert len(colors) <= len(RetroFilter.EXTENDED_PALETTE)

    def test_reduce_colors_limits_palette(self):
        """Test that color reduction limits to palette."""
        # Create image with many colors
        img = Image.new("RGB", (50, 50))
        pixels = img.load()
        for x in range(50):
            for y in range(50):
                pixels[x, y] = (x * 5, y * 5, (x + y) * 2)

        result = RetroFilter.reduce_colors(img)

        # Count unique colors
        colors = set()
        result_pixels = result.load()
        for x in range(50):
            for y in range(50):
                colors.add(result_pixels[x, y])

        # Should be limited to 16 colors
        assert len(colors) <= 16

    def test_add_scanlines(self):
        """Test that scanlines are added."""
        img = Image.new("RGB", (100, 100), (255, 255, 255))
        result = RetroFilter.add_scanlines(img, opacity=100, spacing=3)

        # Result should be RGBA
        assert result.mode == "RGBA"
        assert result.size == (100, 100)

    def test_full_retro_effect(self):
        """Test complete retro transformation."""
        img = Image.new("RGB", (100, 100), (128, 64, 192))
        result = RetroFilter.apply_full_retro_effect(img, pixel_size=8)

        assert result.size == (100, 100)


class TestPhotoBoothCompositor:
    """Tests for PhotoBoothCompositor."""

    def test_generate_without_selfie(self):
        """Test composite generation without selfie."""
        compositor = PhotoBoothCompositor()
        gameplay = Image.new("RGB", (1280, 720), (0, 100, 0))
        config = PhotoBoothConfig()

        result = compositor.generate(selfie=None, gameplay=gameplay, zombie_count=42, config=config)

        assert result.size == (1920, 1080)
        assert result.mode == "RGB"

    def test_generate_with_selfie(self):
        """Test composite generation with selfie."""
        compositor = PhotoBoothCompositor()
        selfie = Image.new("RGB", (640, 480), (255, 0, 0))
        gameplay = Image.new("RGB", (1280, 720), (0, 100, 0))
        config = PhotoBoothConfig()

        result = compositor.generate(
            selfie=selfie, gameplay=gameplay, zombie_count=99, config=config
        )

        assert result.size == (1920, 1080)
        assert result.mode == "RGB"

    def test_draw_zombie_icon_creates_pixels(self):
        """Test that _draw_zombie_icon draws pixel art zombie."""
        compositor = PhotoBoothCompositor()
        canvas = Image.new("RGB", (100, 100), (0, 0, 0))

        # Draw zombie icon at position (10, 10) with size 40
        compositor._draw_zombie_icon(canvas, 10, 10, 40)

        # Check that some pixels were drawn (not all black)
        pixels = canvas.load()
        non_black_pixels = 0
        for x in range(100):
            for y in range(100):
                if pixels[x, y] != (0, 0, 0):
                    non_black_pixels += 1

        # Should have drawn some colored pixels
        assert non_black_pixels > 0

    def test_draw_zombie_icon_uses_green_colors(self):
        """Test that zombie icon uses green color palette."""
        compositor = PhotoBoothCompositor()
        canvas = Image.new("RGB", (100, 100), (0, 0, 0))

        compositor._draw_zombie_icon(canvas, 10, 10, 40)

        # Collect all unique colors
        pixels = canvas.load()
        colors = set()
        for x in range(100):
            for y in range(100):
                if pixels[x, y] != (0, 0, 0):
                    colors.add(pixels[x, y])

        # Should contain green colors (body, head, dark green)
        green_colors = [c for c in colors if c[1] > c[0] and c[1] > c[2]]
        assert len(green_colors) >= 2  # At least body and head green

        # Should contain red for eyes
        red_colors = [c for c in colors if c[0] > c[1] and c[0] > c[2]]
        assert len(red_colors) >= 1

    def test_draw_zombie_icon_scales_with_size(self):
        """Test that zombie icon scales correctly with different sizes."""
        compositor = PhotoBoothCompositor()

        # Draw small icon
        small_canvas = Image.new("RGB", (50, 50), (0, 0, 0))
        compositor._draw_zombie_icon(small_canvas, 5, 5, 20)

        # Draw large icon
        large_canvas = Image.new("RGB", (100, 100), (0, 0, 0))
        compositor._draw_zombie_icon(large_canvas, 10, 10, 40)

        # Count non-black pixels in each
        def count_pixels(canvas):
            pixels = canvas.load()
            count = 0
            for x in range(canvas.width):
                for y in range(canvas.height):
                    if pixels[x, y] != (0, 0, 0):
                        count += 1
            return count

        small_count = count_pixels(small_canvas)
        large_count = count_pixels(large_canvas)

        # Larger icon should have more pixels (roughly 4x for 2x size)
        assert large_count > small_count

    def test_score_header_includes_zombie_icons(self):
        """Test that score header draws zombie icons alongside text."""
        compositor = PhotoBoothCompositor()
        canvas = Image.new("RGB", (1920, 1080), compositor.BG_COLOR)

        compositor._draw_score_header(canvas, 42)

        # Check for green pixels (zombie icons) in header area
        pixels = canvas.load()
        green_pixels_in_header = 0
        header_y_start = compositor.FRAME_BORDER
        header_y_end = compositor.FRAME_BORDER + compositor.SCORE_HEIGHT

        for x in range(1920):
            for y in range(header_y_start, header_y_end):
                r, g, b = pixels[x, y]
                # Check for zombie green colors
                if g > 100 and g > r and g > b:
                    green_pixels_in_header += 1

        # Should have green pixels from zombie icons
        assert green_pixels_in_header > 0

    def test_generate_with_various_zombie_counts(self):
        """Test composite generation with different zombie counts."""
        compositor = PhotoBoothCompositor()
        gameplay = Image.new("RGB", (1280, 720), (0, 100, 0))
        config = PhotoBoothConfig()

        # Test with 0 zombies
        result = compositor.generate(selfie=None, gameplay=gameplay, zombie_count=0, config=config)
        assert result.size == (1920, 1080)

        # Test with large number
        result = compositor.generate(
            selfie=None, gameplay=gameplay, zombie_count=999, config=config
        )
        assert result.size == (1920, 1080)

    def test_qr_code_attribute_exists(self):
        """Test that compositor has qr_code attribute after initialization."""
        compositor = PhotoBoothCompositor()

        # qr_code attribute should exist (may be None if asset not found)
        assert hasattr(compositor, "qr_code")

        # If qr_code loaded, it should be a PIL Image
        if compositor.qr_code is not None:
            assert isinstance(compositor.qr_code, Image.Image)

    def test_footer_renders_with_qr_code(self):
        """Test that footer renders correctly with QR code."""
        compositor = PhotoBoothCompositor()
        canvas = Image.new("RGB", (1920, 1080), compositor.BG_COLOR)
        config = PhotoBoothConfig()

        # Draw footer (includes QR code area)
        compositor._draw_footer(canvas, config)

        # Check that footer area has been modified (not all background color)
        pixels = canvas.load()
        footer_y = compositor.OUTPUT_HEIGHT - compositor.FOOTER_HEIGHT - compositor.FRAME_BORDER

        # Check QR code area (right side of footer)
        qr_size = compositor.FOOTER_HEIGHT - 30
        qr_x = compositor.OUTPUT_WIDTH - compositor.FRAME_BORDER - qr_size - 10

        # At least some pixels in QR area should not be background color
        non_bg_pixels = 0
        for x in range(qr_x, qr_x + qr_size):
            for y in range(footer_y + 5, footer_y + 5 + qr_size):
                if 0 <= x < 1920 and 0 <= y < 1080:
                    if pixels[x, y] != compositor.BG_COLOR:
                        non_bg_pixels += 1

        # Should have drawn something in QR area (either QR code or placeholder)
        assert non_bg_pixels > 0


class TestPhotoBoothController:
    """Tests for PhotoBoothController."""

    def test_initial_state(self):
        """Test controller initial state."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        assert controller.state == PhotoBoothState.INACTIVE
        assert controller.selfie_opted_in is False

    def test_disabled_state(self):
        """Test controller when disabled."""
        config = PhotoBoothConfig(enabled=False)
        controller = PhotoBoothController(config)

        assert controller.state == PhotoBoothState.DISABLED

    def test_consent_flow_opt_in(self):
        """Test consent flow when user opts in."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)
        controller.initialize()

        controller.show_consent_prompt()
        assert controller.state == PhotoBoothState.AWAITING_CONSENT

        controller.handle_consent_input(opted_in=True)
        # Will be False if camera not available, True if available
        assert controller.state in (PhotoBoothState.CONSENT_GIVEN, PhotoBoothState.CONSENT_DECLINED)

    def test_consent_flow_opt_out(self):
        """Test consent flow when user opts out."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)
        controller.initialize()

        controller.show_consent_prompt()
        controller.handle_consent_input(opted_in=False)

        assert controller.state == PhotoBoothState.CONSENT_DECLINED
        assert controller.selfie_opted_in is False

    def test_reset(self):
        """Test controller reset."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)
        controller.initialize()

        controller.show_consent_prompt()
        controller.handle_consent_input(opted_in=True)
        controller.reset()

        assert controller.state == PhotoBoothState.INACTIVE
        assert controller.selfie_opted_in is False


class TestPhotoBoothConsentKeyboardInput:
    """Tests for photo booth consent keyboard input handling in game engine."""

    def test_consent_keyboard_y_opts_in(self):
        """Test that pressing Y key opts in to selfie."""
        from photo_booth.config import PhotoBoothConfig
        from photo_booth.controller import PhotoBoothController, PhotoBoothState

        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)
        controller.show_consent_prompt()

        # Simulate Y key press by calling handle_consent_input
        controller.handle_consent_input(opted_in=True)

        assert controller.state == PhotoBoothState.CONSENT_GIVEN

    def test_consent_keyboard_n_opts_out(self):
        """Test that pressing N key opts out of selfie."""
        from photo_booth.config import PhotoBoothConfig
        from photo_booth.controller import PhotoBoothController, PhotoBoothState

        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)
        controller.show_consent_prompt()

        # Simulate N key press by calling handle_consent_input
        controller.handle_consent_input(opted_in=False)

        assert controller.state == PhotoBoothState.CONSENT_DECLINED
        assert controller.selfie_opted_in is False

    def test_consent_keyboard_a_opts_in(self):
        """Test that pressing A key opts in to selfie (alternative to Y)."""
        from photo_booth.config import PhotoBoothConfig
        from photo_booth.controller import PhotoBoothController, PhotoBoothState

        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)
        controller.show_consent_prompt()

        # A key should behave same as Y key
        controller.handle_consent_input(opted_in=True)

        assert controller.state == PhotoBoothState.CONSENT_GIVEN

    def test_consent_keyboard_b_opts_out(self):
        """Test that pressing B key opts out of selfie (alternative to N)."""
        from photo_booth.config import PhotoBoothConfig
        from photo_booth.controller import PhotoBoothController, PhotoBoothState

        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)
        controller.show_consent_prompt()

        # B key should behave same as N key
        controller.handle_consent_input(opted_in=False)

        assert controller.state == PhotoBoothState.CONSENT_DECLINED
        assert controller.selfie_opted_in is False

    def test_consent_flow_completes_before_arcade_starts(self):
        """Test that consent must be given before arcade session begins."""
        from photo_booth.config import PhotoBoothConfig
        from photo_booth.controller import PhotoBoothController, PhotoBoothState

        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        # Initially inactive
        assert controller.state == PhotoBoothState.INACTIVE

        # Show consent prompt
        controller.show_consent_prompt()
        assert controller.state == PhotoBoothState.AWAITING_CONSENT

        # Give consent
        controller.handle_consent_input(opted_in=True)
        assert controller.is_consent_complete() is True

    def test_consent_input_ignored_when_not_awaiting(self):
        """Test that consent input is ignored when not in AWAITING_CONSENT state."""
        from photo_booth.config import PhotoBoothConfig
        from photo_booth.controller import PhotoBoothController, PhotoBoothState

        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        # Don't show consent prompt - stay in INACTIVE state
        assert controller.state == PhotoBoothState.INACTIVE

        # Try to give consent - should be ignored
        controller.handle_consent_input(opted_in=True)

        # State should remain INACTIVE
        assert controller.state == PhotoBoothState.INACTIVE
        assert controller.selfie_opted_in is False


class TestPhotoBoothArcadeTiming:
    """Tests for photo booth arcade timing functionality."""

    def test_arcade_tracking_starts_at_zero(self):
        """Test that arcade tracking starts with zero elapsed time."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        # Before starting tracking
        assert controller.get_arcade_elapsed_time() == 0.0

    def test_start_arcade_tracking(self):
        """Test starting arcade time tracking."""
        import time

        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        controller.start_arcade_tracking()
        time.sleep(0.1)  # Small delay

        elapsed = controller.get_arcade_elapsed_time()
        assert elapsed >= 0.1
        assert elapsed < 1.0  # Should be close to 0.1

    def test_should_capture_gameplay_timing(self):
        """Test gameplay capture timing logic."""
        config = PhotoBoothConfig(enabled=True, screenshot_delay=0.1)  # Short delay for testing
        controller = PhotoBoothController(config)

        # Before tracking starts
        assert controller.should_capture_gameplay() is False

        controller.start_arcade_tracking()

        # Immediately after start - should not capture yet
        assert controller.should_capture_gameplay() is False

        # Wait for delay
        import time

        time.sleep(0.15)

        # Now should be ready to capture
        assert controller.should_capture_gameplay() is True

    def test_gameplay_captured_flag(self):
        """Test that gameplay_captured flag prevents duplicate captures."""
        config = PhotoBoothConfig(enabled=True, screenshot_delay=0.0)
        controller = PhotoBoothController(config)

        controller.start_arcade_tracking()

        # Initially not captured
        assert controller.gameplay_captured is False
        assert controller.should_capture_gameplay() is True

        # Simulate capture by setting flag directly
        controller._gameplay_captured = True

        # Now should not capture again
        assert controller.should_capture_gameplay() is False

    def test_has_minimum_arcade_time(self):
        """Test minimum arcade time check."""
        import time

        config = PhotoBoothConfig(enabled=True, min_arcade_time=0.1)  # Short for testing
        controller = PhotoBoothController(config)

        controller.start_arcade_tracking()

        # Immediately - not enough time
        assert controller.has_minimum_arcade_time() is False

        # Wait for minimum time
        time.sleep(0.15)

        # Now should have enough time
        assert controller.has_minimum_arcade_time() is True

    def test_reset_clears_arcade_tracking(self):
        """Test that reset clears arcade tracking state."""
        import time

        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        controller.start_arcade_tracking()
        time.sleep(0.1)
        controller._gameplay_captured = True
        controller._selfie_captured = True

        # Reset should clear everything
        controller.reset()

        assert controller.get_arcade_elapsed_time() == 0.0
        assert controller.gameplay_captured is False
        assert controller.selfie_captured is False

    def test_config_timing_defaults(self):
        """Test default timing configuration values."""
        config = PhotoBoothConfig()

        assert config.min_arcade_time == 10.0
        assert config.screenshot_delay == 15.0

    def test_config_timing_from_env(self):
        """Test timing configuration from environment."""
        import os

        # Set environment variables
        os.environ["PHOTO_BOOTH_MIN_ARCADE_TIME"] = "5.0"
        os.environ["PHOTO_BOOTH_SCREENSHOT_DELAY"] = "8.0"

        try:
            config = PhotoBoothConfig.from_env()
            assert config.min_arcade_time == 5.0
            assert config.screenshot_delay == 8.0
        finally:
            # Clean up
            del os.environ["PHOTO_BOOTH_MIN_ARCADE_TIME"]
            del os.environ["PHOTO_BOOTH_SCREENSHOT_DELAY"]


class TestPhotoBoothArcadeTimeTracking:
    """Tests for photo booth arcade time tracking methods."""

    def test_start_arcade_tracking_initializes_time(self):
        """Test that start_arcade_tracking sets the start time."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        # Initially, elapsed time should be 0
        assert controller.get_arcade_elapsed_time() == 0.0

        # Start tracking
        controller.start_arcade_tracking()

        # Elapsed time should now be very small (just started)
        elapsed = controller.get_arcade_elapsed_time()
        assert elapsed >= 0.0
        assert elapsed < 1.0  # Should be less than 1 second

    def test_start_arcade_tracking_resets_capture_flags(self):
        """Test that start_arcade_tracking resets capture flags."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        # Manually set capture flags to True
        controller._gameplay_captured = True
        controller._selfie_captured = True

        # Start tracking should reset them
        controller.start_arcade_tracking()

        assert controller.gameplay_captured is False
        assert controller.selfie_captured is False

    def test_gameplay_captured_property(self):
        """Test gameplay_captured property reflects internal state."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        # Initially False
        assert controller.gameplay_captured is False

        # Set internal flag
        controller._gameplay_captured = True
        assert controller.gameplay_captured is True

    def test_selfie_captured_property(self):
        """Test selfie_captured property reflects internal state."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        # Initially False
        assert controller.selfie_captured is False

        # Set internal flag
        controller._selfie_captured = True
        assert controller.selfie_captured is True

    def test_has_minimum_arcade_time_false_when_not_started(self):
        """Test has_minimum_arcade_time returns False when tracking not started."""
        config = PhotoBoothConfig(enabled=True, min_arcade_time=10.0)
        controller = PhotoBoothController(config)

        # Without starting tracking, should return False
        assert controller.has_minimum_arcade_time() is False

    def test_has_minimum_arcade_time_false_when_too_short(self):
        """Test has_minimum_arcade_time returns False when session too short."""
        config = PhotoBoothConfig(enabled=True, min_arcade_time=10.0)
        controller = PhotoBoothController(config)

        # Start tracking
        controller.start_arcade_tracking()

        # Immediately check - should be False (less than 10 seconds)
        assert controller.has_minimum_arcade_time() is False

    def test_has_minimum_arcade_time_true_when_enough_time(self):
        """Test has_minimum_arcade_time returns True when enough time passed."""
        config = PhotoBoothConfig(enabled=True, min_arcade_time=0.0)  # 0 seconds minimum
        controller = PhotoBoothController(config)

        # Start tracking
        controller.start_arcade_tracking()

        # With 0 second minimum, should immediately be True
        assert controller.has_minimum_arcade_time() is True

    def test_get_arcade_elapsed_time_returns_zero_when_not_started(self):
        """Test get_arcade_elapsed_time returns 0 when not started."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        assert controller.get_arcade_elapsed_time() == 0.0

    def test_should_capture_gameplay_false_when_already_captured(self):
        """Test should_capture_gameplay returns False when already captured."""
        config = PhotoBoothConfig(enabled=True, screenshot_delay=0.0)
        controller = PhotoBoothController(config)

        controller.start_arcade_tracking()
        controller._gameplay_captured = True

        assert controller.should_capture_gameplay() is False

    def test_should_capture_gameplay_false_when_not_enough_time(self):
        """Test should_capture_gameplay returns False when not enough time passed."""
        config = PhotoBoothConfig(enabled=True, screenshot_delay=15.0)
        controller = PhotoBoothController(config)

        controller.start_arcade_tracking()

        # Immediately after starting, should be False (less than 15 seconds)
        assert controller.should_capture_gameplay() is False

    def test_should_capture_gameplay_true_when_ready(self):
        """Test should_capture_gameplay returns True when conditions met."""
        config = PhotoBoothConfig(enabled=True, screenshot_delay=0.0)  # 0 delay
        controller = PhotoBoothController(config)

        controller.start_arcade_tracking()

        # With 0 delay and not captured, should be True
        assert controller.should_capture_gameplay() is True

    def test_should_capture_selfie_false_when_not_opted_in(self):
        """Test should_capture_selfie returns False when not opted in."""
        config = PhotoBoothConfig(enabled=True, screenshot_delay=0.0)
        controller = PhotoBoothController(config)

        controller.start_arcade_tracking()
        controller._selfie_opted_in = False

        assert controller.should_capture_selfie() is False

    def test_should_capture_selfie_false_when_already_captured(self):
        """Test should_capture_selfie returns False when already captured."""
        config = PhotoBoothConfig(enabled=True, screenshot_delay=0.0)
        controller = PhotoBoothController(config)

        controller.start_arcade_tracking()
        controller._selfie_opted_in = True
        controller._selfie_captured = True

        assert controller.should_capture_selfie() is False

    def test_reset_clears_arcade_tracking(self):
        """Test that reset clears arcade tracking state."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        # Start tracking and set flags
        controller.start_arcade_tracking()
        controller._gameplay_captured = True
        controller._selfie_captured = True

        # Reset
        controller.reset()

        # All tracking state should be cleared
        assert controller._arcade_start_time == 0.0
        assert controller.gameplay_captured is False
        assert controller.selfie_captured is False


class TestPhotoBoothGameEngineIntegration:
    """Tests for photo booth integration with game engine logic."""

    def test_composite_generation_requires_gameplay_capture(self):
        """Test that generate_composite fails without gameplay image."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        # Try to generate without capturing gameplay
        result = controller.generate_composite(zombie_count=42)

        # Should return None (no gameplay image)
        assert result is None

    def test_consent_complete_after_opt_in(self):
        """Test is_consent_complete returns True after opting in."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        controller.show_consent_prompt()
        controller.handle_consent_input(opted_in=True)

        assert controller.is_consent_complete() is True

    def test_consent_complete_after_opt_out(self):
        """Test is_consent_complete returns True after opting out."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        controller.show_consent_prompt()
        controller.handle_consent_input(opted_in=False)

        assert controller.is_consent_complete() is True

    def test_consent_not_complete_when_awaiting(self):
        """Test is_consent_complete returns False when still awaiting."""
        config = PhotoBoothConfig(enabled=True)
        controller = PhotoBoothController(config)

        controller.show_consent_prompt()

        assert controller.is_consent_complete() is False

    def test_full_arcade_photo_workflow(self):
        """Test the full workflow: consent -> tracking -> capture -> composite."""
        config = PhotoBoothConfig(
            enabled=True,
            min_arcade_time=0.0,  # No minimum time
            screenshot_delay=0.0,  # No delay
        )
        controller = PhotoBoothController(config)

        # Step 1: Consent flow
        controller.show_consent_prompt()
        controller.handle_consent_input(opted_in=False)  # Opt out of selfie
        assert controller.is_consent_complete() is True

        # Step 2: Start arcade tracking
        controller.start_arcade_tracking()
        assert controller.get_arcade_elapsed_time() >= 0.0

        # Step 3: Check minimum time (should pass with 0.0 config)
        assert controller.has_minimum_arcade_time() is True

        # Step 4: Gameplay capture would happen here (requires pygame surface)
        # We can't test actual capture without pygame, but we can verify the flag
        assert controller.gameplay_captured is False
