"""Abstract base class for genre-specific game controllers.

Each genre (Platformer, Space Shooter, Maze Chase, Fighting) implements
this interface to provide unique gameplay while maintaining consistent
integration with the game engine.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from models import CONTROL_SCHEMES, ControlScheme, GenreType, Vector2

logger = logging.getLogger(__name__)


@dataclass
class InputState:
    """Current state of player input."""

    # Movement
    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False

    # Actions
    jump: bool = False
    shoot: bool = False
    punch: bool = False
    kick: bool = False
    special: bool = False
    block: bool = False

    # Menu
    pause: bool = False
    confirm: bool = False


class GenreController(ABC):
    """Abstract base class for genre-specific game logic.

    Uses Strategy Pattern to allow different gameplay styles
    while maintaining a consistent interface for the game engine.
    """

    def __init__(self, genre: GenreType, screen_width: int, screen_height: int):
        """Initialize the genre controller.

        Args:
            genre: The genre type this controller handles
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.genre = genre
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.zombies: List = []
        self.is_initialized = False
        self.is_complete = False

        logger.info(f"Created {genre.value} controller")

    @abstractmethod
    def initialize_level(
        self, account_id: str, zombies: List, level_width: int, level_height: int
    ) -> None:
        """Set up level layout and spawn zombies.

        Args:
            account_id: AWS account ID for this level
            zombies: List of zombie entities to place
            level_width: Width of the level
            level_height: Height of the level
        """
        pass

    @abstractmethod
    def update(self, delta_time: float, player) -> None:
        """Update game logic for this genre.

        Args:
            delta_time: Time since last frame in seconds
            player: Player entity
        """
        pass

    @abstractmethod
    def handle_input(self, input_state: InputState, player) -> None:
        """Process player input for this genre.

        Args:
            input_state: Current input state
            player: Player entity to control
        """
        pass

    @abstractmethod
    def check_completion(self) -> bool:
        """Check if level completion conditions are met.

        Returns:
            True if level is complete, False otherwise
        """
        pass

    @abstractmethod
    def render(self, surface, camera_offset: Vector2) -> None:
        """Render genre-specific elements.

        Args:
            surface: Pygame surface to render on
            camera_offset: Camera offset for scrolling
        """
        pass

    def get_control_scheme(self) -> ControlScheme:
        """Return the control scheme for this genre.

        Returns:
            ControlScheme with movement and action mappings
        """
        return CONTROL_SCHEMES.get(self.genre, CONTROL_SCHEMES[GenreType.PLATFORMER])

    def get_zombies(self) -> List:
        """Get the list of zombies in this level.

        Returns:
            List of zombie entities
        """
        return self.zombies

    def get_active_zombie_count(self) -> int:
        """Get count of active (non-eliminated) zombies.

        Returns:
            Number of active zombies
        """
        return len(
            [z for z in self.zombies if not getattr(z, "is_quarantining", False)]
        )

    def on_zombie_eliminated(self, zombie) -> None:
        """Called when a zombie is eliminated.

        Args:
            zombie: The eliminated zombie
        """
        logger.info(
            f"Zombie eliminated in {self.genre.value} mode: {zombie.identity_name}"
        )

    def cleanup(self) -> None:
        """Clean up resources when leaving this genre."""
        self.zombies.clear()
        self.is_initialized = False
        self.is_complete = False
        logger.info(f"Cleaned up {self.genre.value} controller")


class GenreControllerFactory:
    """Factory for creating genre controllers."""

    _controllers = {}

    @classmethod
    def register(cls, genre: GenreType, controller_class: type) -> None:
        """Register a controller class for a genre.

        Args:
            genre: The genre type
            controller_class: The controller class to use
        """
        cls._controllers[genre] = controller_class
        logger.info(f"Registered controller for {genre.value}")

    @classmethod
    def create(
        cls, genre: GenreType, screen_width: int, screen_height: int
    ) -> Optional[GenreController]:
        """Create a controller for the specified genre.

        Args:
            genre: The genre type
            screen_width: Screen width
            screen_height: Screen height

        Returns:
            GenreController instance or None if genre not registered
        """
        controller_class = cls._controllers.get(genre)
        if controller_class:
            return controller_class(genre, screen_width, screen_height)

        logger.warning(f"No controller registered for {genre.value}")
        return None

    @classmethod
    def get_registered_genres(cls) -> List[GenreType]:
        """Get list of genres with registered controllers.

        Returns:
            List of registered genre types
        """
        return list(cls._controllers.keys())
