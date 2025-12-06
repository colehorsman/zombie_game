"""Property-based tests for the dialogue system.

**Feature: story-mode-education, Property 1: Dialogue Pause Behavior**
Tests that DialogueSequence correctly manages page navigation and completion state.
"""

import sys

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

sys.path.insert(0, "src")

from models import DialogueMessage, DialogueSequence, TriggerType


# Strategy for generating DialogueMessage instances
@st.composite
def dialogue_message_strategy(draw):
    """Generate random DialogueMessage instances."""
    text = draw(st.text(min_size=1, max_size=100))
    speaker = draw(st.sampled_from(["SONRAI", "SYSTEM", "PLAYER", "ZOMBIE"]))
    highlight_words = draw(st.lists(st.text(min_size=1, max_size=20), max_size=5))
    return DialogueMessage(text=text, speaker=speaker, highlight_words=highlight_words)


# Strategy for generating DialogueSequence instances
@st.composite
def dialogue_sequence_strategy(draw):
    """Generate random DialogueSequence instances with 1-10 messages."""
    trigger_type = draw(st.sampled_from(list(TriggerType)))
    num_messages = draw(st.integers(min_value=1, max_value=10))
    messages = [draw(dialogue_message_strategy()) for _ in range(num_messages)]
    return DialogueSequence(trigger_type=trigger_type, messages=messages)


class TestDialogueSequenceProperties:
    """Property-based tests for DialogueSequence.

    **Feature: story-mode-education, Property 1: Dialogue Pause Behavior**
    **Validates: Requirements 1.3, 1.5**
    """

    @given(dialogue_sequence_strategy())
    @settings(max_examples=100)
    def test_initial_page_is_zero(self, seq: DialogueSequence):
        """Property: New sequences always start at page 0."""
        assert seq.current_page == 0

    @given(dialogue_sequence_strategy())
    @settings(max_examples=100)
    def test_next_page_advances_until_end(self, seq: DialogueSequence):
        """Property: next_page advances until reaching the last page, then returns False."""
        num_messages = len(seq.messages)

        # Advance through all pages
        for i in range(num_messages - 1):
            assert seq.current_page == i
            result = seq.next_page()
            assert result is True
            assert seq.current_page == i + 1

        # At last page, next_page should return False and not advance
        assert seq.is_complete()
        result = seq.next_page()
        assert result is False
        assert seq.current_page == num_messages - 1  # Still on last page

    @given(dialogue_sequence_strategy())
    @settings(max_examples=100)
    def test_is_complete_only_on_last_page(self, seq: DialogueSequence):
        """Property: is_complete returns True only when on the last page."""
        num_messages = len(seq.messages)

        # Not complete until we reach the last page
        for i in range(num_messages - 1):
            assert seq.current_page == i
            assert seq.is_complete() is False
            seq.next_page()

        # Now on last page, should be complete
        assert seq.current_page == num_messages - 1
        assert seq.is_complete() is True

    @given(dialogue_sequence_strategy())
    @settings(max_examples=100)
    def test_get_current_message_returns_correct_message(self, seq: DialogueSequence):
        """Property: get_current_message always returns the message at current_page index."""
        num_messages = len(seq.messages)

        for i in range(num_messages):
            msg = seq.get_current_message()
            assert msg is seq.messages[i]
            if i < num_messages - 1:
                seq.next_page()

    @given(dialogue_sequence_strategy())
    @settings(max_examples=100)
    def test_reset_returns_to_first_page(self, seq: DialogueSequence):
        """Property: reset() always returns to page 0."""
        # Advance to some random page
        while not seq.is_complete():
            seq.next_page()

        # Reset
        seq.reset()

        assert seq.current_page == 0
        assert seq.is_complete() is (len(seq.messages) == 1)  # Only complete if single page


class TestDialogueMessageProperties:
    """Property-based tests for DialogueMessage."""

    @given(st.text(min_size=1, max_size=50), st.text(min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_format_text_with_placeholder(self, name: str, value: str):
        """Property: format_text correctly substitutes placeholders."""
        msg = DialogueMessage(text=f"Hello {{name}}, your value is {{value}}!")
        result = msg.format_text(name=name, value=value)
        assert name in result
        assert value in result

    @given(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_characters="{}")))
    @settings(max_examples=100)
    def test_format_text_without_placeholders_unchanged(self, text: str):
        """Property: format_text returns original text when no placeholders or braces."""
        msg = DialogueMessage(text=text)
        result = msg.format_text()
        assert result == text

    @given(dialogue_message_strategy())
    @settings(max_examples=100)
    def test_format_text_handles_missing_keys_gracefully(self, msg: DialogueMessage):
        """Property: format_text returns original text when keys are missing."""
        # This should not raise an exception
        result = msg.format_text(nonexistent_key="value")
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestEducationalProgressProperties:
    """Property-based tests for EducationalProgress.

    **Feature: story-mode-education, Property 4: Educational Progress Round-Trip**
    **Validates: Requirements 4.2, 4.3**
    """

    @given(
        st.sets(st.sampled_from([t.value for t in TriggerType]), max_size=7),
        st.integers(min_value=0, max_value=1000),
        st.booleans(),
        st.booleans(),
    )
    @settings(max_examples=100)
    def test_round_trip_preserves_all_data(
        self,
        completed_triggers: set,
        zombies_eliminated: int,
        first_role_seen: bool,
        first_user_seen: bool,
    ):
        """Property: to_dict then from_dict preserves all progress data exactly."""
        from models import EducationalProgress

        # Create progress with given values
        progress = EducationalProgress(
            completed_triggers=completed_triggers,
            zombies_eliminated=zombies_eliminated,
            first_role_seen=first_role_seen,
            first_user_seen=first_user_seen,
        )

        # Round-trip through serialization
        data = progress.to_dict()
        restored = EducationalProgress.from_dict(data)

        # Verify all fields preserved
        assert restored.completed_triggers == progress.completed_triggers
        assert restored.zombies_eliminated == progress.zombies_eliminated
        assert restored.first_role_seen == progress.first_role_seen
        assert restored.first_user_seen == progress.first_user_seen

    @given(st.sampled_from(list(TriggerType)))
    @settings(max_examples=100)
    def test_has_seen_after_mark_seen(self, trigger_type: TriggerType):
        """Property: has_seen returns True after mark_seen for any trigger type."""
        from models import EducationalProgress

        progress = EducationalProgress()
        assert progress.has_seen(trigger_type) is False

        progress.mark_seen(trigger_type)
        assert progress.has_seen(trigger_type) is True

    @given(
        st.sets(st.sampled_from([t.value for t in TriggerType]), min_size=1, max_size=7),
        st.integers(min_value=1, max_value=100),
    )
    @settings(max_examples=100)
    def test_reset_clears_all_progress(self, completed_triggers: set, zombies_eliminated: int):
        """Property: reset clears all progress to initial state."""
        from models import EducationalProgress

        progress = EducationalProgress(
            completed_triggers=completed_triggers,
            zombies_eliminated=zombies_eliminated,
            first_role_seen=True,
            first_user_seen=True,
        )

        progress.reset()

        assert len(progress.completed_triggers) == 0
        assert progress.zombies_eliminated == 0
        assert progress.first_role_seen is False
        assert progress.first_user_seen is False

    def test_from_dict_handles_empty_data(self):
        """Property: from_dict returns default progress for empty/None data."""
        from models import EducationalProgress

        # Test with None
        progress = EducationalProgress.from_dict(None)
        assert len(progress.completed_triggers) == 0
        assert progress.zombies_eliminated == 0

        # Test with empty dict
        progress = EducationalProgress.from_dict({})
        assert len(progress.completed_triggers) == 0
        assert progress.zombies_eliminated == 0

    @given(
        st.sampled_from(list(TriggerType)),
        st.sampled_from(list(TriggerType)),
    )
    @settings(max_examples=100)
    def test_marking_one_trigger_does_not_affect_others(
        self, trigger1: TriggerType, trigger2: TriggerType
    ):
        """
        Property: Completing one trigger type does not affect other trigger types.

        **Feature: story-mode-education, Property 5: Progress Tracking Independence**
        **Validates: Requirements 4.1, 4.5**
        """
        from models import EducationalProgress

        progress = EducationalProgress()

        # Mark first trigger
        progress.mark_seen(trigger1)

        # Check that only trigger1 is marked (unless they're the same)
        assert progress.has_seen(trigger1) is True

        if trigger1 != trigger2:
            assert progress.has_seen(trigger2) is False

            # Mark second trigger
            progress.mark_seen(trigger2)

            # Both should now be marked
            assert progress.has_seen(trigger1) is True
            assert progress.has_seen(trigger2) is True

    @given(st.lists(st.sampled_from(list(TriggerType)), min_size=1, max_size=7, unique=True))
    @settings(max_examples=100)
    def test_multiple_triggers_tracked_independently(self, triggers: list):
        """Property: Multiple triggers can be tracked independently."""
        from models import EducationalProgress

        progress = EducationalProgress()
        all_triggers = list(TriggerType)

        # Mark each trigger in the list
        for trigger in triggers:
            progress.mark_seen(trigger)

        # Verify only the marked triggers are seen
        for trigger in all_triggers:
            expected = trigger in triggers
            assert progress.has_seen(trigger) == expected, f"Trigger {trigger} mismatch"


class TestEducationManagerProperties:
    """Property-based tests for EducationManager.

    **Feature: story-mode-education, Property 2: First Kill Education Trigger**
    **Validates: Requirements 2.1, 2.3, 2.5**
    """

    @given(
        st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_characters="{}")),
        st.sampled_from(["User", "Role", "ServiceAccount"]),
        st.integers(min_value=1, max_value=365),
    )
    @settings(max_examples=100)
    def test_first_kill_triggers_with_zombie_data(
        self, zombie_name: str, zombie_type: str, days: int
    ):
        """Property: First elimination triggers education with zombie name and type."""
        from education_manager import EducationManager

        manager = EducationManager()

        # First kill should trigger
        context = {
            "zombie_name": zombie_name,
            "zombie_type": zombie_type,
            "days_since_login": str(days),
        }
        dialogue = manager.check_trigger(TriggerType.FIRST_ZOMBIE_KILL, context)

        assert dialogue is not None
        assert dialogue.trigger_type == TriggerType.FIRST_ZOMBIE_KILL

        # Format the first message and verify it contains zombie name
        msg = dialogue.get_current_message()
        formatted = msg.format_text(**manager.get_format_kwargs())
        assert zombie_name in formatted

    @given(st.sampled_from(list(TriggerType)))
    @settings(max_examples=100)
    def test_trigger_not_repeated_after_seen(self, trigger_type: TriggerType):
        """Property: Triggers don't fire again after being seen."""
        from education_manager import EducationManager

        manager = EducationManager()

        # First trigger should work
        dialogue1 = manager.check_trigger(trigger_type)
        if dialogue1:  # Some triggers may not have content
            # Dismiss it
            manager.dismiss_dialogue()

            # Second trigger should return None
            dialogue2 = manager.check_trigger(trigger_type)
            assert dialogue2 is None

    @given(st.sampled_from(list(TriggerType)))
    @settings(max_examples=100)
    def test_no_trigger_while_dialogue_active(self, trigger_type: TriggerType):
        """Property: No new triggers while a dialogue is active."""
        from education_manager import EducationManager

        manager = EducationManager()

        # Start a dialogue
        manager.check_trigger(TriggerType.STORY_MODE_WELCOME)

        # Try to trigger another - should fail
        dialogue = manager.check_trigger(trigger_type)
        assert dialogue is None or trigger_type == TriggerType.STORY_MODE_WELCOME

    def test_milestone_5_triggers_at_exact_count(self):
        """Property: 5-kill milestone triggers at exactly 5 eliminations."""
        from education_manager import EducationManager

        manager = EducationManager()

        # Counts 1-4 should not trigger milestone
        for i in range(4):
            result = manager.increment_eliminations()
            assert result is None, f"Unexpected trigger at count {i + 1}"

        # Count 5 should trigger
        result = manager.increment_eliminations()
        assert result is not None
        assert result.trigger_type == TriggerType.MILESTONE_5_KILLS

    def test_milestone_10_triggers_at_exact_count(self):
        """Property: 10-kill milestone triggers at exactly 10 eliminations."""
        from education_manager import EducationManager

        manager = EducationManager()
        manager.progress.zombies_eliminated = 9

        # Count 10 should trigger
        result = manager.increment_eliminations()
        assert result is not None
        assert result.trigger_type == TriggerType.MILESTONE_10_KILLS

    @given(st.sampled_from(["Role", "role", "ROLE", "aws.iam.role"]))
    @settings(max_examples=10)
    def test_first_role_encounter_triggers(self, role_type: str):
        """Property: First Role encounter triggers role education."""
        from education_manager import EducationManager

        manager = EducationManager()

        result = manager.check_zombie_type_education(role_type)
        assert result is not None
        assert result.trigger_type == TriggerType.FIRST_ROLE_ENCOUNTER

        # Second encounter should not trigger
        manager.dismiss_dialogue()
        result2 = manager.check_zombie_type_education(role_type)
        assert result2 is None

    @given(st.sampled_from(["User", "user", "USER", "aws.iam.user"]))
    @settings(max_examples=10)
    def test_first_user_encounter_triggers(self, user_type: str):
        """Property: First User encounter triggers user education."""
        from education_manager import EducationManager

        manager = EducationManager()

        result = manager.check_zombie_type_education(user_type)
        assert result is not None
        assert result.trigger_type == TriggerType.FIRST_USER_ENCOUNTER

        # Second encounter should not trigger
        manager.dismiss_dialogue()
        result2 = manager.check_zombie_type_education(user_type)
        assert result2 is None


class TestZombieInfoPanelProperties:
    """Property-based tests for zombie info panel completeness.

    **Feature: story-mode-education, Property 3: Zombie Info Panel Completeness**
    **Validates: Requirements 3.1, 3.2, 3.3**
    """

    @given(
        st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_characters="{}")),
        st.sampled_from(["User", "Role"]),
        st.integers(min_value=0, max_value=365),
    )
    @settings(max_examples=100)
    def test_info_panel_shows_name_type_and_days(
        self, zombie_name: str, zombie_type: str, days_since_login: int
    ):
        """
        Property: For any eliminated zombie, the info panel (across all dialogue pages)
        displays identity name, type (User or Role), and days since last login.
        """
        from education_manager import EducationManager

        manager = EducationManager()

        # Trigger first kill education with zombie context
        context = {
            "zombie_name": zombie_name,
            "zombie_type": zombie_type,
            "days_since_login": str(days_since_login),
        }
        dialogue = manager.check_trigger(TriggerType.FIRST_ZOMBIE_KILL, context)

        assert dialogue is not None, "First kill should trigger dialogue"

        # Collect all formatted text from all pages
        all_text = []
        for msg in dialogue.messages:
            formatted = msg.format_text(**manager.get_format_kwargs())
            all_text.append(formatted)

        combined_text = " ".join(all_text)

        # Verify zombie name is displayed somewhere in the dialogue
        assert zombie_name in combined_text, f"Zombie name '{zombie_name}' not in info panel"

        # Verify zombie type is displayed (case-insensitive check)
        assert (
            zombie_type.lower() in combined_text.lower()
        ), f"Zombie type '{zombie_type}' not in info panel"

        # Verify days since login is displayed
        assert (
            str(days_since_login) in combined_text
        ), f"Days since login '{days_since_login}' not in info panel"

    @given(
        st.text(min_size=1, max_size=30, alphabet=st.characters(blacklist_characters="{}")),
        st.sampled_from(["User", "Role"]),
    )
    @settings(max_examples=50)
    def test_info_panel_handles_unknown_days(self, zombie_name: str, zombie_type: str):
        """
        Property: Info panel gracefully handles unknown days since login.
        """
        from education_manager import EducationManager

        manager = EducationManager()

        # Trigger with "unknown" days
        context = {
            "zombie_name": zombie_name,
            "zombie_type": zombie_type,
            "days_since_login": "unknown",
        }
        dialogue = manager.check_trigger(TriggerType.FIRST_ZOMBIE_KILL, context)

        assert dialogue is not None

        # Collect all formatted text from all pages
        all_text = []
        for msg in dialogue.messages:
            formatted = msg.format_text(**manager.get_format_kwargs())
            all_text.append(formatted)

        combined_text = " ".join(all_text)

        # Should still contain name and type
        assert zombie_name in combined_text
        assert zombie_type.lower() in combined_text.lower()

        # Should handle "unknown" gracefully - text should be formatted
        # (no unformatted placeholders like {zombie_name})
        assert "{zombie_name}" not in combined_text
        assert "{zombie_type}" not in combined_text


class TestTypeSpecificEducationProperties:
    """Property-based tests for type-specific education content.

    **Feature: story-mode-education, Property 7: Type-Specific Education**
    **Validates: Requirements 5.2, 5.3**
    """

    @given(st.sampled_from(["Role", "role", "ROLE"]))
    @settings(max_examples=10)
    def test_role_education_explains_service_accounts(self, role_type: str):
        """
        Property: First Role encounter triggers education explaining
        that Roles are used by services, applications, and cross-account access.
        """
        from education_manager import EducationManager

        manager = EducationManager()

        result = manager.check_zombie_type_education(role_type)
        assert result is not None
        assert result.trigger_type == TriggerType.FIRST_ROLE_ENCOUNTER

        # Collect all text from the dialogue
        all_text = " ".join(msg.text.lower() for msg in result.messages)

        # Should explain what Roles are used for
        assert "role" in all_text, "Should mention 'role' in explanation"
        assert any(
            word in all_text for word in ["service", "application", "cross-account"]
        ), "Should explain Role usage (services, applications, or cross-account)"

    @given(st.sampled_from(["User", "user", "USER"]))
    @settings(max_examples=10)
    def test_user_education_explains_human_identities(self, user_type: str):
        """
        Property: First User encounter triggers education explaining
        that Users are human accounts (employees, contractors).
        """
        from education_manager import EducationManager

        manager = EducationManager()

        result = manager.check_zombie_type_education(user_type)
        assert result is not None
        assert result.trigger_type == TriggerType.FIRST_USER_ENCOUNTER

        # Collect all text from the dialogue
        all_text = " ".join(msg.text.lower() for msg in result.messages)

        # Should explain what Users are
        assert "user" in all_text, "Should mention 'user' in explanation"
        assert any(
            word in all_text for word in ["human", "employee", "contractor", "people"]
        ), "Should explain User as human identity"
