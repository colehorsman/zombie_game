"""Tests for CheatCodeController."""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import pygame (it's already mocked in conftest.py or actually installed)
try:
    import pygame
except ImportError:
    # Create minimal pygame mock if not available
    pygame = type(sys)('pygame')
    pygame.K_u = ord('u')
    pygame.K_n = ord('n')
    pygame.K_l = ord('l')
    pygame.K_o = ord('o')
    pygame.K_c = ord('c')
    pygame.K_k = ord('k')
    pygame.K_s = ord('s')
    pygame.K_i = ord('i')
    pygame.K_p = ord('p')
    pygame.K_a = ord('a')
    pygame.K_b = ord('b')
    pygame.K_UP = 273
    pygame.K_DOWN = 274
    pygame.K_LEFT = 276
    pygame.K_RIGHT = 275

from cheat_code_controller import CheatCodeController, CheatCodeAction, CheatCodeResult


class TestCheatCodeController:
    """Tests for the CheatCodeController class."""

    def test_initial_state(self):
        """Controller starts with empty buffers."""
        controller = CheatCodeController()
        assert controller.cheat_buffer == []
        assert controller.konami_buffer == []
        assert controller.arcade_buffer == []
        assert not controller.unlock_enabled

    def test_unlock_code_detection(self):
        """UNLOCK code is detected correctly."""
        controller = CheatCodeController()

        # Type U-N-L-O-C-K
        keys = [ord('u'), ord('n'), ord('l'), ord('o'), ord('c'), ord('k')]
        result = None
        for key in keys:
            result = controller.process_key(key, current_time=0)

        assert result.action == CheatCodeAction.UNLOCK_ALL_LEVELS
        assert "All Levels Unlocked" in result.message
        assert controller.unlock_enabled

    def test_skip_code_detection(self):
        """SKIP code is detected correctly."""
        controller = CheatCodeController()

        # Type S-K-I-P
        keys = [ord('s'), ord('k'), ord('i'), ord('p')]
        result = None
        for key in keys:
            result = controller.process_key(key, current_time=0)

        assert result.action == CheatCodeAction.SKIP_LEVEL
        assert result.message is None  # Handled by GameEngine

    def test_konami_code_detection(self):
        """Konami code is detected correctly."""
        controller = CheatCodeController()

        # UP UP DOWN DOWN LEFT RIGHT LEFT RIGHT
        keys = [273, 273, 274, 274, 276, 275, 276, 275]
        result = None
        for key in keys:
            result = controller.process_key(key, current_time=0)

        assert result.action == CheatCodeAction.SPAWN_BOSS

    def test_arcade_code_detection(self):
        """Arcade code is detected correctly."""
        controller = CheatCodeController()

        # UP UP DOWN DOWN A B
        keys = [273, 273, 274, 274, ord('a'), ord('b')]
        result = None
        for key in keys:
            result = controller.process_key(key, current_time=0)

        assert result.action == CheatCodeAction.START_ARCADE

    def test_partial_code_returns_none(self):
        """Partial code input returns NONE action."""
        controller = CheatCodeController()

        # Type partial UNLOCK: U-N-L
        keys = [ord('u'), ord('n'), ord('l')]
        for key in keys:
            result = controller.process_key(key, current_time=0)

        assert result.action == CheatCodeAction.NONE

    def test_wrong_code_returns_none(self):
        """Wrong code input returns NONE action."""
        controller = CheatCodeController()

        # Type random keys
        keys = [ord('x'), ord('y'), ord('z')]
        for key in keys:
            result = controller.process_key(key, current_time=0)

        assert result.action == CheatCodeAction.NONE

    def test_timeout_resets_konami_buffer(self):
        """Konami buffer resets after timeout."""
        controller = CheatCodeController()

        # Start Konami sequence
        controller.process_key(273, current_time=0)  # UP
        controller.process_key(273, current_time=0.5)  # UP
        controller.process_key(274, current_time=1.0)  # DOWN

        # Wait for timeout
        controller.process_key(274, current_time=5.0)  # DOWN after timeout

        # Buffer should have been reset, so only last DOWN is in buffer
        assert len(controller.konami_buffer) == 1

    def test_timeout_resets_arcade_buffer(self):
        """Arcade buffer resets after timeout."""
        controller = CheatCodeController()

        # Start Arcade sequence
        controller.process_key(273, current_time=0)  # UP
        controller.process_key(273, current_time=0.5)  # UP

        # Wait for timeout
        controller.process_key(274, current_time=5.0)  # DOWN after timeout

        # Buffer should have been reset
        assert len(controller.arcade_buffer) == 1

    def test_buffer_trimming(self):
        """Buffers are trimmed to max code length."""
        controller = CheatCodeController()

        # Add many keys
        for i in range(20):
            controller.process_key(ord('x'), current_time=0)

        assert len(controller.cheat_buffer) <= 6
        assert len(controller.konami_buffer) <= 8
        assert len(controller.arcade_buffer) <= 6

    def test_reset_clears_buffers(self):
        """Reset clears all buffers."""
        controller = CheatCodeController()

        # Add some keys
        controller.process_key(ord('u'), current_time=0)
        controller.process_key(273, current_time=0)

        controller.reset()

        assert controller.cheat_buffer == []
        assert controller.konami_buffer == []
        assert controller.arcade_buffer == []

    def test_is_unlock_enabled(self):
        """is_unlock_enabled returns correct state."""
        controller = CheatCodeController()
        assert not controller.is_unlock_enabled()

        controller.enable_unlock()
        assert controller.is_unlock_enabled()

        controller.disable_unlock()
        assert not controller.is_unlock_enabled()

    def test_enable_unlock_manually(self):
        """enable_unlock sets unlock state."""
        controller = CheatCodeController()
        controller.enable_unlock()
        assert controller.unlock_enabled

    def test_unlock_persists_after_code(self):
        """Unlock state persists after code is entered."""
        controller = CheatCodeController()

        # Enter UNLOCK code
        keys = [ord('u'), ord('n'), ord('l'), ord('o'), ord('c'), ord('k')]
        for key in keys:
            controller.process_key(key, current_time=0)

        # Buffer is cleared but unlock remains enabled
        assert controller.cheat_buffer == []
        assert controller.unlock_enabled

    def test_code_detection_clears_buffer(self):
        """Successful code detection clears the relevant buffer."""
        controller = CheatCodeController()

        # Enter SKIP code
        keys = [ord('s'), ord('k'), ord('i'), ord('p')]
        for key in keys:
            controller.process_key(key, current_time=0)

        assert controller.cheat_buffer == []

    def test_multiple_codes_in_sequence(self):
        """Multiple codes can be entered in sequence."""
        controller = CheatCodeController()

        # Enter UNLOCK
        unlock_keys = [ord('u'), ord('n'), ord('l'), ord('o'), ord('c'), ord('k')]
        for key in unlock_keys:
            result = controller.process_key(key, current_time=0)
        assert result.action == CheatCodeAction.UNLOCK_ALL_LEVELS

        # Enter SKIP
        skip_keys = [ord('s'), ord('k'), ord('i'), ord('p')]
        for key in skip_keys:
            result = controller.process_key(key, current_time=0)
        assert result.action == CheatCodeAction.SKIP_LEVEL

    def test_interleaved_input_no_false_positive(self):
        """Interleaved input doesn't trigger false positives."""
        controller = CheatCodeController()

        # Type UNBLOCXK (wrong)
        keys = [ord('u'), ord('n'), ord('b'), ord('l'), ord('o'), ord('c'), ord('x'), ord('k')]
        result = None
        for key in keys:
            result = controller.process_key(key, current_time=0)

        # Should not trigger UNLOCK
        assert result.action == CheatCodeAction.NONE
        assert not controller.unlock_enabled
