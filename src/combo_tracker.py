"""Combo tracking system for arcade mode."""

import logging


logger = logging.getLogger(__name__)


class ComboTracker:
    """Tracks elimination combos with 3-second window and multiplier."""

    def __init__(self):
        """Initialize the combo tracker."""
        self.combo_count = 0
        self.combo_timer = 0.0
        self.combo_window = 3.0  # 3-second window to maintain combo
        self.highest_combo = 0
        self.combo_multiplier_threshold = 5  # 5+ combo activates multiplier
        self.combo_multiplier = 1.5  # 1.5x multiplier at 5+ combo

    def add_elimination(self) -> None:
        """
        Add an elimination to the combo.

        Resets the combo timer to 3 seconds.
        """
        self.combo_count += 1
        self.combo_timer = self.combo_window

        # Track highest combo
        if self.combo_count > self.highest_combo:
            self.highest_combo = self.combo_count
            logger.info(f"🔥 New highest combo: {self.highest_combo}x")

    def update(self, delta_time: float) -> None:
        """
        Update the combo timer.

        Args:
            delta_time: Time elapsed since last frame
        """
        if self.combo_count > 0:
            self.combo_timer -= delta_time

            # Combo expired
            if self.combo_timer <= 0:
                logger.info(f"💥 Combo expired at {self.combo_count}x")
                self.combo_count = 0
                self.combo_timer = 0.0

    def get_combo_count(self) -> int:
        """Get current combo count."""
        return self.combo_count

    def get_combo_multiplier(self) -> float:
        """
        Get current combo multiplier.

        Returns:
            1.0 for combos < 5, 1.5 for combos >= 5
        """
        if self.combo_count >= self.combo_multiplier_threshold:
            return self.combo_multiplier
        return 1.0

    def get_highest_combo(self) -> int:
        """Get highest combo achieved."""
        return self.highest_combo

    def is_multiplier_active(self) -> bool:
        """Check if combo multiplier is active."""
        return self.combo_count >= self.combo_multiplier_threshold

    def reset(self) -> None:
        """Reset combo tracker to initial state."""
        self.combo_count = 0
        self.combo_timer = 0.0
        self.highest_combo = 0
        logger.info("🔄 Combo tracker reset")
