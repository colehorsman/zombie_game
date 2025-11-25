"""Tests for main.py initialization and configuration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pygame
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from main import (
    load_configuration,
    calculate_scaled_dimensions,
    initialize_pygame
)


class TestLoadConfiguration:
    """Tests for configuration loading."""

    @patch('main.load_dotenv')
    @patch('os.getenv')
    def test_load_configuration_success(self, mock_getenv, mock_load_dotenv):
        """Test successful configuration loading with all required values."""
        # Mock environment variables
        env_vars = {
            'SONRAI_API_URL': 'https://test.sonrai.com/graphql',
            'SONRAI_ORG_ID': 'test-org-123',
            'SONRAI_API_TOKEN': 'test-token-456',
            'GAME_WIDTH': '1280',
            'GAME_HEIGHT': '720',
            'FULLSCREEN': 'false',
            'TARGET_FPS': '60',
            'MAX_ZOMBIES': '1000'
        }
        mock_getenv.side_effect = lambda key, default=None: env_vars.get(key, default)

        config = load_configuration()

        assert config['api_url'] == 'https://test.sonrai.com/graphql'
        assert config['org_id'] == 'test-org-123'
        assert config['api_token'] == 'test-token-456'
        assert config['game_width'] == 1280
        assert config['game_height'] == 720
        assert config['fullscreen'] is False
        assert config['target_fps'] == 60
        assert config['max_zombies'] == 1000

    @patch('main.load_dotenv')
    @patch('os.getenv')
    def test_load_configuration_missing_api_url(self, mock_getenv, mock_load_dotenv):
        """Test configuration loading fails when API URL is missing."""
        env_vars = {
            'SONRAI_ORG_ID': 'test-org-123',
            'SONRAI_API_TOKEN': 'test-token-456',
            'GAME_WIDTH': '1280',
            'GAME_HEIGHT': '720'
        }
        mock_getenv.side_effect = lambda key, default=None: env_vars.get(key, default)

        with pytest.raises(ValueError, match="SONRAI_API_URL is required"):
            load_configuration()

    @patch('main.load_dotenv')
    @patch('os.getenv')
    def test_load_configuration_missing_org_id(self, mock_getenv, mock_load_dotenv):
        """Test configuration loading fails when org ID is missing."""
        env_vars = {
            'SONRAI_API_URL': 'https://test.sonrai.com/graphql',
            'SONRAI_API_TOKEN': 'test-token-456'
        }
        mock_getenv.side_effect = lambda key, default=None: env_vars.get(key, default)

        with pytest.raises(ValueError, match="SONRAI_ORG_ID is required"):
            load_configuration()

    @patch('main.load_dotenv')
    @patch('os.getenv')
    def test_load_configuration_missing_api_token(self, mock_getenv, mock_load_dotenv):
        """Test configuration loading fails when API token is missing."""
        env_vars = {
            'SONRAI_API_URL': 'https://test.sonrai.com/graphql',
            'SONRAI_ORG_ID': 'test-org-123'
        }
        mock_getenv.side_effect = lambda key, default=None: env_vars.get(key, default)

        with pytest.raises(ValueError, match="SONRAI_API_TOKEN is required"):
            load_configuration()

    @patch('main.load_dotenv')
    @patch('os.getenv')
    def test_load_configuration_uses_defaults(self, mock_getenv, mock_load_dotenv):
        """Test configuration uses default values when optional vars are missing."""
        env_vars = {
            'SONRAI_API_URL': 'https://test.sonrai.com/graphql',
            'SONRAI_ORG_ID': 'test-org-123',
            'SONRAI_API_TOKEN': 'test-token-456'
        }
        mock_getenv.side_effect = lambda key, default=None: env_vars.get(key, default)

        config = load_configuration()

        assert config['game_width'] == 1280  # Default
        assert config['game_height'] == 720  # Default
        assert config['fullscreen'] is False  # Default
        assert config['target_fps'] == 60  # Default
        assert config['max_zombies'] == 1000  # Default


class TestCalculateScaledDimensions:
    """Tests for aspect ratio scaling calculations."""

    def test_calculate_scaled_dimensions_pillarbox(self):
        """Test pillarboxing (black bars on sides) when display is wider."""
        # Game: 1280x720 (16:9), Display: 1920x1080 (16:9 but wider)
        scaled_w, scaled_h, offset_x, offset_y = calculate_scaled_dimensions(
            1280, 720, 1920, 1080
        )

        # Should scale to full height, add pillarbox on sides
        assert scaled_h == 1080
        assert scaled_w == 1920  # 1080 * (1280/720) = 1920
        assert offset_x == 0  # No offset needed (perfect fit)
        assert offset_y == 0

    def test_calculate_scaled_dimensions_letterbox(self):
        """Test letterboxing (black bars on top/bottom) when display is taller."""
        # Game: 1280x720 (16:9), Display: 1280x1024 (5:4, taller)
        scaled_w, scaled_h, offset_x, offset_y = calculate_scaled_dimensions(
            1280, 720, 1280, 1024
        )

        # Should scale to full width, add letterbox on top/bottom
        assert scaled_w == 1280
        assert scaled_h == 720  # 1280 / (1280/720) = 720
        assert offset_x == 0
        assert offset_y == (1024 - 720) // 2  # Centered vertically

    def test_calculate_scaled_dimensions_perfect_fit(self):
        """Test no scaling needed when aspect ratios match."""
        # Game: 1280x720, Display: 1280x720 (exact match)
        scaled_w, scaled_h, offset_x, offset_y = calculate_scaled_dimensions(
            1280, 720, 1280, 720
        )

        assert scaled_w == 1280
        assert scaled_h == 720
        assert offset_x == 0
        assert offset_y == 0

    def test_calculate_scaled_dimensions_4k_display(self):
        """Test scaling for 4K display."""
        # Game: 1280x720, Display: 3840x2160 (4K, 16:9)
        scaled_w, scaled_h, offset_x, offset_y = calculate_scaled_dimensions(
            1280, 720, 3840, 2160
        )

        # Should scale to full height (3x scale)
        assert scaled_h == 2160
        assert scaled_w == 3840  # 2160 * (1280/720) = 3840
        assert offset_x == 0
        assert offset_y == 0


class TestInitializePygame:
    """Tests for Pygame initialization with controller detection."""

    @patch('pygame.init')
    @patch('pygame.joystick.init')
    @patch('pygame.joystick.get_count')
    @patch('pygame.joystick.Joystick')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.Surface')
    def test_initialize_pygame_no_controllers(
        self, mock_surface, mock_caption, mock_set_mode, 
        mock_joystick_class, mock_get_count, mock_joy_init, mock_pygame_init
    ):
        """Test Pygame initialization when no controllers are detected."""
        # Mock no controllers
        mock_get_count.return_value = 0
        
        # Mock display surface
        mock_display = Mock()
        mock_set_mode.return_value = mock_display
        
        # Mock game surface
        mock_game_surface = Mock()
        mock_surface.return_value = mock_game_surface

        display, game_surface = initialize_pygame(1280, 720, fullscreen=False)

        # Verify pygame initialization
        mock_pygame_init.assert_called_once()
        mock_joy_init.assert_called_once()
        mock_get_count.assert_called_once()
        
        # Verify no joystick was initialized
        mock_joystick_class.assert_not_called()
        
        # Verify display created
        assert display == mock_display
        assert game_surface == mock_game_surface

    @patch('pygame.init')
    @patch('pygame.joystick.init')
    @patch('pygame.joystick.get_count')
    @patch('pygame.joystick.Joystick')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.Surface')
    def test_initialize_pygame_with_controllers(
        self, mock_surface, mock_caption, mock_set_mode,
        mock_joystick_class, mock_get_count, mock_joy_init, mock_pygame_init
    ):
        """Test Pygame initialization when controllers are detected."""
        # Mock 2 controllers
        mock_get_count.return_value = 2
        
        # Mock joystick instances
        mock_joy1 = Mock()
        mock_joy1.get_name.return_value = "8BitDo SN30 Pro"
        mock_joy2 = Mock()
        mock_joy2.get_name.return_value = "Xbox Controller"
        
        mock_joystick_class.side_effect = [mock_joy1, mock_joy2]
        
        # Mock display surface
        mock_display = Mock()
        mock_set_mode.return_value = mock_display
        
        # Mock game surface
        mock_game_surface = Mock()
        mock_surface.return_value = mock_game_surface

        display, game_surface = initialize_pygame(1280, 720, fullscreen=False)

        # Verify pygame initialization
        mock_pygame_init.assert_called_once()
        mock_joy_init.assert_called_once()
        mock_get_count.assert_called_once()
        
        # Verify both joysticks were initialized
        assert mock_joystick_class.call_count == 2
        mock_joy1.init.assert_called_once()
        mock_joy2.init.assert_called_once()
        
        # Verify display created
        assert display == mock_display
        assert game_surface == mock_game_surface

    @patch('pygame.init')
    @patch('pygame.joystick.init')
    @patch('pygame.joystick.get_count')
    @patch('pygame.display.Info')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.Surface')
    def test_initialize_pygame_fullscreen_mode(
        self, mock_surface, mock_caption, mock_set_mode,
        mock_display_info, mock_get_count, mock_joy_init, mock_pygame_init
    ):
        """Test Pygame initialization in fullscreen mode."""
        # Mock no controllers
        mock_get_count.return_value = 0
        
        # Mock display info
        mock_info = Mock()
        mock_info.current_w = 1920
        mock_info.current_h = 1080
        mock_display_info.return_value = mock_info
        
        # Mock display surface
        mock_display = Mock()
        mock_set_mode.return_value = mock_display
        
        # Mock game surface
        mock_game_surface = Mock()
        mock_surface.return_value = mock_game_surface

        display, game_surface = initialize_pygame(1280, 720, fullscreen=True)

        # Verify fullscreen mode was set with native resolution
        mock_set_mode.assert_called_once_with(
            (1920, 1080),
            pygame.FULLSCREEN
        )
        
        # Verify display created
        assert display == mock_display
        assert game_surface == mock_game_surface

    @patch('pygame.init')
    @patch('pygame.joystick.init')
    @patch('pygame.joystick.get_count')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.Surface')
    def test_initialize_pygame_windowed_mode(
        self, mock_surface, mock_caption, mock_set_mode,
        mock_get_count, mock_joy_init, mock_pygame_init
    ):
        """Test Pygame initialization in windowed mode."""
        # Mock no controllers
        mock_get_count.return_value = 0
        
        # Mock display surface
        mock_display = Mock()
        mock_set_mode.return_value = mock_display
        
        # Mock game surface
        mock_game_surface = Mock()
        mock_surface.return_value = mock_game_surface

        display, game_surface = initialize_pygame(1280, 720, fullscreen=False)

        # Verify windowed mode was set with resizable flag
        mock_set_mode.assert_called_once_with(
            (1280, 720),
            pygame.RESIZABLE
        )
        
        # Verify display created
        assert display == mock_display
        assert game_surface == mock_game_surface

    @patch('pygame.init')
    @patch('pygame.joystick.init')
    @patch('pygame.joystick.get_count')
    @patch('pygame.joystick.Joystick')
    def test_initialize_pygame_controller_detection_early(
        self, mock_joystick_class, mock_get_count, mock_joy_init, mock_pygame_init
    ):
        """Test that controller detection happens EARLY before other initialization."""
        # Mock 1 controller
        mock_get_count.return_value = 1
        
        # Mock joystick instance
        mock_joy = Mock()
        mock_joy.get_name.return_value = "Test Controller"
        mock_joystick_class.return_value = mock_joy
        
        # Track call order
        call_order = []
        mock_pygame_init.side_effect = lambda: call_order.append('pygame.init')
        mock_joy_init.side_effect = lambda: call_order.append('joystick.init')
        mock_get_count.side_effect = lambda: (call_order.append('get_count'), 1)[1]

        with patch('pygame.display.set_mode'), \
             patch('pygame.display.set_caption'), \
             patch('pygame.Surface'):
            initialize_pygame(1280, 720, fullscreen=False)

        # Verify controller detection happened early
        assert call_order[0] == 'pygame.init'
        assert call_order[1] == 'joystick.init'
        assert call_order[2] == 'get_count'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
