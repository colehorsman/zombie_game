"""Purple shield rendering for protected entities."""

import pygame
import math


def create_small_shield_sprite() -> pygame.Surface:
    """
    Create a solid dark purple shield sprite for left arm.

    Returns:
        Pygame surface with the shield sprite (covers left arm)
    """
    # Shield dimensions - proper shield shape
    shield_width = 18
    shield_height = 24
    shield = pygame.Surface((shield_width, shield_height), pygame.SRCALPHA)

    # Solid dark purple - no transparency
    PURPLE_DARK = (100, 30, 150)  # Solid dark purple
    PURPLE_BORDER = (70, 20, 110)  # Even darker border
    PURPLE_HIGHLIGHT = (130, 50, 180)  # Slight highlight

    # Create shield shape using polygon (rounded top, pointed bottom)
    # Define shield outline points
    shield_points = [
        (shield_width // 2, 2),  # Top center
        (shield_width - 3, 4),  # Top right
        (shield_width - 2, shield_height // 2),  # Middle right
        (shield_width // 2, shield_height - 2),  # Bottom point
        (2, shield_height // 2),  # Middle left
        (3, 4),  # Top left
    ]

    # Draw solid shield shape
    pygame.draw.polygon(shield, PURPLE_DARK, shield_points)

    # Add a center vertical highlight line
    pygame.draw.line(
        shield,
        PURPLE_HIGHLIGHT,
        (shield_width // 2, 4),
        (shield_width // 2, shield_height - 4),
        2,
    )

    # Draw thick border
    pygame.draw.polygon(shield, PURPLE_BORDER, shield_points, 2)

    return shield


def render_shield(
    surface: pygame.Surface,
    entity,
    camera_offset: tuple = (0, 0),
    pulse_time: float = 0.0,
):
    """
    Render a small purple shield on the entity's left arm.

    Args:
        surface: Surface to render to
        entity: Entity to protect (must have position, width, height)
        camera_offset: Camera offset for map mode (camera_x, camera_y)
        pulse_time: Time value for pulsing animation
    """
    # Calculate screen position
    screen_x = int(entity.position.x - camera_offset[0])
    screen_y = int(entity.position.y - camera_offset[1])

    # Create shield if not cached
    if not hasattr(entity, "_shield_sprite"):
        entity._shield_sprite = create_small_shield_sprite()

    # No transparency - solid shield
    shield_to_render = entity._shield_sprite

    # Position shield on left arm (covering the briefcase/left side)
    shield_x = screen_x - 4  # Slightly left of entity to cover left arm
    shield_y = screen_y + entity.height // 2 - 2  # Center vertically on arm

    # Render solid shield
    surface.blit(shield_to_render, (shield_x, shield_y))
