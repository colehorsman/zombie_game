"""
Tests for LevelEntryMenuController.

Includes both unit tests and property-based tests using Hypothesis.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hypothesis import given, settings
from hypothesis import strategies as st

from level_entry_menu_controller import LevelEntryAction, LevelEntryMenuController


class TestLevelEntryMenuControllerUnit:
    """Unit tests for LevelEntryMenuController."""

    def test_initialization_default(self):
        """Test controller initializes with correct defaults."""
        controller = LevelEntryMenuController()
        assert controller.enabled is True
        assert controller.active is False
        assert controller.selected_index == 0  # Arcade mode by default
        assert len(controller.options) == 2

    def test_initialization_story_default(self):
        """Test controller initializes with story mode as default."""
        controller = LevelEntryMenuController(default_mode="story")
        assert controller.selected_index == 1

    def test_initialization_disabled(self):
        """Test controller can be disabled."""
        controller = LevelEntryMenuController(enabled=False)
        assert controller.enabled is False

    def test_show_activates_menu(self):
        """Test show() activates the menu and returns message."""
        controller = LevelEntryMenuController()
        message = controller.show("Sandbox")
        assert controller.active is True
        assert controller.level_name == "Sandbox"
        assert "SANDBOX" in message
        assert "ARCADE MODE" in message

    def test_hide_deactivates_menu(self):
        """Test hide() deactivates the menu."""
        controller = LevelEntryMenuController()
        controller.show("Sandbox")
        controller.hide()
        assert controller.active is False
        assert controller.level_name is None

    def test_navigate_down(self):
        """Test navigating down changes selection."""
        controller = LevelEntryMenuController()
        controller.show("Sandbox")
        controller.navigate(1)
        assert controller.selected_index == 1

    def test_navigate_up_wraps(self):
        """Test navigating up from first option wraps to last."""
        controller = LevelEntryMenuController()
        controller.show("Sandbox")
        controller.navigate(-1)
        assert controller.selected_index == 1

    def test_navigate_down_wraps(self):
        """Test navigating down from last option wraps to first."""
        controller = LevelEntryMenuController()
        controller.show("Sandbox")
        controller.navigate(1)  # Now at index 1
        controller.navigate(1)  # Should wrap to 0
        assert controller.selected_index == 0

    def test_select_arcade_mode(self):
        """Test selecting Arcade Mode returns correct action."""
        controller = LevelEntryMenuController()
        controller.show("Sandbox")
        action = controller.select()
        assert action == LevelEntryAction.ARCADE_MODE

    def test_select_story_mode(self):
        """Test selecting Story Mode returns correct action."""
        controller = LevelEntryMenuController()
        controller.show("Sandbox")
        controller.navigate(1)
        action = controller.select()
        assert action == LevelEntryAction.STORY_MODE

    def test_cancel_returns_cancel_action(self):
        """Test cancel() returns CANCEL action."""
        controller = LevelEntryMenuController()
        controller.show("Sandbox")
        action = controller.cancel()
        assert action == LevelEntryAction.CANCEL
        assert controller.active is False

    def test_select_when_inactive_returns_none(self):
        """Test select() when inactive returns NONE."""
        controller = LevelEntryMenuController()
        action = controller.select()
        assert action == LevelEntryAction.NONE

    def test_navigate_when_inactive_returns_empty(self):
        """Test navigate() when inactive returns empty string."""
        controller = LevelEntryMenuController()
        result = controller.navigate(1)
        assert result == ""


class TestLevelEntryMenuControllerProperties:
    """Property-based tests for LevelEntryMenuController using Hypothesis."""

    @given(
        default_mode=st.sampled_from(["arcade", "story", "ARCADE", "STORY", "Arcade"])
    )
    @settings(max_examples=100)
    def test_property_1_default_selection_respects_configuration(
        self, default_mode: str
    ):
        """
        **Feature: level-entry-mode-selector, Property 1: Default Selection Respects Configuration**

        *For any* valid default_mode configuration ("arcade" or "story"),
        when the menu is shown, the initial selected_index SHALL correspond
        to that mode (0 for arcade, 1 for story).

        **Validates: Requirements 1.1, 5.3**
        """
        controller = LevelEntryMenuController(default_mode=default_mode)
        controller.show("TestLevel")

        expected_index = 1 if default_mode.lower() == "story" else 0
        assert controller.selected_index == expected_index

    @given(
        start_index=st.integers(min_value=0, max_value=1),
        direction=st.sampled_from([-1, 1]),
    )
    @settings(max_examples=100)
    def test_property_2_navigation_wraps_within_bounds(
        self, start_index: int, direction: int
    ):
        """
        **Feature: level-entry-mode-selector, Property 2: Navigation Wraps Within Bounds**

        *For any* starting selection index and navigation direction,
        the resulting selection index SHALL always be within [0, len(OPTIONS)-1]
        and SHALL change by exactly 1 position (with wrapping).

        **Validates: Requirements 2.1, 2.4**
        """
        controller = LevelEntryMenuController()
        controller.show("TestLevel")
        controller._selected_index = start_index

        controller.navigate(direction)

        # Result should be within bounds
        assert 0 <= controller.selected_index < len(controller.OPTIONS)

        # Result should be exactly 1 position different (with wrapping)
        expected = (start_index + direction) % len(controller.OPTIONS)
        assert controller.selected_index == expected

    @given(selection_index=st.integers(min_value=0, max_value=1))
    @settings(max_examples=100)
    def test_property_3_selection_returns_correct_action(self, selection_index: int):
        """
        **Feature: level-entry-mode-selector, Property 3: Selection Returns Correct Action**

        *For any* valid selection index, calling select() SHALL return
        the corresponding LevelEntryAction (index 0 → ARCADE_MODE, index 1 → STORY_MODE).

        **Validates: Requirements 2.2**
        """
        controller = LevelEntryMenuController()
        controller.show("TestLevel")
        controller._selected_index = selection_index

        action = controller.select()

        expected_actions = {
            0: LevelEntryAction.ARCADE_MODE,
            1: LevelEntryAction.STORY_MODE,
        }
        assert action == expected_actions[selection_index]

    @given(
        selection_index=st.integers(min_value=0, max_value=1),
        level_name=st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("L", "N")),
        ),
    )
    @settings(max_examples=100)
    def test_property_4_cancel_always_returns_cancel_action(
        self, selection_index: int, level_name: str
    ):
        """
        **Feature: level-entry-mode-selector, Property 4: Cancel Always Returns Cancel Action**

        *For any* menu state (any selection index, any level name),
        calling cancel() SHALL always return LevelEntryAction.CANCEL.

        **Validates: Requirements 2.3**
        """
        controller = LevelEntryMenuController()
        controller.show(level_name)
        controller._selected_index = selection_index

        action = controller.cancel()

        assert action == LevelEntryAction.CANCEL

    @given(
        level_name=st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("L", "N")),
        )
    )
    @settings(max_examples=100)
    def test_property_5_message_contains_level_name(self, level_name: str):
        """
        **Feature: level-entry-mode-selector, Property 5: Message Contains Level Name**

        *For any* level name string, the build_message output SHALL contain that level name.

        **Validates: Requirements 4.2**
        """
        controller = LevelEntryMenuController()
        message = controller.build_message(level_name)

        assert level_name.upper() in message

    @given(selection_index=st.integers(min_value=0, max_value=1))
    @settings(max_examples=100)
    def test_property_6_message_shows_correct_selection_indicator(
        self, selection_index: int
    ):
        """
        **Feature: level-entry-mode-selector, Property 6: Message Shows Correct Selection Indicator**

        *For any* selection index, the build_message output SHALL contain "▶"
        prefix only for the selected option and "  " prefix for non-selected options.

        **Validates: Requirements 2.4**
        """
        controller = LevelEntryMenuController()
        controller._selected_index = selection_index
        message = controller.build_message("TestLevel")

        # Split message into lines and find option lines
        lines = message.split("\n")
        option_lines = [line for line in lines if "MODE" in line]

        assert len(option_lines) == 2

        for i, line in enumerate(option_lines):
            if i == selection_index:
                assert line.startswith(
                    "▶ "
                ), f"Selected option {i} should have ▶ prefix"
            else:
                assert line.startswith(
                    "  "
                ), f"Non-selected option {i} should have space prefix"
