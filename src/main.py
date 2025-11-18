"""Main entry point for Sonrai Zombie Blaster."""

import logging
import os
import sys
from typing import List

import pygame
from dotenv import load_dotenv

from models import Vector2, GameStatus
from sonrai_client import SonraiAPIClient
from zombie import Zombie
from game_engine import GameEngine
from renderer import Renderer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_configuration() -> dict:
    """
    Load configuration from environment variables.

    Returns:
        Dictionary of configuration values

    Raises:
        ValueError: If required configuration is missing
    """
    load_dotenv()

    config = {
        'api_url': os.getenv('SONRAI_API_URL'),
        'org_id': os.getenv('SONRAI_ORG_ID'),
        'api_token': os.getenv('SONRAI_API_TOKEN'),
        'game_width': int(os.getenv('GAME_WIDTH', '800')),
        'game_height': int(os.getenv('GAME_HEIGHT', '600')),
        'target_fps': int(os.getenv('TARGET_FPS', '60'))
    }

    # Validate required configuration
    if not config['api_url']:
        raise ValueError("SONRAI_API_URL is required in .env file")
    if not config['org_id']:
        raise ValueError("SONRAI_ORG_ID is required in .env file")
    if not config['api_token']:
        raise ValueError("SONRAI_API_TOKEN is required in .env file")

    return config


def initialize_pygame(width: int, height: int) -> pygame.Surface:
    """
    Initialize Pygame and create the game window.

    Args:
        width: Window width
        height: Window height

    Returns:
        Pygame surface for rendering

    Raises:
        RuntimeError: If Pygame initialization fails
    """
    try:
        pygame.init()
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sonrai Zombie Blaster")
        logger.info(f"Pygame initialized: {width}x{height}")
        return screen
    except pygame.error as e:
        raise RuntimeError(f"Failed to initialize Pygame: {e}")


def fetch_zombies(api_client: SonraiAPIClient, aws_account: str = "577945324761", filter_test_users: bool = True) -> List[Zombie]:
    """
    Fetch unused identities from Sonrai API and create zombie entities.

    Args:
        api_client: Initialized Sonrai API client
        aws_account: AWS account number to filter
        filter_test_users: If True, only include test-user-X identities (default: True)

    Returns:
        List of Zombie entities

    Raises:
        RuntimeError: If API fetch fails
    """
    try:
        logger.info(f"Fetching unused identities from Sonrai API for account {aws_account}...")
        identities = api_client.fetch_unused_identities(limit=1000, scope=None, days_since_login="0", filter_account=aws_account)

        if not identities:
            logger.warning("No unused identities found")
            return []

        # Filter for test-user identities if requested
        if filter_test_users:
            identities = [i for i in identities if 'test-user' in i.identity_name.lower()]
            logger.info(f"Filtered to {len(identities)} test-user identities")

        if not identities:
            logger.warning("No test-user identities found after filtering")
            return []

        # Create zombie entities (one-to-one mapping)
        zombies = []
        for identity in identities:
            # Initial position will be set by distribute_zombies()
            zombie = Zombie(
                identity_id=identity.identity_id,
                identity_name=identity.identity_name,
                position=Vector2(0, 0)
            )
            zombies.append(zombie)

        logger.info(f"Created {len(zombies)} zombie entities")
        return zombies

    except Exception as e:
        raise RuntimeError(f"Failed to fetch unused identities: {e}")


def main():
    """Main game loop."""
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_configuration()

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease create a .env file with the following variables:")
        print("  SONRAI_API_URL=https://crc-graphql-server.sonraisecurity.com/graphql")
        print("  SONRAI_ORG_ID=your_org_id")
        print("  SONRAI_API_TOKEN=your_api_token")
        print("\nSee .env.example for a template.")
        sys.exit(1)

    try:
        # Initialize Pygame
        screen = initialize_pygame(config['game_width'], config['game_height'])

    except RuntimeError as e:
        print(f"\n❌ Pygame Initialization Error: {e}")
        print("\nPlease check your graphics drivers and Pygame installation.")
        sys.exit(1)

    try:
        # Initialize Sonrai API client
        logger.info("Initializing Sonrai API client...")
        api_client = SonraiAPIClient(
            api_url=config['api_url'],
            org_id=config['org_id'],
            api_token=config['api_token']
        )

        # Authenticate
        if not api_client.authenticate():
            raise RuntimeError("Failed to authenticate with Sonrai API")

        # Fetch zombies from myhealth sandbox account
        zombies = fetch_zombies(api_client, aws_account="577945324761")

        if not zombies:
            print("\n🎉 No unused identities found! Your cloud is already secure!")
            pygame.quit()
            sys.exit(0)

    except RuntimeError as e:
        print(f"\n❌ API Connection Error: {e}")
        print("\nPlease check:")
        print("  - Your network connection")
        print("  - Your API credentials in .env")
        print("  - The Sonrai API URL")
        pygame.quit()
        sys.exit(1)

    # Initialize game engine
    logger.info("Initializing game engine...")
    game_engine = GameEngine(
        api_client=api_client,
        zombies=zombies,
        screen_width=config['game_width'],
        screen_height=config['game_height']
    )

    # Distribute zombies across the level
    game_engine.distribute_zombies()

    # Initialize renderer
    renderer = Renderer(screen)

    # Start the game
    game_engine.start()

    # Game loop
    clock = pygame.time.Clock()
    logger.info("Starting game loop...")

    while game_engine.is_running():
        # Calculate delta time
        delta_time = clock.tick(config['target_fps']) / 1000.0

        # Handle input
        events = pygame.event.get()
        game_engine.handle_input(events)

        # Update game state
        game_engine.update(delta_time)

        # Render
        renderer.clear_screen()
        renderer.render_background()

        # Update renderer scroll
        renderer.update_scroll(game_engine.get_scroll_offset() - renderer.scroll_offset)

        # Render game entities
        zombies = game_engine.get_zombies()
        renderer.render_zombies(zombies)
        renderer.render_zombie_labels(zombies)
        renderer.render_projectiles(game_engine.get_projectiles())
        renderer.render_player(game_engine.get_player())
        
        # Debug: Print zombie count on first frame
        if delta_time < 0.1 and len(zombies) > 0:
            logger.info(f"Rendering {len(zombies)} zombies. First 3 positions: {[(z.position.x, z.position.y) for z in zombies[:3]]}")

        # Render UI
        renderer.render_ui(game_engine.get_game_state())

        # Render congratulations message if present
        game_state = game_engine.get_game_state()
        if game_state.status == GameStatus.PAUSED and game_state.congratulations_message:
            renderer.render_message_bubble(game_state.congratulations_message)

        # Update display
        pygame.display.flip()

    # Cleanup
    logger.info("Game ended. Cleaning up...")
    pygame.quit()
    logger.info("Goodbye!")


if __name__ == "__main__":
    main()
