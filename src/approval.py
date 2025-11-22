"""Approval collectibles for production environment red tape mechanics."""

import pygame
from models import Vector2


class ApprovalCollectible:
    """
    Represents a Change Approval Form collectible.

    Required in production environments to quarantine zombies.
    Represents Change Advisory Board (CAB) approval process.
    """

    def __init__(self, position: Vector2):
        """
        Initialize an approval collectible.

        Args:
            position: Position in world coordinates
        """
        self.position = position
        self.collected = False

        # Form dimensions
        self.width = 16
        self.height = 20  # Taller than regular collectibles (document shape)

        # Animation
        self.animation_timer = 0.0
        self.glow_intensity = 0

        # Create approval form sprite
        self.sprite = self._create_approval_form()

    def _create_approval_form(self) -> pygame.Surface:
        """Create an approval form sprite (looks like a document)."""
        sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Colors
        PAPER_WHITE = (255, 255, 255)
        PAPER_SHADOW = (220, 220, 220)
        TEXT_BLACK = (50, 50, 50)
        STAMP_RED = (220, 20, 20)
        GOLD_BORDER = (255, 215, 0)
        BLACK = (0, 0, 0)

        # Paper background
        pygame.draw.rect(sprite, PAPER_WHITE, (2, 2, self.width - 4, self.height - 4))

        # Paper shadow (3D effect)
        pygame.draw.line(sprite, PAPER_SHADOW, (2, self.height - 3), (self.width - 2, self.height - 3))
        pygame.draw.line(sprite, PAPER_SHADOW, (self.width - 3, 2), (self.width - 3, self.height - 3))

        # Document lines (representing text)
        for i in range(4, 12, 2):
            pygame.draw.line(sprite, TEXT_BLACK, (4, i), (self.width - 4, i))

        # "APPROVED" stamp (red circle)
        pygame.draw.circle(sprite, STAMP_RED, (self.width // 2, 14), 4, 1)
        pygame.draw.line(sprite, STAMP_RED, (self.width // 2 - 2, 14), (self.width // 2 + 2, 14))

        # Gold border (makes it stand out)
        pygame.draw.rect(sprite, GOLD_BORDER, (0, 0, self.width, self.height), 2)

        # Black outline
        pygame.draw.rect(sprite, BLACK, (0, 0, self.width, self.height), 1)

        return sprite

    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle for collision detection.

        Returns:
            Pygame Rect representing the form's bounds
        """
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            self.width,
            self.height
        )

    def check_collision(self, player_bounds: pygame.Rect) -> bool:
        """
        Check if player is colliding with the approval form.

        Args:
            player_bounds: Player's bounding rectangle

        Returns:
            True if player is touching the form
        """
        if self.collected:
            return False
        return self.get_bounds().colliderect(player_bounds)

    def collect(self) -> bool:
        """
        Collect this approval form.

        Returns:
            True if successfully collected (was not already collected)
        """
        if not self.collected:
            self.collected = True
            return True
        return False

    def update(self, delta_time: float) -> None:
        """
        Update approval form animation (glowing effect).

        Args:
            delta_time: Time elapsed since last frame
        """
        if not self.collected:
            # Pulsing glow animation
            self.animation_timer += delta_time * 2
            self.glow_intensity = int(50 + 50 * abs(pygame.math.Vector2(1, 0).rotate(self.animation_timer * 180).x))

    def render(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """
        Render the approval form to the screen.

        Args:
            screen: Pygame surface to render to
            camera_x: Camera x position
            camera_y: Camera y position
        """
        if not self.collected:
            screen_x = int(self.position.x - camera_x)
            screen_y = int(self.position.y - camera_y)

            # Draw glow effect (larger semi-transparent circle behind)
            glow_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
            glow_color = (255, 215, 0, self.glow_intensity)  # Gold with pulsing alpha
            pygame.draw.circle(
                glow_surface,
                glow_color,
                (self.width // 2 + 5, self.height // 2 + 5),
                12
            )
            screen.blit(glow_surface, (screen_x - 5, screen_y - 5))

            # Draw the form sprite
            screen.blit(self.sprite, (screen_x, screen_y))


class ApprovalManager:
    """
    Manages approval collectibles and approval status for a level.

    Tracks how many approvals have been collected and whether
    zombies can be quarantined in production environments.
    """

    def __init__(self, approvals_needed: int = 0):
        """
        Initialize the approval manager.

        Args:
            approvals_needed: Number of approvals required (0 = no approval system)
        """
        self.approvals_needed = approvals_needed
        self.approvals_collected = 0
        self.approval_forms: list[ApprovalCollectible] = []

    def add_approval_form(self, position: Vector2) -> None:
        """
        Add an approval form collectible to the level.

        Args:
            position: World position for the form
        """
        form = ApprovalCollectible(position)
        self.approval_forms.append(form)

    def collect_approval(self, player_bounds: pygame.Rect) -> bool:
        """
        Check if player collected any approval forms.

        Args:
            player_bounds: Player's bounding rectangle

        Returns:
            True if an approval was collected this frame
        """
        for form in self.approval_forms:
            if form.check_collision(player_bounds):
                if form.collect():
                    self.approvals_collected += 1
                    return True
        return False

    def has_enough_approvals(self) -> bool:
        """
        Check if enough approvals have been collected.

        Returns:
            True if approvals_collected >= approvals_needed
        """
        if self.approvals_needed == 0:
            return True  # No approval system in this environment
        return self.approvals_collected >= self.approvals_needed

    def get_approvals_remaining(self) -> int:
        """
        Get number of approvals still needed.

        Returns:
            Number of approvals remaining to collect
        """
        return max(0, self.approvals_needed - self.approvals_collected)

    def update(self, delta_time: float) -> None:
        """Update all approval form animations."""
        for form in self.approval_forms:
            form.update(delta_time)

    def render(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """Render all approval forms."""
        for form in self.approval_forms:
            form.render(screen, camera_x, camera_y)

    def reset(self) -> None:
        """Reset approval status for a new level."""
        self.approvals_collected = 0
        self.approval_forms.clear()
