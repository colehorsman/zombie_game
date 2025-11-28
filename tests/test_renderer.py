"""Tests for Renderer class - visual rendering logic."""

import pytest
from unittest.mock import Mock, MagicMock, patch
import pygame
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from renderer import Renderer
from jit_access_quest import Auditor, AdminRole
from models import PermissionSet, Vector2
from game_map import GameMap


@pytest.fixture
def mock_screen():
    """Create a mock pygame screen."""
    pygame.init()
    return pygame.display.set_mode((1280, 720))


@pytest.fixture
def renderer(mock_screen):
    """Create a renderer instance."""
    return Renderer(mock_screen)


@pytest.fixture
def mock_game_map():
    """Create a mock game map."""
    game_map = Mock(spec=GameMap)
    game_map.camera_x = 0
    game_map.camera_y = 0
    game_map.is_on_screen = Mock(return_value=True)
    game_map.world_to_screen = Mock(side_effect=lambda x, y: (x, y))
    return game_map


@pytest.fixture
def sample_auditor():
    """Create a sample auditor for testing."""
    return Auditor(x=500, y=400, patrol_width=400)


@pytest.fixture
def sample_admin_role():
    """Create a sample admin role for testing."""
    perm_set = PermissionSet(
        id="ps-admin-123",
        name="AdministratorAccess",
        identity_labels=["ADMIN"],
        user_count=5,
        has_jit=False
    )
    return AdminRole(perm_set, x=600, y=400)


class TestAuditorRendering:
    """Tests for auditor rendering (man in black suit style)."""

    def test_render_auditor_draws_on_screen(self, renderer, mock_game_map, sample_auditor):
        """Test that auditor is rendered when on screen."""
        # Mock pygame drawing functions to track calls
        with patch('pygame.draw.rect') as mock_rect, \
             patch('pygame.draw.circle') as mock_circle, \
             patch('pygame.draw.line') as mock_line:
            
            renderer.render_auditor(sample_auditor, mock_game_map)
            
            # Verify drawing functions were called (auditor has multiple body parts)
            assert mock_rect.call_count > 0, "Should draw rectangles for body parts"
            assert mock_circle.call_count > 0, "Should draw circles for head and hands"
            assert mock_line.call_count > 0, "Should draw lines for clipboard checklist"

    def test_render_auditor_not_drawn_when_off_screen(self, renderer, mock_game_map, sample_auditor):
        """Test that auditor is not rendered when off screen."""
        mock_game_map.is_on_screen = Mock(return_value=False)
        
        with patch('pygame.draw.rect') as mock_rect:
            renderer.render_auditor(sample_auditor, mock_game_map)
            
            # Should not draw anything if off screen
            mock_rect.assert_not_called()

    def test_render_auditor_handles_none(self, renderer, mock_game_map):
        """Test that render_auditor handles None auditor gracefully."""
        # Should not raise exception
        renderer.render_auditor(None, mock_game_map)

    def test_render_auditor_uses_correct_colors(self, renderer, mock_game_map, sample_auditor):
        """Test that auditor uses correct colors for man in black suit."""
        with patch('pygame.draw.rect') as mock_rect, \
             patch('pygame.draw.circle') as mock_circle:
            
            renderer.render_auditor(sample_auditor, mock_game_map)
            
            # Check that black/dark colors are used for suit
            rect_calls = [call[0][1] for call in mock_rect.call_args_list]  # Get color arguments
            
            # Should have dark colors for suit (20-30 RGB range)
            dark_colors = [color for color in rect_calls if isinstance(color, tuple) and max(color) <= 50]
            assert len(dark_colors) > 0, "Should use dark colors for black suit"
            
            # Should have skin tone for head/hands (220, 180, 140)
            circle_calls = [call[0][1] for call in mock_circle.call_args_list]
            skin_colors = [color for color in circle_calls if isinstance(color, tuple) and color[0] > 200]
            assert len(skin_colors) > 0, "Should use skin tone for head and hands"

    def test_render_auditor_draws_clipboard(self, renderer, mock_game_map, sample_auditor):
        """Test that auditor renders with clipboard."""
        with patch('pygame.draw.rect') as mock_rect, \
             patch('pygame.draw.line') as mock_line:
            
            renderer.render_auditor(sample_auditor, mock_game_map)
            
            # Clipboard should have brown backing (139, 90, 43)
            rect_calls = [call[0][1] for call in mock_rect.call_args_list]
            brown_colors = [color for color in rect_calls if isinstance(color, tuple) and 
                          color[0] > 100 and color[1] < 100 and color[2] < 50]
            assert len(brown_colors) > 0, "Should have brown clipboard backing"
            
            # Should draw lines for checklist
            assert mock_line.call_count >= 3, "Should draw at least 3 lines for checklist"

    def test_render_auditor_draws_sunglasses(self, renderer, mock_game_map, sample_auditor):
        """Test that auditor renders with sunglasses."""
        with patch('pygame.draw.rect') as mock_rect:
            
            renderer.render_auditor(sample_auditor, mock_game_map)
            
            # Sunglasses should be black rectangles (10, 10, 10)
            rect_calls = [call[0][1] for call in mock_rect.call_args_list]
            black_colors = [color for color in rect_calls if color == (10, 10, 10)]
            assert len(black_colors) >= 2, "Should have at least 2 black rectangles for sunglasses"


class TestAdminRoleRendering:
    """Tests for admin role rendering (gold suit with crown)."""

    def test_render_admin_roles_draws_on_screen(self, renderer, mock_game_map, sample_admin_role):
        """Test that admin roles are rendered when on screen."""
        with patch('pygame.draw.rect') as mock_rect, \
             patch('pygame.draw.circle') as mock_circle, \
             patch('pygame.draw.polygon') as mock_polygon:
            
            renderer.render_admin_roles([sample_admin_role], mock_game_map, pulse_time=0.0)
            
            # Verify drawing functions were called
            assert mock_rect.call_count > 0, "Should draw rectangles for body"
            assert mock_polygon.call_count > 0, "Should draw polygon for crown"

    def test_render_admin_roles_uses_gold_color_when_unprotected(self, renderer, mock_game_map, sample_admin_role):
        """Test that unprotected admin roles use gold suit color."""
        sample_admin_role.has_jit = False
        
        with patch('pygame.draw.rect') as mock_rect:
            renderer.render_admin_roles([sample_admin_role], mock_game_map, pulse_time=0.0)
            
            # Check for gold color (218, 165, 32)
            rect_calls = [call[0][1] for call in mock_rect.call_args_list]
            gold_colors = [color for color in rect_calls if isinstance(color, tuple) and 
                         color[0] > 200 and color[1] > 150 and color[2] < 50]
            assert len(gold_colors) > 0, "Should use gold color for unprotected admin role"

    def test_render_admin_roles_uses_green_color_when_protected(self, renderer, mock_game_map, sample_admin_role):
        """Test that protected admin roles use green suit color."""
        sample_admin_role.has_jit = True
        
        with patch('pygame.draw.rect') as mock_rect:
            renderer.render_admin_roles([sample_admin_role], mock_game_map, pulse_time=0.0)
            
            # Check for green color (60, 140, 60)
            rect_calls = [call[0][1] for call in mock_rect.call_args_list]
            green_colors = [color for color in rect_calls if isinstance(color, tuple) and 
                          color[0] < 100 and color[1] > 100 and color[2] < 100]
            assert len(green_colors) > 0, "Should use green color for protected admin role"

    def test_render_admin_roles_draws_crown(self, renderer, mock_game_map, sample_admin_role):
        """Test that admin roles render with crown."""
        with patch('pygame.draw.polygon') as mock_polygon:
            renderer.render_admin_roles([sample_admin_role], mock_game_map, pulse_time=0.0)
            
            # Should draw crown polygon
            assert mock_polygon.call_count >= 1, "Should draw crown polygon"
            
            # Check crown color is gold (255, 215, 0)
            if mock_polygon.call_args_list:
                crown_color = mock_polygon.call_args_list[0][0][1]
                assert crown_color == (255, 215, 0), "Crown should be gold color"

    def test_render_admin_roles_draws_shield_when_protected(self, renderer, mock_game_map, sample_admin_role):
        """Test that protected admin roles render with purple shield."""
        sample_admin_role.has_jit = True
        
        with patch('shield.render_shield') as mock_render_shield:
            renderer.render_admin_roles([sample_admin_role], mock_game_map, pulse_time=0.5)
            
            # Should call render_shield for protected role
            mock_render_shield.assert_called_once()
            
            # Verify correct parameters
            call_args = mock_render_shield.call_args
            assert call_args[0][1] == sample_admin_role, "Should pass admin role to shield renderer"

    def test_render_admin_roles_no_shield_when_unprotected(self, renderer, mock_game_map, sample_admin_role):
        """Test that unprotected admin roles don't render shield."""
        sample_admin_role.has_jit = False
        
        with patch('shield.render_shield') as mock_render_shield:
            renderer.render_admin_roles([sample_admin_role], mock_game_map, pulse_time=0.5)
            
            # Should NOT call render_shield for unprotected role
            mock_render_shield.assert_not_called()

    def test_render_admin_roles_draws_label(self, renderer, mock_game_map, sample_admin_role):
        """Test that admin roles render with permission set name label."""
        # Create a mock font to capture render calls
        mock_font = Mock()
        mock_surface = Mock()
        mock_surface.get_width.return_value = 100
        mock_font.render.return_value = mock_surface

        # Patch the renderer's existing small_font attribute
        original_font = renderer.small_font
        renderer.small_font = mock_font

        try:
            renderer.render_admin_roles([sample_admin_role], mock_game_map, pulse_time=0.0)

            # Should render label with permission set name
            render_calls = [call[0][0] for call in mock_font.render.call_args_list]
            assert any("AdministratorAccess" in str(call) for call in render_calls), \
                "Should render permission set name as label"
        finally:
            renderer.small_font = original_font

    def test_render_admin_roles_not_drawn_when_off_screen(self, renderer, mock_game_map, sample_admin_role):
        """Test that admin roles are not rendered when off screen."""
        mock_game_map.is_on_screen = Mock(return_value=False)
        
        with patch('pygame.draw.rect') as mock_rect:
            renderer.render_admin_roles([sample_admin_role], mock_game_map, pulse_time=0.0)
            
            # Should not draw anything if off screen
            mock_rect.assert_not_called()


class TestJitQuestMessageRendering:
    """Tests for JIT quest message rendering."""

    def test_render_jit_quest_message_displays_when_active(self, renderer):
        """Test that JIT quest messages are displayed when active."""
        from models import JitQuestState
        
        jit_quest = JitQuestState(
            active=True,
            auditor_position=Vector2(500, 400),
            admin_roles=[],
            protected_count=0,
            total_count=2,
            quest_completed=False,
            quest_failed=False
        )
        jit_quest.quest_message = "Test message"
        jit_quest.quest_message_timer = 3.0
        
        with patch.object(renderer, 'render_message_bubble') as mock_render_bubble:
            renderer.render_jit_quest_message(jit_quest)
            
            # Should call render_message_bubble with the message
            mock_render_bubble.assert_called_once_with("Test message")

    def test_render_jit_quest_message_not_displayed_when_timer_expired(self, renderer):
        """Test that JIT quest messages are not displayed when timer expires."""
        from models import JitQuestState
        
        jit_quest = JitQuestState(
            active=True,
            auditor_position=Vector2(500, 400),
            admin_roles=[],
            protected_count=0,
            total_count=2,
            quest_completed=False,
            quest_failed=False
        )
        jit_quest.quest_message = "Test message"
        jit_quest.quest_message_timer = 0.0  # Expired
        
        with patch.object(renderer, 'render_message_bubble') as mock_render_bubble:
            renderer.render_jit_quest_message(jit_quest)
            
            # Should NOT call render_message_bubble when timer expired
            mock_render_bubble.assert_not_called()

    def test_render_jit_quest_message_handles_none(self, renderer):
        """Test that render_jit_quest_message handles None quest state."""
        # Should not raise exception
        renderer.render_jit_quest_message(None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
