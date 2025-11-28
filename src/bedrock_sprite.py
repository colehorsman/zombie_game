"""Bedrock service icon sprite generation."""

import pygame


def generate_bedrock_sprite() -> pygame.Surface:
    """
    Generate 8-bit Bedrock service icon (48x48px).

    Blue-to-purple gradient hexagonal blocks in retro style.

    Returns:
        48x48 Surface with Bedrock icon
    """
    # Create surface with transparency
    sprite = pygame.Surface((48, 48), pygame.SRCALPHA)

    # Define hexagonal block colors (blue to purple gradient)
    colors = [
        (0, 100, 255),  # Bright blue
        (50, 80, 220),  # Medium blue
        (100, 60, 200),  # Blue-purple
        (150, 40, 180),  # Purple
    ]

    # Draw hexagonal blocks (3x3 grid)
    block_size = 14
    spacing = 16

    positions = [
        (8, 8),
        (24, 8),
        (40, 8),  # Top row
        (8, 24),
        (24, 24),
        (40, 24),  # Middle row
        (8, 40),
        (24, 40),
        (40, 40),  # Bottom row
    ]

    for i, (x, y) in enumerate(positions):
        # Pick color from gradient
        color = colors[i % len(colors)]

        # Draw filled rectangle as simplified hexagon
        rect = pygame.Rect(x, y, block_size, block_size)
        pygame.draw.rect(sprite, color, rect)

        # Add darker border for depth
        border_color = (
            max(0, color[0] - 50),
            max(0, color[1] - 50),
            max(0, color[2] - 50),
        )
        pygame.draw.rect(sprite, border_color, rect, 2)

    return sprite


def generate_bedrock_protected() -> pygame.Surface:
    """
    Generate Bedrock icon with green shield overlay.

    Returns:
        48x48 Surface with Bedrock icon and protection shield
    """
    # Start with base sprite
    sprite = generate_bedrock_sprite()

    # Add semi-transparent green shield overlay
    shield_surface = pygame.Surface((48, 48), pygame.SRCALPHA)

    # Draw green circle for shield
    shield_color = (0, 255, 0, 100)  # Semi-transparent green
    pygame.draw.circle(shield_surface, shield_color, (24, 24), 20)

    # Draw shield border
    border_color = (0, 200, 0, 200)  # More opaque green border
    pygame.draw.circle(shield_surface, border_color, (24, 24), 20, 3)

    # Add checkmark in center
    checkmark_color = (0, 255, 0, 255)
    pygame.draw.line(shield_surface, checkmark_color, (16, 24), (22, 30), 3)
    pygame.draw.line(shield_surface, checkmark_color, (22, 30), (32, 18), 3)

    # Blit shield onto sprite
    sprite.blit(shield_surface, (0, 0))

    return sprite


def generate_bedrock_unprotected() -> pygame.Surface:
    """
    Generate Bedrock icon with red warning indicator.

    Returns:
        48x48 Surface with Bedrock icon and warning
    """
    # Start with base sprite
    sprite = generate_bedrock_sprite()

    # Add semi-transparent red warning overlay
    warning_surface = pygame.Surface((48, 48), pygame.SRCALPHA)

    # Draw red triangle for warning
    warning_color = (255, 0, 0, 100)  # Semi-transparent red
    points = [(24, 10), (10, 38), (38, 38)]
    pygame.draw.polygon(warning_surface, warning_color, points)

    # Draw warning border
    border_color = (255, 0, 0, 200)  # More opaque red border
    pygame.draw.polygon(warning_surface, border_color, points, 3)

    # Add exclamation mark in center
    exclaim_color = (255, 0, 0, 255)
    pygame.draw.line(warning_surface, exclaim_color, (24, 18), (24, 28), 3)
    pygame.draw.circle(warning_surface, exclaim_color, (24, 33), 2)

    # Blit warning onto sprite
    sprite.blit(warning_surface, (0, 0))

    return sprite
