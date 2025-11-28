"""Tests for BossDialogueController."""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from boss_dialogue_controller import BossDialogueController, BossDialogueContent


@pytest.fixture
def sample_dialogue_data():
    """Sample boss dialogue data."""
    return {
        "title": "🕷️ TEST BOSS APPEARS! 🕷️",
        "description": "This is a test boss for unit testing.",
        "how_attacked": [
            "Attack method 1",
            "Attack method 2",
            "Attack method 3"
        ],
        "victims": "Test Corp, Example Inc",
        "prevention": [
            "Prevention tip 1",
            "Prevention tip 2"
        ],
        "mechanic": "Defeat the test boss to pass the test!"
    }


class TestBossDialogueContent:
    """Tests for the BossDialogueContent dataclass."""

    def test_from_dict(self, sample_dialogue_data):
        """from_dict creates content from dictionary."""
        content = BossDialogueContent.from_dict(sample_dialogue_data)

        assert content.title == "🕷️ TEST BOSS APPEARS! 🕷️"
        assert content.description == "This is a test boss for unit testing."
        assert len(content.how_attacked) == 3
        assert content.victims == "Test Corp, Example Inc"
        assert len(content.prevention) == 2
        assert content.mechanic == "Defeat the test boss to pass the test!"

    def test_from_dict_with_defaults(self):
        """from_dict handles missing fields with defaults."""
        content = BossDialogueContent.from_dict({})

        assert content.title == "BOSS APPEARS!"
        assert content.description == ""
        assert content.how_attacked == []
        assert content.victims == ""
        assert content.prevention == []
        assert content.mechanic == ""


class TestBossDialogueController:
    """Tests for the BossDialogueController class."""

    def test_initial_state(self):
        """Controller starts in hidden state."""
        controller = BossDialogueController()

        assert not controller.is_showing
        assert controller.content is None
        assert not controller.has_been_shown

    def test_show_dialogue(self, sample_dialogue_data):
        """show displays the dialogue."""
        controller = BossDialogueController()
        controller.show(sample_dialogue_data)

        assert controller.is_showing
        assert controller.content is not None
        assert controller.content.title == "🕷️ TEST BOSS APPEARS! 🕷️"
        assert controller.has_been_shown

    def test_dismiss_when_showing(self, sample_dialogue_data):
        """dismiss hides the dialogue and returns True."""
        controller = BossDialogueController()
        controller.show(sample_dialogue_data)

        result = controller.dismiss()

        assert result is True
        assert not controller.is_showing
        # Content should still be accessible after dismiss
        assert controller.content is not None

    def test_dismiss_when_not_showing(self):
        """dismiss returns False when no dialogue showing."""
        controller = BossDialogueController()

        result = controller.dismiss()

        assert result is False

    def test_reset(self, sample_dialogue_data):
        """reset clears all state."""
        controller = BossDialogueController()
        controller.show(sample_dialogue_data)
        controller.dismiss()

        controller.reset()

        assert not controller.is_showing
        assert controller.content is None
        assert not controller.has_been_shown

    def test_has_been_shown_persists(self, sample_dialogue_data):
        """has_been_shown remains True after dismiss."""
        controller = BossDialogueController()
        controller.show(sample_dialogue_data)
        controller.dismiss()

        assert controller.has_been_shown

    def test_build_message(self, sample_dialogue_data):
        """build_message creates formatted dialogue."""
        controller = BossDialogueController()
        controller.show(sample_dialogue_data)

        message = controller.build_message()

        # Check key elements are present
        assert "TEST BOSS APPEARS" in message
        assert "test boss for unit testing" in message
        assert "HOW THEY ATTACKED" in message
        assert "Attack method 1" in message
        assert "NOTABLE VICTIMS" in message
        assert "Test Corp" in message
        assert "PREVENTION" in message
        assert "Prevention tip 1" in message
        assert "Press ENTER to begin" in message

    def test_build_message_no_content(self):
        """build_message returns fallback when no content."""
        controller = BossDialogueController()

        message = controller.build_message()

        assert message == "BOSS BATTLE!"

    def test_get_title(self, sample_dialogue_data):
        """get_title returns boss title."""
        controller = BossDialogueController()
        controller.show(sample_dialogue_data)

        title = controller.get_title()

        assert "TEST BOSS APPEARS" in title

    def test_get_title_no_content(self):
        """get_title returns fallback when no content."""
        controller = BossDialogueController()

        title = controller.get_title()

        assert title == "BOSS BATTLE"

    def test_multiple_shows(self, sample_dialogue_data):
        """Showing dialogue multiple times updates content."""
        controller = BossDialogueController()

        # First show
        controller.show(sample_dialogue_data)
        assert "TEST BOSS" in controller.content.title

        # Second show with different data
        new_data = {
            "title": "NEW BOSS",
            "description": "Different boss",
            "how_attacked": [],
            "victims": "",
            "prevention": [],
            "mechanic": ""
        }
        controller.show(new_data)

        assert controller.content.title == "NEW BOSS"
        assert controller.is_showing

    def test_build_message_formatting(self, sample_dialogue_data):
        """build_message includes proper bullet points and structure."""
        controller = BossDialogueController()
        controller.show(sample_dialogue_data)

        message = controller.build_message()

        # Check bullet formatting
        assert "  • Attack method 1" in message
        assert "  ✓ Prevention tip 1" in message
        # Check separator line
        assert "═" in message
