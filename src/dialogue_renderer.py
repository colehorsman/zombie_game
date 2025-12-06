"""Dialogue renderer for 8-bit comic book-style educational bubbles.

Renders Zelda-style dialogue bubbles with pointed tails, page indicators,
and highlighted words for Story Mode educational content.
"""

import logging
from typing import Optional, Tuple

import pygame

from models import DialogueMessage, DialogueSequence

logger = logging.getLogger(__name__)

# Dialogue bubble styling constants
BUBBLE_PADDING = 20
BUBBLE_BORDER_WIDTH = 4
BUBBLE_CORNER_RADIUS = 8
BUBBLE_MAX_WIDTH = 500
BUBBLE_MIN_WIDTH = 200

# Colors (8-bit retro palette)
BUBBLE_BG_COLOR = (20, 20, 40)  # Dark blue-black
BUBBLE_BORDER_COLOR = (138, 43, 226)  # Purple (Sonrai brand)
TEXT_COLOR = (255, 255, 255)  # White
HIGHLIGHT_COLOR = (255, 215, 0)  # Gold for highlighted words
SPEAKER_COLOR = (138, 43, 226)  # Purple for speaker name
PAGE_INDICATOR_COLOR = (100, 100, 120)  # Gray for inactive dots
PAGE_INDICATOR_ACTIVE = (255, 255, 255)  # White for active dot

# Tail constants
TAIL_WIDTH = 20
TAIL_HEIGHT = 15


class DialogueRenderer:
    """Renders 8-bit comic book-style dialogue bubbles."""

    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize the dialogue renderer.

        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = None
        self.speaker_font = None
        self._init_fonts()

    def _init_fonts(self) -> None:
        """Initialize 8-bit style fonts."""
        pygame.font.init()
        # Try to use a pixel/8-bit style font, fall back to default
        try:
            self.font = pygame.font.Font(None, 24)  # Default font at 24pt
            self.speaker_font = pygame.font.Font(None, 20)  # Smaller for speaker
        except Exception as e:
            logger.warning(f"Could not load fonts: {e}")
            self.font = pygame.font.SysFont("arial", 20)
            self.speaker_font = pygame.font.SysFont("arial", 16)

    def render_dialogue(
        self,
        surface: pygame.Surface,
        dialogue: DialogueSequence,
        target_pos: Optional[Tuple[int, int]] = None,
        format_kwargs: Optional[dict] = None,
    ) -> None:
        """
        Render a dialogue bubble with the current message.

        Args:
            surface: Pygame surface to render on
            dialogue: The DialogueSequence to render
            target_pos: Position to point the tail at (e.g., zombie position)
            format_kwargs: Keyword arguments for text formatting (e.g., zombie_name)
        """
        message = dialogue.get_current_message()
        if not message:
            return

        # Format the message text with any provided kwargs
        text = message.format_text(**(format_kwargs or {}))

        # Calculate bubble dimensions and position
        bubble_rect, tail_points = self._calculate_bubble_geometry(
            text, message.speaker, target_pos
        )

        # Draw semi-transparent overlay to dim the game
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # 50% transparent black
        surface.blit(overlay, (0, 0))

        # Draw the bubble background
        self._draw_bubble(surface, bubble_rect, tail_points)

        # Draw the speaker name
        self._draw_speaker(surface, message.speaker, bubble_rect)

        # Draw the message text with highlights
        self._draw_text(surface, text, message.highlight_words, bubble_rect)

        # Draw page indicators if multi-page
        if len(dialogue.messages) > 1:
            self._draw_page_indicators(
                surface, dialogue.current_page, len(dialogue.messages), bubble_rect
            )

        # Draw "Press A/ENTER to continue" hint
        self._draw_continue_hint(surface, bubble_rect, dialogue.is_complete())

    def _calculate_bubble_geometry(
        self,
        text: str,
        speaker: str,
        target_pos: Optional[Tuple[int, int]],
    ) -> Tuple[pygame.Rect, list]:
        """
        Calculate bubble position and tail points.

        Args:
            text: The message text
            speaker: Speaker name
            target_pos: Position to point tail at

        Returns:
            Tuple of (bubble_rect, tail_points)
        """
        # Calculate text dimensions
        lines = self._wrap_text(text, BUBBLE_MAX_WIDTH - BUBBLE_PADDING * 2)
        text_height = len(lines) * (self.font.get_height() + 4)
        text_width = max(self.font.size(line)[0] for line in lines) if lines else 100

        # Add padding and speaker height
        bubble_width = min(max(text_width + BUBBLE_PADDING * 2, BUBBLE_MIN_WIDTH), BUBBLE_MAX_WIDTH)
        bubble_height = text_height + BUBBLE_PADDING * 2 + 30  # Extra for speaker + hint

        # Position bubble in center-bottom of screen by default
        bubble_x = (self.screen_width - bubble_width) // 2
        bubble_y = self.screen_height - bubble_height - 80  # 80px from bottom

        # Adjust if target position provided
        if target_pos:
            # Point tail toward target, but keep bubble in safe area
            bubble_x = max(
                20,
                min(
                    target_pos[0] - bubble_width // 2,
                    self.screen_width - bubble_width - 20,
                ),
            )
            # Keep bubble in lower portion of screen
            bubble_y = max(
                self.screen_height // 2,
                min(bubble_y, self.screen_height - bubble_height - 40),
            )

        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)

        # Calculate tail points (pointing down toward target or center-bottom)
        tail_tip_x = target_pos[0] if target_pos else bubble_x + bubble_width // 2
        tail_tip_y = bubble_y + bubble_height + TAIL_HEIGHT

        # Clamp tail tip to be within bubble width
        tail_tip_x = max(bubble_x + 30, min(tail_tip_x, bubble_x + bubble_width - 30))

        tail_points = [
            (tail_tip_x - TAIL_WIDTH // 2, bubble_y + bubble_height - 2),
            (tail_tip_x + TAIL_WIDTH // 2, bubble_y + bubble_height - 2),
            (tail_tip_x, tail_tip_y),
        ]

        return bubble_rect, tail_points

    def _wrap_text(self, text: str, max_width: int) -> list:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            if self.font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines if lines else [""]

    def _draw_bubble(self, surface: pygame.Surface, rect: pygame.Rect, tail_points: list) -> None:
        """Draw the bubble background with border and tail."""
        # Draw main bubble with rounded corners
        pygame.draw.rect(surface, BUBBLE_BG_COLOR, rect, border_radius=BUBBLE_CORNER_RADIUS)
        pygame.draw.rect(
            surface,
            BUBBLE_BORDER_COLOR,
            rect,
            BUBBLE_BORDER_WIDTH,
            border_radius=BUBBLE_CORNER_RADIUS,
        )

        # Draw tail
        pygame.draw.polygon(surface, BUBBLE_BG_COLOR, tail_points)
        pygame.draw.lines(surface, BUBBLE_BORDER_COLOR, False, tail_points[1:], BUBBLE_BORDER_WIDTH)
        pygame.draw.lines(surface, BUBBLE_BORDER_COLOR, False, tail_points[:2], BUBBLE_BORDER_WIDTH)

    def _draw_speaker(self, surface: pygame.Surface, speaker: str, rect: pygame.Rect) -> None:
        """Draw the speaker name at the top of the bubble."""
        speaker_text = self.speaker_font.render(f"[ {speaker} ]", True, SPEAKER_COLOR)
        speaker_x = rect.x + BUBBLE_PADDING
        speaker_y = rect.y + 8
        surface.blit(speaker_text, (speaker_x, speaker_y))

    def _draw_text(
        self,
        surface: pygame.Surface,
        text: str,
        highlight_words: list,
        rect: pygame.Rect,
    ) -> None:
        """Draw the message text with highlighted words."""
        lines = self._wrap_text(text, rect.width - BUBBLE_PADDING * 2)
        y = rect.y + 30  # Below speaker name

        for line in lines:
            x = rect.x + BUBBLE_PADDING
            words = line.split()

            for i, word in enumerate(words):
                # Check if this word should be highlighted
                is_highlighted = any(hw.lower() in word.lower() for hw in highlight_words)
                color = HIGHLIGHT_COLOR if is_highlighted else TEXT_COLOR

                word_surface = self.font.render(word, True, color)
                surface.blit(word_surface, (x, y))
                x += word_surface.get_width() + self.font.size(" ")[0]

            y += self.font.get_height() + 4

    def _draw_page_indicators(
        self,
        surface: pygame.Surface,
        current_page: int,
        total_pages: int,
        rect: pygame.Rect,
    ) -> None:
        """Draw page indicator dots at the bottom of the bubble."""
        dot_radius = 4
        dot_spacing = 12
        total_width = total_pages * dot_spacing

        start_x = rect.x + (rect.width - total_width) // 2
        y = rect.y + rect.height - 20

        for i in range(total_pages):
            x = start_x + i * dot_spacing + dot_radius
            color = PAGE_INDICATOR_ACTIVE if i == current_page else PAGE_INDICATOR_COLOR
            pygame.draw.circle(surface, color, (x, y), dot_radius)

    def _draw_continue_hint(
        self, surface: pygame.Surface, rect: pygame.Rect, is_last_page: bool
    ) -> None:
        """Draw the 'Press A/ENTER to continue' hint."""
        hint_text = "Press A / ENTER to close" if is_last_page else "Press A / ENTER →"
        hint_surface = self.speaker_font.render(hint_text, True, PAGE_INDICATOR_COLOR)
        hint_x = rect.x + rect.width - hint_surface.get_width() - BUBBLE_PADDING
        hint_y = rect.y + rect.height - 18
        surface.blit(hint_surface, (hint_x, hint_y))

    def render_bubble(
        self,
        surface: pygame.Surface,
        text: str,
        position: Tuple[int, int],
        speaker: str = "SONRAI",
        highlight_words: Optional[list] = None,
    ) -> None:
        """
        Render a standalone dialogue bubble at the specified position.

        Args:
            surface: Pygame surface to render on
            text: The text to display
            position: (x, y) center position for the bubble
            speaker: Name of the speaker
            highlight_words: Words to highlight in gold
        """
        if highlight_words is None:
            highlight_words = []

        # Calculate bubble geometry
        bubble_rect, tail_points = self._calculate_bubble_geometry(text, position, None)

        # Draw bubble background
        self._draw_bubble(surface, bubble_rect, tail_points)

        # Draw speaker name
        self._draw_speaker(surface, speaker, bubble_rect)

        # Draw text with highlights
        self._draw_text(surface, text, highlight_words, bubble_rect)

        # Draw continue hint
        self._draw_continue_hint(surface, bubble_rect, True)

    def render_page_indicator(
        self,
        surface: pygame.Surface,
        current_page: int,
        total_pages: int,
        position: Tuple[int, int],
    ) -> None:
        """
        Render page indicator dots below the dialogue bubble.

        Args:
            surface: Pygame surface to render on
            current_page: Current page number (1-indexed)
            total_pages: Total number of pages
            position: (x, y) center position for the indicators
        """
        dot_radius = 4
        dot_spacing = 12
        total_width = (total_pages - 1) * dot_spacing
        start_x = position[0] - total_width // 2
        y = position[1]

        for i in range(total_pages):
            x = start_x + i * dot_spacing
            color = PAGE_INDICATOR_ACTIVE if i == current_page - 1 else PAGE_INDICATOR_COLOR
            pygame.draw.circle(surface, color, (x, y), dot_radius)
