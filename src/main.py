"""Main entry point for Sonrai Zombie Blaster."""

import logging
import os
import sys
from typing import List, Optional

import pygame
from dotenv import load_dotenv

# Pre-initialize camera BEFORE pygame to avoid macOS conflicts
_pre_initialized_camera = None


def _pre_init_camera() -> Optional[object]:
    """
    Pre-initialize camera before pygame to avoid macOS AVFoundation conflicts.

    On macOS, pygame's video initialization can interfere with OpenCV camera access.
    By opening the camera first and keeping it open, we avoid this issue.

    Returns:
        OpenCV VideoCapture object if successful, None otherwise
    """
    global _pre_initialized_camera
    try:
        import cv2

        print("📷 PRE-INIT: Opening camera before pygame...")
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                print("📷 PRE-INIT: Camera opened successfully!")
                _pre_initialized_camera = cap
                return cap
            else:
                print("📷 PRE-INIT: Camera opened but read failed")
                cap.release()
        else:
            print("📷 PRE-INIT: Failed to open camera")
    except ImportError:
        print("📷 PRE-INIT: OpenCV not available")
    except Exception as e:
        print(f"📷 PRE-INIT: Error - {e}")
    return None


# Pre-init camera immediately on module load (before pygame.init)
_pre_init_camera()

from game_engine import GameEngine
from level_manager import LevelManager
from models import GameStatus, Vector2
from renderer import Renderer
from save_manager import SaveManager
from sonrai_client import SonraiAPIClient
from zombie import Zombie

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
        "api_url": os.getenv("SONRAI_API_URL"),
        "org_id": os.getenv("SONRAI_ORG_ID"),
        "api_token": os.getenv("SONRAI_API_TOKEN"),
        "game_width": int(os.getenv("GAME_WIDTH", "1280")),  # Base rendering resolution
        "game_height": int(os.getenv("GAME_HEIGHT", "720")),
        "fullscreen": os.getenv("FULLSCREEN", "false").lower()
        == "true",  # Fullscreen mode
        "target_fps": int(os.getenv("TARGET_FPS", "60")),
        "max_zombies": int(
            os.getenv("MAX_ZOMBIES", "1000")
        ),  # Default to 1000 to capture all API zombies
    }

    # Validate required configuration
    if not config["api_url"]:
        raise ValueError("SONRAI_API_URL is required in .env file")
    if not config["org_id"]:
        raise ValueError("SONRAI_ORG_ID is required in .env file")
    if not config["api_token"]:
        raise ValueError("SONRAI_API_TOKEN is required in .env file")

    return config


def calculate_scaled_dimensions(
    game_width: int, game_height: int, display_width: int, display_height: int
) -> tuple[int, int, int, int]:
    """
    Calculate scaled dimensions with aspect ratio preservation (letterboxing/pillarboxing).

    Args:
        game_width: Base game rendering width
        game_height: Base game rendering height
        display_width: Display/window width
        display_height: Display/window height

    Returns:
        Tuple of (scaled_width, scaled_height, offset_x, offset_y)
    """
    game_aspect = game_width / game_height
    display_aspect = display_width / display_height

    if display_aspect > game_aspect:
        # Display is wider - pillarbox (black bars on sides)
        scaled_height = display_height
        scaled_width = int(scaled_height * game_aspect)
        offset_x = (display_width - scaled_width) // 2
        offset_y = 0
    else:
        # Display is taller - letterbox (black bars on top/bottom)
        scaled_width = display_width
        scaled_height = int(scaled_width / game_aspect)
        offset_x = 0
        offset_y = (display_height - scaled_height) // 2

    return scaled_width, scaled_height, offset_x, offset_y


def initialize_pygame(
    width: int, height: int, fullscreen: bool = False
) -> tuple[pygame.Surface, pygame.Surface]:
    """
    Initialize Pygame and create the game window with display scaling.

    Args:
        width: Base game rendering width
        height: Base game rendering height
        fullscreen: Whether to start in fullscreen mode

    Returns:
        Tuple of (display_surface, game_surface)
        - display_surface: The actual window/screen (scaled)
        - game_surface: Internal rendering surface (base resolution)

    Raises:
        RuntimeError: If Pygame initialization fails
    """
    try:
        pygame.init()

        # Initialize controller detection EARLY (before any other initialization)
        pygame.joystick.init()
        controller_count = pygame.joystick.get_count()
        if controller_count > 0:
            logger.info(f"🎮 Detected {controller_count} controller(s)")
            for i in range(controller_count):
                joy = pygame.joystick.Joystick(i)
                joy.init()
                logger.info(f"   Controller {i}: {joy.get_name()}")
        else:
            logger.info("⌨️  No controllers detected, keyboard input available")

        # Create display surface (fullscreen or windowed)
        if fullscreen:
            # Get native screen resolution
            display_info = pygame.display.Info()
            display = pygame.display.set_mode(
                (display_info.current_w, display_info.current_h), pygame.FULLSCREEN
            )
            logger.info(
                f"Fullscreen mode: {display_info.current_w}x{display_info.current_h}"
            )
        else:
            # Windowed mode - make it resizable for macOS menu options
            display = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            logger.info(f"Windowed mode: {width}x{height}")

        pygame.display.set_caption("Sonrai Zombie Blaster")

        # Create internal game surface at base resolution
        game_surface = pygame.Surface((width, height))
        logger.info(f"Game rendering surface: {width}x{height}")

        return display, game_surface
    except pygame.error as e:
        raise RuntimeError(f"Failed to initialize Pygame: {e}")


def fetch_zombies(
    api_client: SonraiAPIClient,
    aws_account: str = "577945324761",
    filter_test_users: bool = True,
    max_zombies: int = 1000,
    quarantined_identities: set = None,
) -> List[Zombie]:
    """
    Fetch unused identities from Sonrai API and create zombie entities.

    Args:
        api_client: Initialized Sonrai API client
        aws_account: AWS account number to filter
        filter_test_users: If True, only include test-user-X identities (default: True)
        max_zombies: Maximum number of zombies to create (default: 1000, configurable via MAX_ZOMBIES env var)
        quarantined_identities: Set of identity IDs that have been quarantined (to exclude from loading)

    Returns:
        List of Zombie entities

    Raises:
        RuntimeError: If API fetch fails
    """
    try:
        if quarantined_identities is None:
            quarantined_identities = set()

        logger.info(
            f"Fetching unused identities from Sonrai API for account {aws_account}..."
        )
        identities = api_client.fetch_unused_identities(
            limit=1000, scope=None, days_since_login="0", filter_account=aws_account
        )

        logger.info(f"Received {len(identities)} total identities from API")

        if not identities:
            logger.warning("No unused identities found")
            return []

        # Filter out quarantined identities (from save file)
        if quarantined_identities:
            before_filter = len(identities)
            identities = [
                i for i in identities if i.identity_id not in quarantined_identities
            ]
            filtered_count = before_filter - len(identities)
            if filtered_count > 0:
                logger.info(
                    f"Filtered out {filtered_count} quarantined identities from save file"
                )

        # Filter for test-user identities if requested
        if filter_test_users:
            before_filter = len(identities)
            identities = [
                i for i in identities if "test-user" in i.identity_name.lower()
            ]
            logger.info(
                f"Filtered from {before_filter} to {len(identities)} test-user identities"
            )

        if not identities:
            logger.warning("No test-user identities found after filtering")
            return []

        # Limit to max_zombies for better gameplay
        if len(identities) > max_zombies:
            logger.info(
                f"Would limit from {len(identities)} to {max_zombies} zombies, but applying limit..."
            )
            identities = identities[:max_zombies]
            logger.info(f"Limited to {max_zombies} zombies for optimal gameplay")
        else:
            logger.info(
                f"Using all {len(identities)} identities (under max_zombies limit of {max_zombies})"
            )

        # Create zombie entities (one-to-one mapping)
        zombies = []
        for identity in identities:
            # Initial position will be set by distribute_zombies()
            zombie = Zombie(
                identity_id=identity.identity_id,
                identity_name=identity.identity_name,
                position=Vector2(0, 0),
                account=aws_account,
                scope=identity.scope,  # Pass scope from API
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
        # Initialize Pygame with fullscreen support
        display, game_surface = initialize_pygame(
            config["game_width"], config["game_height"], config["fullscreen"]
        )
        is_fullscreen = config["fullscreen"]

    except RuntimeError as e:
        print(f"\n❌ Pygame Initialization Error: {e}")
        print("\nPlease check your graphics drivers and Pygame installation.")
        sys.exit(1)

    try:
        # Check for existing save file
        save_manager = SaveManager()
        save_data = save_manager.load_game()
        quarantined_identities = set()

        if save_data:
            logger.info("🎮 Found existing save file! Loading progress...")
            quarantined_identities = set(save_data.get("quarantined_identities", []))
            save_info = save_manager.get_save_info()
            if save_info:
                logger.info(f"   Last saved: {save_info['last_saved']}")
                logger.info(f"   Score: {save_info['score']}")
                logger.info(f"   Eliminations: {save_info['eliminations']}")
                logger.info(f"   Completed levels: {save_info['completed_levels']}")
        else:
            logger.info("🆕 No save file found. Starting new game...")

        # Initialize Sonrai API client
        logger.info("Initializing Sonrai API client...")
        api_client = SonraiAPIClient(
            api_url=config["api_url"],
            org_id=config["org_id"],
            api_token=config["api_token"],
        )

        # Authenticate
        if not api_client.authenticate():
            raise RuntimeError("Failed to authenticate with Sonrai API")

        # Fetch accounts and their zombie counts
        logger.info("Fetching AWS accounts from Sonrai API...")
        account_data = api_client.fetch_accounts_with_unused_identities()

        if not account_data:
            print("\n🎉 No unused identities found! Your cloud is already secure!")
            pygame.quit()
            sys.exit(0)

        # Log account information
        logger.info(f"Found {len(account_data)} AWS accounts:")
        for account, count in sorted(
            account_data.items(), key=lambda x: x[1], reverse=True
        ):
            logger.info(f"  {account}: {count} zombies")

        # Initialize level manager
        logger.info("Initializing level manager...")
        try:
            # Get the project root (parent of src/)
            src_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(src_dir)
            csv_path = os.path.join(project_root, "assets", "aws_accounts.csv")
            level_manager = LevelManager(csv_path)
            logger.info(f"Loaded {len(level_manager.levels)} levels")
        except Exception as e:
            logger.error(f"Failed to initialize level manager: {e}")
            level_manager = None

        # Fetch 3rd party access information (MyHealth organization)
        logger.info("Fetching 3rd party access from Sonrai API...")
        third_party_data = api_client.fetch_third_parties_by_account(
            root_scope="aws/r-ipxz"
        )
        logger.info(f"Found 3rd parties in {len(third_party_data)} accounts")
        for account, parties in third_party_data.items():
            if parties:
                logger.info(
                    f"  Account {account}: {len(parties)} 3rd parties - {', '.join([p['name'] for p in parties[:3]])}{'...' if len(parties) > 3 else ''}"
                )

        # Fetch zombies from ALL AWS accounts (for level loading)
        all_zombies = []
        for account_num, zombie_count in account_data.items():
            if zombie_count > 0:
                logger.info(
                    f"Fetching {zombie_count} zombies from account {account_num}..."
                )
                try:
                    account_zombies = fetch_zombies(
                        api_client,
                        aws_account=account_num,
                        filter_test_users=False,
                        max_zombies=zombie_count,  # Fetch exact number for this account
                        quarantined_identities=quarantined_identities,  # Filter out quarantined identities
                    )
                    all_zombies.extend(account_zombies)
                    logger.info(
                        f"  -> Added {len(account_zombies)} zombies from account {account_num}"
                    )
                except Exception as e:
                    logger.warning(
                        f"  -> Failed to fetch zombies from account {account_num}: {e}"
                    )
                    continue

        zombies = all_zombies
        logger.info(f"Total zombies across all accounts: {len(zombies)}")

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

    # Initialize game engine (starts in LOBBY mode)
    logger.info("Initializing game engine...")
    game_engine = GameEngine(
        api_client=api_client,
        zombies=zombies,  # All zombies (will be filtered by level when entering levels)
        screen_width=config["game_width"],
        screen_height=config["game_height"],
        account_data=account_data,
        third_party_data=third_party_data,
        level_manager=level_manager,
    )

    # Restore game state from save file (if exists)
    if save_data:
        logger.info("Restoring game state from save file...")
        game_engine.restore_game_state(save_data)

    # Don't distribute zombies - we start in lobby mode with no zombies
    # Zombies will be loaded when entering levels

    # Initialize renderer
    # Initialize renderer with game surface (not display)
    renderer = Renderer(game_surface)

    # Connect renderer to game engine for photo booth capture
    game_engine.renderer = renderer

    # Start the game
    game_engine.start()

    # Game loop
    clock = pygame.time.Clock()
    logger.info("Starting game loop...")

    while game_engine.is_running():
        # Calculate delta time
        delta_time = clock.tick(config["target_fps"]) / 1000.0

        # Handle input
        events = pygame.event.get()

        # Handle fullscreen toggle and window resize events
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Check for fullscreen toggle keys
                is_toggle = (
                    event.key == pygame.K_F11  # F11
                    or event.key == pygame.K_f  # F key
                    or (
                        event.key == pygame.K_f and (event.mod & pygame.KMOD_META)
                    )  # CMD+F on macOS
                )

                if is_toggle:
                    is_fullscreen = not is_fullscreen
                    logger.info(
                        f"Fullscreen toggle detected! Switching to: {'FULLSCREEN' if is_fullscreen else 'WINDOWED'}"
                    )

                    # Recreate display with new mode
                    display, game_surface = initialize_pygame(
                        config["game_width"], config["game_height"], is_fullscreen
                    )
                    # Update renderer with new game surface
                    renderer.screen = game_surface
                    logger.info(f"Display mode changed successfully")

            elif event.type == pygame.VIDEORESIZE:
                # Window was resized (by user or macOS menu)
                logger.info(f"Window resized to: {event.w}x{event.h}")
                # Update display size but keep game_surface at base resolution
                display = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        game_engine.handle_input(events, game_surface)

        # Update game state
        game_engine.update(delta_time)

        # Render
        renderer.clear_screen()

        # Get game map (if using map mode)
        game_map = game_engine.get_game_map()

        # Check if we're in a special genre mode that handles its own rendering
        from models import GenreType

        game_state = game_engine.get_game_state()
        is_space_shooter = (
            game_state.current_genre == GenreType.SPACE_SHOOTER
            and game_engine.active_genre_controller
        )
        is_racing = (
            game_state.current_genre == GenreType.RACING
            and game_engine.active_genre_controller
        )
        is_special_genre = is_space_shooter or is_racing

        # Render background (map or grid) - skip for special genres that render their own
        if is_special_genre:
            # Special genres handle their own background rendering
            pass  # Background rendered by controller
        else:
            renderer.render_background(game_map)

            # Render flashing lightning (platformer mode only)
            renderer.render_lightning(game_map, delta_time, game_state.play_time)

            # Render doors (if using map mode)
            if game_map and hasattr(game_map, "doors"):
                renderer.render_doors(game_map.doors, game_map)

            # Render collectibles (if using map mode)
            if game_map and hasattr(game_map, "collectibles"):
                renderer.render_collectibles(game_map.collectibles, game_map)

            # Render powerups (AWS-themed power-ups)
            powerups = game_engine.get_powerups()
            if powerups and game_map:
                renderer.render_powerups(powerups, game_map)

        # Update renderer scroll (classic mode only)
        if not game_map:
            renderer.update_scroll(
                game_engine.get_scroll_offset() - renderer.scroll_offset
            )

        # Render game entities (skip in special genre modes - they handle their own rendering)
        zombies = game_engine.get_zombies()
        if not is_special_genre:
            renderer.render_zombies(zombies, game_map)
            renderer.render_zombie_labels(zombies, game_map)

            # Render health bars for zombies (skip hidden zombies)
            for zombie in zombies:
                if not zombie.is_hidden:
                    renderer.render_health_bar(zombie, game_map)

        # Render 3rd parties (skip in special genre modes)
        if not is_special_genre:
            third_parties = game_engine.get_third_parties()
            renderer.render_third_parties(third_parties, game_map)
            renderer.render_third_party_labels(third_parties, game_map)

            # Render health bars for 3rd parties
            for third_party in third_parties:
                renderer.render_health_bar(third_party, game_map)

            # Render purple shields for protected 3rd parties
            for third_party in third_parties:
                if third_party.is_protected:
                    renderer.render_shield(third_party, game_map, game_state.play_time)

            renderer.render_projectiles(game_engine.get_projectiles(), game_map)

            # Render normal player
            renderer.render_player(game_engine.get_player(), game_map)
        else:
            # Special genre mode - the controller handles ALL rendering
            # Pass player for controllers that render custom player (like WALLy in maze chase)
            player = game_engine.get_player()
            if hasattr(game_engine.active_genre_controller, "render"):
                # Try to pass player if the render method accepts it
                try:
                    game_engine.active_genre_controller.render(
                        renderer.screen, Vector2(0, 0), player
                    )
                except TypeError:
                    # Fallback for controllers that don't accept player parameter
                    game_engine.active_genre_controller.render(
                        renderer.screen, Vector2(0, 0)
                    )

        # Render boss if in boss battle
        boss = game_engine.get_boss()
        if boss:
            # Import cyber boss types for type checking
            from cyber_boss import HeartbleedBoss, ScatteredSpiderBoss, WannaCryBoss

            # Render appropriate boss type
            if isinstance(boss, ScatteredSpiderBoss):
                renderer.render_scattered_spider(boss, game_map)
            elif isinstance(boss, HeartbleedBoss):
                renderer.render_heartbleed_boss(boss, game_map)
            elif isinstance(boss, WannaCryBoss):
                renderer.render_wannacry_boss(boss, game_map)
            else:
                renderer.render_boss(boss, game_map)

            # Render health bar for all boss types
            renderer.render_boss_health_bar(boss, game_map)

        # Render service protection quest elements
        if game_map and game_map.mode == "platformer":
            # Render service nodes (Bedrock icons)
            service_nodes = game_engine.get_service_nodes()
            if service_nodes:
                renderer.render_service_nodes(
                    service_nodes, game_map, game_state.play_time
                )

            # Render hacker character
            hacker = game_engine.get_hacker()
            if hacker:
                renderer.render_hacker(hacker, game_map)

            # Render race timer and quest messages
            active_quest = game_engine.get_active_quest()
            if active_quest:
                # Render countdown timer
                renderer.render_race_timer(
                    active_quest.time_remaining, active_quest.status
                )

                # Render quest warning message
                if game_state.quest_message and game_state.quest_message_timer > 0:
                    renderer.render_message_bubble(game_state.quest_message)

            # Render service hint
            if game_state.service_hint_message and game_state.service_hint_timer > 0:
                renderer.render_service_hint(
                    game_state.service_hint_message, game_state.service_hint_timer
                )

        # Render JIT Access Quest elements
        if (
            game_state.status == GameStatus.PLAYING
            and game_state.jit_quest
            and game_state.jit_quest.active
        ):
            # Render auditor
            auditor = game_engine.auditor
            if auditor:
                renderer.render_auditor(auditor, game_map)

            # Render admin roles
            admin_roles = game_engine.admin_roles
            if admin_roles:
                renderer.render_admin_roles(admin_roles, game_map, game_state.play_time)

            # Render JIT quest messages
            renderer.render_jit_quest_message(game_state.jit_quest)

        # Render UI (including player health)
        player = game_engine.get_player()
        renderer.render_ui(game_state, player)

        # Render minimap (if using map mode, but not in platformer levels or landing zone view)
        if (
            game_map
            and game_map.mode != "platformer"
            and not game_map.landing_zone_view
        ):
            renderer.render_minimap(game_map, player.position, zombies)

        # Render landing zone overlay (if in landing zone view)
        if game_map and game_map.landing_zone_view:
            renderer.render_landing_zone_overlay(game_map)

        # Render production outage overlay (if active)
        if game_state.status == GameStatus.PLAYING:
            outage_state = game_engine.outage_manager.get_state()
            if outage_state.active:
                renderer.render_production_outage(outage_state)

        # Render boss dialogue if showing
        if game_engine.showing_boss_dialogue and game_engine.boss_dialogue_content:
            renderer.render_boss_dialogue(game_engine.boss_dialogue_content)

        # Render educational dialogue if active (Story Mode)
        if game_state.is_dialogue_active:
            renderer.render_educational_dialogue(
                game_engine.dialogue_renderer,
                game_state,
            )

        # Render photo booth summary screen if active (takes over entire screen)
        if (
            getattr(game_state, "photo_booth_summary_active", False)
            and game_state.photo_booth_path
        ):
            renderer.render_photo_booth_summary(game_state.photo_booth_path)
        # Render congratulations message if present (not while photo booth summary is showing)
        elif (
            game_state.status == GameStatus.PAUSED
            and game_state.congratulations_message
        ):
            renderer.render_message_bubble(game_state.congratulations_message)

        # Evidence capture - frame capture and visual feedback
        current_time = pygame.time.get_ticks() / 1000.0
        game_engine.evidence_capture.capture_frame(game_surface, current_time)
        game_engine.evidence_capture.update_flash(delta_time)
        game_engine.evidence_capture.render_recording_indicator(
            game_surface, current_time
        )

        # Process any pending screenshot BEFORE flash overlay (capture clean frame)
        game_engine.evidence_capture.process_pending_screenshot(game_surface)

        # Render flash overlay AFTER screenshot capture
        game_engine.evidence_capture.render_flash(game_surface)

        # Scale and display game surface with aspect ratio preservation
        if is_fullscreen or display.get_size() != game_surface.get_size():
            # Calculate scaled dimensions with letterboxing/pillarboxing
            display_width, display_height = display.get_size()
            scaled_width, scaled_height, offset_x, offset_y = (
                calculate_scaled_dimensions(
                    config["game_width"],
                    config["game_height"],
                    display_width,
                    display_height,
                )
            )

            # Clear display (black background for letterboxing)
            display.fill((0, 0, 0))

            # Scale game surface and blit to display
            scaled_surface = pygame.transform.scale(
                game_surface, (scaled_width, scaled_height)
            )
            display.blit(scaled_surface, (offset_x, offset_y))
        else:
            # Windowed mode at native resolution - direct blit
            display.blit(game_surface, (0, 0))

        # Update display
        pygame.display.flip()

    # Cleanup
    logger.info("Game ended. Cleaning up...")
    pygame.quit()
    logger.info("Goodbye!")


if __name__ == "__main__":
    main()
