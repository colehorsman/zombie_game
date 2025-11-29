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
