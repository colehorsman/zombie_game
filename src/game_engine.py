"""Core game engine and game loop."""

import logging
import threading
import time
from typing import List, Optional, Union

import pygame

from approval import ApprovalManager
from arcade_mode import ArcadeModeManager
from arcade_results_controller import (
    ArcadeResultsAction,
    ArcadeResultsController,
    ArcadeStatsSnapshot,
)
from aws_iam_client import AWSIAMClient
from boss import Boss  # DEPRECATED - kept for backwards compatibility
from boss_dialogue_controller import BossDialogueController
from cheat_code_controller import CheatCodeAction, CheatCodeController
from collision import SpatialGrid, check_collisions_with_spatial_grid
from combo_tracker import ComboTracker
from cyber_boss import (
    BOSS_LEVEL_MAP,
    BossType,
    HeartbleedBoss,
    ScatteredSpiderBoss,
    WannaCryBoss,
    create_cyber_boss,
    get_boss_dialogue,
)

# Educational dialogue system for Story Mode
from dialogue_renderer import DialogueRenderer
from difficulty_config import EnvironmentDifficulty, get_difficulty_for_environment
from education_manager import EducationManager
from evidence_capture import EvidenceCapture
from game_map import GameMap

# Genre selection removed - using static level-to-genre mapping instead
from hacker import Hacker
from jit_access_quest import AdminRole, Auditor, create_jit_quest_entities
from level_entry_menu_controller import LevelEntryAction, LevelEntryMenuController
from level_manager import LevelManager
from models import (
    GameState,
    GameStatus,
    GenreType,
    JitQuestState,
    PermissionSet,
    TriggerType,
    Vector2,
)
from pause_menu_controller import PauseMenuAction, PauseMenuController
from player import Player
from powerup import PowerUp, PowerUpManager, PowerUpType, spawn_random_powerups
from production_outage import ProductionOutageManager
from projectile import Projectile
from reinvent_stats_tracker import record_arcade_session
from save_manager import SaveManager
from service_protection_quest import (
    SERVICE_ICON_Y,
    ServiceNode,
    ServiceProtectionQuestManager,
    create_bedrock_protection_quest,
    create_service_node,
)
from sonrai_client import SonraiAPIClient
from zombie import Zombie

# Photo booth for arcade mode selfies
try:
    from photo_booth import PhotoBoothController, PhotoBoothState

    PHOTO_BOOTH_AVAILABLE = True
    print(f"📸 PHOTO BOOTH IMPORT SUCCESS: {PhotoBoothController}, {PhotoBoothState}")
except ImportError as e:
    PHOTO_BOOTH_AVAILABLE = False
    PhotoBoothController = None
    PhotoBoothState = None
    print(f"📸 PHOTO BOOTH IMPORT FAILED: {e}")

logger = logging.getLogger(__name__)


class GameEngine:
    """Core game loop and state management."""

    def __init__(
        self,
        api_client: SonraiAPIClient,
        zombies: List[Zombie],
        screen_width: int,
        screen_height: int,
        use_map: bool = True,
        account_data: dict = None,
        third_party_data: dict = None,
        level_manager: LevelManager = None,
        difficulty: EnvironmentDifficulty = None,
        approval_manager: ApprovalManager = None,
    ):
        """
        Initialize the game engine.

        Args:
            api_client: Sonrai API client for quarantine operations
            zombies: Initial list of zombie entities
            screen_width: Width of the game screen
            screen_height: Height of the game screen
            use_map: Whether to use map-based navigation (True) or classic scrolling (False)
            account_data: Dictionary of AWS accounts and zombie counts
            third_party_data: Dictionary of 3rd party access by account
            level_manager: Level progression manager
            difficulty: Difficulty configuration for current level
            approval_manager: Manager for approval collectibles (production environments)
        """
        self.api_client = api_client
        self.all_zombies = zombies  # Store all zombies (for level loading)
        self.zombies = []  # Active zombies (empty in lobby, populated in level)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.use_map = use_map
        self.level_manager = level_manager
        self.difficulty = difficulty
        self.approval_manager = approval_manager
        self.account_data = account_data or {}
        self.third_party_data = third_party_data or {}

        # Initialize game map if enabled (LOBBY mode - main branch style)
        if use_map:
            # LOBBY MODE: Use main branch style (no reveal_radius, no api_client in GameMap)
            self.game_map = GameMap(
                "assets/reinvent_floorplan.png",
                screen_width,
                screen_height,
                account_data,
                third_party_data,
            )

            # LOBBY: Distribute all zombies across rooms (visible in lobby, like main branch)
            # This allows players to see zombies in rooms before entering
            if zombies:
                self.zombies = zombies  # Show all zombies in lobby
                self.game_map.scatter_zombies(self.zombies)
                # Make zombies visible in lobby (they're hidden by default)
                for zombie in self.zombies:
                    zombie.is_hidden = False
                logger.info(f"🏛️  Distributed {len(self.zombies)} zombies across lobby rooms")

            # LOBBY: Spawn player in far top-left corner (open lobby area)
            # Future: This will be the AWS Control Tower location
            # Map is 3600x2700, spawn at top-left in open space
            self.landing_zone = Vector2(
                100,  # Far left, in open lobby area
                150,  # Top area, below any header text
            )
            player_start_pos = self.landing_zone
            logger.info(
                f"🏛️  Spawning player at LOBBY safe zone (top-left) ({player_start_pos.x}, {player_start_pos.y})"
            )
            self.player = Player(
                player_start_pos,
                self.game_map.map_width,
                self.game_map.map_height,
                self.game_map,
            )

            # Spatial grid for entire map
            self.spatial_grid = SpatialGrid(self.game_map.map_width, self.game_map.map_height)
        else:
            self.game_map = None
            self.landing_zone = Vector2(screen_width // 2, screen_height // 2)
            # Classic mode - initialize player on screen
            player_start_pos = Vector2(50, screen_height // 2 - 16)
            self.player = Player(player_start_pos, screen_width, screen_height)

            # Spatial grid for screen
            self.spatial_grid = SpatialGrid(screen_width, screen_height)

        # Game entities
        self.projectiles: List[Projectile] = []

        # AWS-themed power-ups
        self.powerup_manager = PowerUpManager()
        self.powerups: List[PowerUp] = []

        # Star Power - instant quarantine on touch (like projectiles)
        self.star_power_touched_zombies = (
            set()
        )  # Track which zombies we've already touched during current Star Power
        self.star_power_was_active = False  # Track when Star Power ends to clear touched set

        # Arcade Mode
        self.arcade_manager = ArcadeModeManager()
        self.combo_tracker = ComboTracker()

        # Count 3rd parties
        third_parties_count = 0
        if use_map and self.game_map and hasattr(self.game_map, "third_parties"):
            third_parties_count = len(self.game_map.third_parties)

        # Get level info
        current_level = level_manager.get_current_level() if level_manager else None
        level_number = current_level.level_number if current_level else 1
        environment_type = current_level.environment_type if current_level else "sandbox"

        # Game state - START IN LOBBY MODE
        # In lobby, zombies are visible but not interactive (they're in rooms)
        lobby_zombie_count = len(zombies) if zombies else 0
        self.game_state = GameState(
            status=GameStatus.LOBBY,  # Start in lobby mode
            zombies_remaining=lobby_zombie_count,  # Total zombies visible in lobby
            zombies_quarantined=0,
            total_zombies=lobby_zombie_count,  # Total zombies in lobby
            third_parties_blocked=0,
            total_third_parties=third_parties_count,
            current_level=level_number if level_manager else 1,
            environment_type=environment_type if level_manager else "lobby",
        )

        # Track which level account IDs have been completed
        self.completed_level_account_ids = set()

        # Save/load game state
        self.save_manager = SaveManager()
        self.quarantined_identities = set()  # Track identity IDs that have been quarantined
        self.blocked_third_parties = set()  # Track third-party names that have been blocked

        # Evidence capture (screenshots & recordings)
        self.evidence_capture = EvidenceCapture()
        self.last_autosave_time = 0.0  # Track last autosave for periodic saves
        self.autosave_interval = 30.0  # Autosave every 30 seconds

        # Cheat code system - now managed by CheatCodeController
        self.cheat_code_controller = CheatCodeController()

        # Door interaction cooldown (prevents immediate re-entry after returning to lobby)
        self.door_interaction_cooldown = 0.0  # Seconds remaining before doors can be entered

        # Timing
        self.start_time = time.time()
        self.running = True

        # Input state
        self.keys_pressed = set()

        # Controller support (8-bit style with hot-plug support)
        pygame.joystick.init()
        self.joystick = None

        # Initialize controller with retry logic
        # Sometimes controllers aren't immediately recognized on startup
        self._init_controller_with_retry()

        # Scrolling (only for classic mode)
        self.scroll_speed = 50.0  # pixels per second
        self.scroll_offset = 0.0

        # Boss battle (supports both old Boss and new cyber bosses)
        self.boss: Optional[Union[Boss, ScatteredSpiderBoss, HeartbleedBoss, WannaCryBoss]] = None
        self.boss_spawned = False
        self.boss_type: Optional[BossType] = None

        # Boss dialogue system - now managed by BossDialogueController
        self.boss_dialogue_controller = BossDialogueController()

        # Pause menu (Zelda-style) - now managed by PauseMenuController
        self.pause_menu_controller = PauseMenuController()

        # Arcade results menu - now managed by ArcadeResultsController
        self.arcade_results_controller = ArcadeResultsController()

        # Level entry mode selector - shows when entering levels (Arcade vs Story mode)
        import os

        level_entry_enabled = (
            os.getenv("LEVEL_ENTRY_MODE_SELECTOR_ENABLED", "true").lower() == "true"
        )
        default_level_entry_mode = os.getenv("DEFAULT_LEVEL_ENTRY_MODE", "arcade")
        # AUTO_START_ARCADE: Skip menu and go directly to arcade mode for Sandbox
        self.auto_start_arcade = os.getenv("AUTO_START_ARCADE", "true").lower() == "true"
        self.level_entry_menu_controller = LevelEntryMenuController(
            enabled=level_entry_enabled, default_mode=default_level_entry_mode
        )
        self._pending_door_entry = None  # Door waiting for mode selection

        # Static genre mapping per level (Option B - no selection menu)
        from models import GenreType

        self.LEVEL_GENRE_MAP = {
            1: GenreType.SPACE_SHOOTER,  # Sandbox - space invaders style
            2: GenreType.SPACE_SHOOTER,  # Stage - space invaders style
            3: GenreType.MAZE_CHASE,  # Automation - navigate pipelines
            4: GenreType.PLATFORMER,  # WebApp - standard platformer
            5: GenreType.RACING,  # Production Data - Mario Kart style racing!
            6: GenreType.FIGHTING,  # Production - boss battle!
            7: GenreType.PLATFORMER,  # Org - standard
        }
        self.active_genre_controller = None  # Active genre controller for current level
        self._pending_story_mode = False  # Track if story mode was selected
        logger.info(f"🕹️ AUTO_START_ARCADE = {self.auto_start_arcade}")

        # Photo booth for arcade mode selfies
        self.photo_booth = None
        self._pending_arcade_stats = None  # Stats pending while photo booth summary is shown
        self.renderer = None  # Set by main.py after creation for photo booth capture
        print(f"📸 PHOTO_BOOTH_AVAILABLE = {PHOTO_BOOTH_AVAILABLE}")
        if PHOTO_BOOTH_AVAILABLE:
            self.photo_booth = PhotoBoothController()
            self.photo_booth.initialize()
            print(
                f"📸 Photo booth initialized: state={self.photo_booth.state}, "
                f"camera_available={self.photo_booth.is_camera_available}, "
                f"webcam_open={self.photo_booth._webcam is not None and self.photo_booth._webcam.isOpened() if self.photo_booth._webcam else 'No webcam'}"
            )
            logger.info(
                f"📸 Photo booth initialized: state={self.photo_booth.state}, "
                f"camera_available={self.photo_booth.is_camera_available}"
            )

        # Game over menu
        self.game_over_menu_active = False
        self.game_over_selected_index = 0

        # Educational dialogue system for Story Mode
        self.education_manager = EducationManager(save_manager=self.save_manager)
        self.dialogue_renderer = DialogueRenderer(screen_width, screen_height)

        # AWS IAM client for fetching zombie permission data (Story Mode)
        self.iam_client = AWSIAMClient(use_placeholder=True)

        # Controller unlock combo state (L + R + Start)
        self.controller_unlock_combo_triggered = False

        # Controller button labels for 8BitDo SN30 Pro
        # Note: PauseMenuController has its own copy, but keeping this for backwards compatibility
        self.controller_labels = {
            "confirm": "A",
            "back": "B",
            "pause": "Start",
            "lobby": "Select",
            "up": "D-Pad ↑",
            "down": "D-Pad ↓",
        }

        # Service Protection Quests
        self.quest_manager: Optional[ServiceProtectionQuestManager] = None
        self.service_nodes: List[ServiceNode] = []
        self.hacker: Optional[Hacker] = None

        # JIT Access Quest
        self.auditor: Optional[Auditor] = None
        self.admin_roles: List[AdminRole] = []

        # Production account IDs for JIT quest
        self.JIT_QUEST_ACCOUNTS = {
            "160224865296",  # MyHealth - Production Data
            "613056517323",  # MyHealth - Production
            "437154727976",  # Sonrai MyHealth - Org
        }

        # Production Outage system - random events that freeze player while they "fix prod"
        self.outage_manager = ProductionOutageManager(
            trigger_chance_per_second=0.005,  # 0.5% chance per second (~once every 3-4 minutes)
            cooldown_seconds=45.0,  # Minimum 45 seconds between outages
            outage_duration=5.0,  # 5 second freeze
        )

    def _init_controller_with_retry(self, max_retries: int = 5, delay: float = 0.3) -> None:
        """
        Initialize controller with retry logic.

        Controllers sometimes aren't immediately recognized on startup,
        especially USB/Bluetooth controllers. This method retries a few times
        with small delays and event pumps to ensure proper detection.

        Args:
            max_retries: Number of retry attempts
            delay: Delay in seconds between retries
        """
        logger.info(f"🎮 Initializing controller detection (max {max_retries} attempts)...")
        print(f"🎮 Initializing controller detection (max {max_retries} attempts)...")

        for attempt in range(max_retries):
            # Pump events multiple times to ensure pygame processes device connections
            for _ in range(3):
                pygame.event.pump()
                time.sleep(0.05)

            # Re-query joystick subsystem
            pygame.joystick.quit()
            pygame.joystick.init()

            controller_count = pygame.joystick.get_count()
            logger.info(
                f"🎮 Controller scan attempt {attempt + 1}/{max_retries}: found {controller_count} device(s)"
            )
            print(
                f"🎮 Controller scan attempt {attempt + 1}/{max_retries}: found {controller_count} device(s)"
            )

            if controller_count > 0:
                # Try to find a recognized controller
                for i in range(controller_count):
                    joy = pygame.joystick.Joystick(i)
                    joy.init()
                    logger.info(f"🎮 Found controller {i}: {joy.get_name()}")
                    print(f"🎮 Found controller {i}: {joy.get_name()}")
                    if self.joystick is None:
                        self.joystick = joy
                        logger.info(f"🎮 Using controller: {joy.get_name()}")
                        print(f"🎮 ✅ Using controller: {joy.get_name()}")
                break
            else:
                if attempt < max_retries - 1:
                    logger.info(
                        f"🎮 No controller found (attempt {attempt + 1}/{max_retries}), retrying in {delay}s..."
                    )
                    time.sleep(delay)

        if self.joystick is None:
            logger.info(
                "⌨️  No controller detected, using keyboard (connect controller and it will be auto-detected)"
            )
            print("⌨️  No controller detected, using keyboard")
            print("💡 Tip: Connect your controller and it will be auto-detected via hot-plug")

    def start(self) -> None:
        """Start the game."""
        self.running = True
        self.start_time = time.time()
        logger.info("Game started")

        # Initialize service protection quests
        self._initialize_quests()

    def _initialize_quests(self) -> None:
        """Initialize service protection quests for Sandbox and Production levels."""
        if not self.level_manager:
            return

        self.quest_manager = ServiceProtectionQuestManager()

        # Check which services are unprotected in each level's account
        # Level 1: Sandbox (577945324761)
        # Level 6: Production (613056517323)

        # Sandbox quest (Level 1) - only create if bedrock-agentcore is unprotected
        sandbox_level = next((l for l in self.level_manager.levels if l.level_number == 1), None)
        if sandbox_level:
            logger.info(
                f"🔍 Checking protection status for Sandbox account {sandbox_level.account_id}..."
            )
            unprotected_services = self.api_client.get_unprotected_services(
                sandbox_level.account_id
            )

            if "bedrock-agentcore" in unprotected_services:
                # Service is unprotected - create quest!
                # Trigger at x=2500 (halfway through level) to give player time to warm up
                sandbox_quest = create_bedrock_protection_quest(
                    quest_id="sandbox_bedrock_agentcore",
                    level=1,
                    trigger_pos=Vector2(2500, 400),
                    service_pos=Vector2(5000, SERVICE_ICON_Y),
                )
                self.quest_manager.add_quest(sandbox_quest)
                logger.info(f"✅ Created Sandbox Bedrock AgentCore quest (service is unprotected)")
            else:
                logger.info(f"⏭️  Skipping Sandbox quest - bedrock-agentcore already protected")

        # Production quest (Level 6) - only create if bedrock-agentcore is unprotected
        production_level = next((l for l in self.level_manager.levels if l.level_number == 6), None)
        if production_level:
            logger.info(
                f"🔍 Checking protection status for Production account {production_level.account_id}..."
            )
            unprotected_services = self.api_client.get_unprotected_services(
                production_level.account_id
            )

            if "bedrock-agentcore" in unprotected_services:
                # Service is unprotected - create quest!
                # Trigger at x=1500 to give player time to warm up before hacker challenge
                # Service icon at x=2500 (ahead of trigger position)
                production_quest = create_bedrock_protection_quest(
                    quest_id="production_bedrock_agentcore",
                    level=6,
                    trigger_pos=Vector2(1500, 400),
                    service_pos=Vector2(2500, SERVICE_ICON_Y),
                )
                self.quest_manager.add_quest(production_quest)
                logger.info(
                    f"✅ Created Production Bedrock AgentCore quest (service is unprotected)"
                )
            else:
                logger.info(f"⏭️  Skipping Production quest - bedrock-agentcore already protected")

    def _initialize_jit_quest(self, account_id: str) -> None:
        """
        Initialize JIT Access Quest for production accounts.

        Args:
            account_id: AWS account ID to check
        """
        # Reset JIT quest entities
        self.auditor = None
        self.admin_roles = []
        self.game_state.jit_quest = None

        # Only initialize for production accounts
        if account_id not in self.JIT_QUEST_ACCOUNTS:
            logger.info(f"⏭️  Account {account_id} is not a production account - skipping JIT quest")
            return

        try:
            logger.info(
                f"🔍 Checking for admin/privileged permission sets in account {account_id}..."
            )

            # Fetch permission sets (admin/privileged roles)
            permission_sets_data = self.api_client.fetch_permission_sets(account_id)

            if not permission_sets_data:
                logger.info(f"⏭️  No admin/privileged permission sets found - skipping JIT quest")
                return

            # Fetch JIT configuration to see which are already protected
            jit_config = self.api_client.fetch_jit_configuration(account_id)
            enrolled_ids = set(jit_config.get("enrolledPermissionSets", []))

            # Create PermissionSet objects and mark which have JIT
            permission_sets = []
            unprotected_count = 0
            for ps_data in permission_sets_data:
                has_jit = ps_data["id"] in enrolled_ids
                perm_set = PermissionSet(
                    id=ps_data["id"],
                    name=ps_data["name"],
                    identity_labels=ps_data["identityLabels"],
                    user_count=ps_data["userCount"],
                    has_jit=has_jit,
                )
                permission_sets.append(perm_set)
                if not has_jit:
                    unprotected_count += 1
                    logger.info(f"  ⚠️  {perm_set.name} - UNPROTECTED (needs JIT)")
                else:
                    logger.info(f"  ✅ {perm_set.name} - already has JIT protection")

            # Only create quest if there are unprotected roles
            if unprotected_count == 0:
                logger.info(f"⏭️  All admin/privileged roles already have JIT - skipping quest")
                return

            # Create quest entities
            logger.info(
                f"✅ Creating JIT Access Quest with {len(permission_sets)} permission sets ({unprotected_count} unprotected)"
            )

            # Calculate ground level for platformer mode
            # Use the same ground level as zombies - get from platform positions
            # The last platforms in the list are the ground segments
            ground_y = 400  # Default fallback
            if hasattr(self.game_map, "platform_positions") and self.game_map.platform_positions:
                # Get the ground platform (last ones in the list are ground segments)
                # Ground platforms have y position around 600-650
                for (
                    platform_x,
                    platform_y,
                    platform_width,
                ) in self.game_map.platform_positions:
                    if platform_y > ground_y:
                        ground_y = platform_y
                logger.info(f"Using ground_y = {ground_y} from platform positions")

            self.auditor, self.admin_roles = create_jit_quest_entities(
                permission_sets, self.game_map.map_width, ground_y
            )

            # Initialize quest state
            self.game_state.jit_quest = JitQuestState(
                active=True,
                auditor_position=self.auditor.position,
                admin_roles=permission_sets,
                protected_count=len(permission_sets) - unprotected_count,
                total_count=len(permission_sets),
                quest_completed=False,
                quest_failed=False,
            )

            logger.info(
                f"✅ JIT Access Quest initialized: {unprotected_count}/{len(permission_sets)} roles need protection"
            )

        except Exception as e:
            logger.error(f"Failed to initialize JIT quest: {e}", exc_info=True)
            self.auditor = None
            self.admin_roles = []
            self.game_state.jit_quest = None

    def _update_quests(self, delta_time: float) -> None:
        """Update service protection quests."""
        if not self.quest_manager:
            return

        from models import QuestStatus

        # Get quest for current level
        active_quest = self.quest_manager.get_quest_for_level(self.game_state.current_level)
        if not active_quest:
            return

        # Check for quest trigger (player crosses x=300)
        if active_quest.status == QuestStatus.NOT_STARTED:
            if self.player.position.x > active_quest.trigger_position.x:
                # Trigger quest - show warning dialog
                active_quest.status = QuestStatus.TRIGGERED
                self.game_state.quest_message = (
                    "⚠️ WARNING! ⚠️\n\n"
                    f"You have {active_quest.time_limit:.0f} SECONDS to protect "
                    "Bedrock AgentCore before a hacker creates unauthorized "
                    "AI agent runtimes and code interpreters!\n\n"
                    "Press B/SPACE/ENTER to begin!"
                )
                self.game_state.quest_message_timer = 999.0  # Show until dismissed
                logger.info(f"🎮 Quest triggered at x={self.player.position.x}")

        # Update active quest
        if active_quest.status == QuestStatus.ACTIVE:
            # Update timer
            active_quest.time_remaining -= delta_time

            # Check if timer expired
            if active_quest.time_remaining <= 0:
                self._handle_quest_failure(active_quest, "Time's up!")
                return

            # Update hacker
            if self.hacker:
                self.hacker.update(delta_time, self.game_map)

                # Check if hacker reached service
                hacker_dist = self._distance(self.hacker.position, active_quest.service_position)
                if hacker_dist < 50:  # Hacker reached icon
                    self._handle_quest_failure(active_quest, "Hacker reached service first!")
                    return

            # Check if player near service (auto-protect within 80px)
            player_dist = self._distance(self.player.position, active_quest.service_position)
            if player_dist < 80:  # Auto-protect range
                # Find service node
                for service_node in self.service_nodes:
                    if service_node.position.x == active_quest.service_position.x:
                        if not service_node.protected:
                            self._try_protect_service(active_quest, service_node)

    def _distance(self, pos1: Vector2, pos2: Vector2) -> float:
        """Calculate Euclidean distance between two positions."""
        dx = pos2.x - pos1.x
        dy = pos2.y - pos1.y
        return (dx * dx + dy * dy) ** 0.5

    def _handle_quest_failure(self, quest, reason: str) -> None:
        """Handle quest failure."""
        from models import QuestStatus

        quest.status = QuestStatus.COMPLETED
        quest.player_won = False
        self.hacker = None

        # BUG FIX: Ensure all zombies are in correct state before pausing
        # Reset any quarantine flags that might have been set incorrectly
        for zombie in self.zombies:
            if zombie.is_quarantining and zombie in self.zombies:
                # If zombie is still in the list but marked as quarantining, reset it
                zombie.is_quarantining = False
                logger.warning(f"Reset is_quarantining flag on {zombie.identity_name}")

        # Pause game to show failure message
        self.game_state.previous_status = self.game_state.status  # BUG FIX: Save previous status
        self.game_state.status = GameStatus.PAUSED

        # Show mission failed message
        self.game_state.congratulations_message = (
            "❌ Mission Failed: AgentCore Compromised\n\n"
            "The hacker reached Bedrock AgentCore first and created "
            "unauthorized AI agent runtimes with code interpreters!\n\n"
            "Your sensitive data is now being exfiltrated through "
            "gateway targets.\n\n"
            "Press A/B/Start or ENTER to continue"
        )

        logger.info(f"❌ QUEST FAILED: {reason}")
        logger.info(
            f"🐛 DEBUG: {len(self.zombies)} zombies in list, {len([z for z in self.zombies if not z.is_quarantining])} not quarantining"
        )

    def _try_protect_service(self, quest, service_node: ServiceNode) -> None:
        """
        Attempt to protect service via Sonrai API.

        Args:
            quest: Active quest
            service_node: Service node to protect
        """
        try:
            from models import QuestStatus

            # Call REAL Sonrai API to protect the service!
            result = self.api_client.protect_service(
                service_type=quest.service_type,
                account_id=self.game_state.current_level_account_id,
                service_name=f"{quest.service_type.capitalize()} Service",
            )

            if result.success:
                # Success! Player won the race
                service_node.protected = True
                quest.status = QuestStatus.COMPLETED
                quest.player_won = True
                self.game_state.services_protected += 1

                # Stop hacker
                self.hacker = None

                # BUG FIX: Ensure all zombies are in correct state before pausing
                # Reset any quarantine/hidden flags that might have been set incorrectly
                # This prevents zombies from becoming unshootable after quest success
                # BUT: Skip this during arcade mode - eliminated zombies should stay hidden!
                if not self.arcade_manager.is_active():
                    for zombie in self.zombies:
                        if zombie.is_quarantining or zombie.is_hidden:
                            # If zombie is still in the list but marked as quarantining/hidden, reset it
                            zombie.is_quarantining = False
                            zombie.is_hidden = False
                            logger.warning(
                                f"Reset quarantine/hidden flags on {zombie.identity_name}"
                            )

                # Pause game to show success message
                self.game_state.previous_status = (
                    self.game_state.status
                )  # Save current status before pausing
                self.game_state.status = GameStatus.PAUSED

                # Show success message with ChatOps info
                self.game_state.congratulations_message = (
                    f"🛡️ AGENTCORE PROTECTED!\n\n"
                    f"You protected Bedrock AgentCore! High-risk operations like "
                    f"CreateAgentRuntime, CreateCodeInterpreter, and "
                    f"UpdateGatewayTarget now require ChatOps approval "
                    f"through Slack or Teams!\n\n"
                    f"The Cloud Permissions Firewall blocked unauthorized "
                    f"AI agent creation and code execution.\n\n"
                    "Press A/B/Start or ENTER to continue"
                )

                logger.info(
                    f"✅ PLAYER WON THE RACE! Service protected at x={service_node.position.x}"
                )
                logger.info(f"🎉 Showing success message to player")
                logger.info(
                    f"🐛 DEBUG: {len(self.zombies)} zombies in list, {len([z for z in self.zombies if not z.is_quarantining])} not quarantining"
                )
            else:
                # API error - show error message but don't fail quest
                error_msg = result.error_message or "Unknown error"
                logger.error(f"Failed to protect service: {error_msg}")
                self.game_state.quest_message = (
                    f"⚠️ Protection Failed\n\n" f"Error: {error_msg}\n\n" "Try again!"
                )
                self.game_state.quest_message_timer = 3.0

        except Exception as e:
            logger.error(f"Exception protecting service: {e}")

    def _update_jit_quest(self, delta_time: float) -> None:
        """Update JIT Access Quest entities and check for interactions."""
        if not self.game_state.jit_quest or not self.game_state.jit_quest.active:
            return

        # Update auditor patrol
        if self.auditor:
            self.auditor.update(delta_time)
            self.game_state.jit_quest.auditor_position = self.auditor.position

        # Update admin roles
        for admin_role in self.admin_roles:
            admin_role.update(delta_time)

        # Update quest message timer
        if self.game_state.jit_quest.quest_message_timer > 0:
            self.game_state.jit_quest.quest_message_timer -= delta_time
            if self.game_state.jit_quest.quest_message_timer <= 0:
                self.game_state.jit_quest.quest_message = None

        # Check for player interaction with admin roles
        if self.player:
            player_bounds = self.player.get_bounds()

            for admin_role in self.admin_roles:
                if not admin_role.has_jit:  # Only interact with unprotected roles
                    role_bounds = admin_role.get_bounds()

                    # Check if player is near admin role
                    if player_bounds.colliderect(role_bounds):
                        # Player is touching unprotected admin role - apply JIT!
                        self._apply_jit_to_admin_role(admin_role)

    def _apply_jit_to_admin_role(self, admin_role: AdminRole) -> None:
        """
        Apply JIT protection to an admin role via Sonrai API.

        Args:
            admin_role: AdminRole entity to protect
        """
        try:
            logger.info(f"Applying JIT protection to {admin_role.permission_set.name}...")

            # Call REAL Sonrai API to apply JIT protection
            result = self.api_client.apply_jit_protection(
                account_id=self.game_state.current_level_account_id,
                permission_set_id=admin_role.permission_set.id,
                permission_set_name=admin_role.permission_set.name,
            )

            if result.success:
                # Success! Mark role as protected
                admin_role.apply_jit_protection()
                self.game_state.jit_quest.protected_count += 1

                # Show success message
                self.game_state.jit_quest.quest_message = (
                    f"✅ JIT Protection Applied!\n\n"
                    f"{admin_role.permission_set.name} now requires\n"
                    f"Just-In-Time approval for access.\n\n"
                    f"Progress: {self.game_state.jit_quest.protected_count}/{self.game_state.jit_quest.total_count} roles protected"
                )
                self.game_state.jit_quest.quest_message_timer = 3.0

                logger.info(f"✅ JIT applied to {admin_role.permission_set.name}")

                # Check if all roles are now protected
                if (
                    self.game_state.jit_quest.protected_count
                    >= self.game_state.jit_quest.total_count
                ):
                    self._complete_jit_quest()
            else:
                # API error
                error_msg = result.error_message or "Unknown error"
                logger.error(f"Failed to apply JIT protection: {error_msg}")
                self.game_state.jit_quest.quest_message = (
                    f"⚠️ JIT Protection Failed\n\n" f"Error: {error_msg}\n\n" "Try again!"
                )
                self.game_state.jit_quest.quest_message_timer = 3.0

        except Exception as e:
            logger.error(f"Exception applying JIT protection: {e}")

    def _complete_jit_quest(self) -> None:
        """Handle JIT quest completion."""
        self.game_state.jit_quest.quest_completed = True

        # Pause game to show success message
        self.game_state.previous_status = (
            self.game_state.status
        )  # Save current status before pausing
        self.game_state.status = GameStatus.PAUSED

        # Show audit success message
        self.game_state.congratulations_message = (
            "🎉 Audit Deficiency Prevented!\n\n"
            "All admin and privileged roles now require\n"
            "Just-In-Time approval for access!\n\n"
            "Standing admin access has been eliminated,\n"
            "preventing a significant audit finding.\n\n"
            "Press A/B/Start or ENTER to continue"
        )

        logger.info(
            f"✅ JIT QUEST COMPLETED! All {self.game_state.jit_quest.total_count} roles protected"
        )

    def update(self, delta_time: float) -> None:
        """
        Update game state for one frame.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Periodic autosave (every 30 seconds during gameplay)
        current_time = time.time()
        if current_time - self.last_autosave_time >= self.autosave_interval:
            if self.game_state.status in (
                GameStatus.LOBBY,
                GameStatus.PLAYING,
                GameStatus.BOSS_BATTLE,
            ):
                self._save_game()
                self.last_autosave_time = current_time

        # Update play time
        if self.game_state.status == GameStatus.PLAYING:
            self.game_state.play_time = time.time() - self.start_time

        # Update resource message timer (only if not in "always show" mode)
        # Timer of 999.0 means "show while hovering" - don't decrement it
        if (
            self.game_state.resource_message_timer > 0
            and self.game_state.resource_message_timer < 999.0
        ):
            self.game_state.resource_message_timer -= delta_time
            if self.game_state.resource_message_timer <= 0:
                self.game_state.resource_message = None

        # Handle photo booth consent timeout
        if getattr(self.game_state, "photo_booth_consent_active", False) and self.photo_booth:
            if self.photo_booth.check_consent_timeout():
                logger.info("📸 Photo booth consent timed out")
                self._begin_arcade_session()

        # Handle different game states
        if self.game_state.status == GameStatus.LOBBY:
            self._update_lobby(delta_time)
        elif self.game_state.status == GameStatus.PLAYING:
            self._update_playing(delta_time)  # LEVEL mode (platformer)

            # Update arcade mode if active (only during PLAYING, not during PAUSED)
            if self.arcade_manager.is_active():
                logger.debug(f"🎮 Arcade mode is active, updating...")
                self._update_arcade_mode(delta_time)
                # Sync arcade state to game state for rendering
                self.game_state.arcade_mode = self.arcade_manager.get_state()
            else:
                self.game_state.arcade_mode = None
        elif self.game_state.status == GameStatus.BOSS_BATTLE:
            self._update_boss_battle(delta_time)
        elif self.game_state.status == GameStatus.PAUSED:
            # Game is paused, don't update entities or arcade timer
            # Keep arcade state synced for rendering (shows paused timer)
            if self.arcade_manager.is_active():
                self.game_state.arcade_mode = self.arcade_manager.get_state()
            pass

    def _update_lobby(self, delta_time: float) -> None:
        """
        Update game logic during LOBBY state (top-down navigation).

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Update door interaction cooldown
        if self.door_interaction_cooldown > 0:
            self.door_interaction_cooldown -= delta_time
            if self.door_interaction_cooldown <= 0:
                logger.info("🚪 Door interaction cooldown expired - doors can now be entered")

        # Update camera to follow player
        if self.use_map and self.game_map:
            self.game_map.update_camera(self.player.position.x, self.player.position.y)
            self.game_map.update_zoom(delta_time)

        # Update player (top-down movement - no gravity)
        self.player.update(delta_time, is_platformer_mode=False)

        # Update zombies (they're visible in lobby but not interactive - just for display)
        # Don't update zombie AI or reveal logic in lobby - they're just decorative
        # Zombies will become interactive when entering a level

        # Update third parties (they walk around in lobby)
        if self.game_map and hasattr(self.game_map, "third_parties"):
            for third_party in self.game_map.third_parties:
                third_party.update(delta_time, self.game_map)

        # Check for door collisions (only if cooldown expired)
        if (
            self.game_map
            and hasattr(self.game_map, "doors")
            and self.door_interaction_cooldown <= 0
        ):
            player_bounds = self.player.get_bounds()
            logger.debug(
                f"Checking {len(self.game_map.doors)} doors for collision with player at ({self.player.position.x}, {self.player.position.y})"
            )
            for door in self.game_map.doors:
                if door.check_collision(player_bounds):
                    logger.info(
                        f"🚪 Door collision! Door at ({door.position.x}, {door.position.y}) → {door.destination_room_name}"
                    )
                    # Check if this door's level is unlocked BEFORE attempting to enter
                    door_name = door.destination_room_name

                    # Find the level that matches this door
                    level_unlocked = False
                    locked_reason = ""

                    # If level_manager doesn't exist, allow all doors (sandbox mode)
                    if not self.level_manager:
                        level_unlocked = True
                    else:
                        for level in self.level_manager.levels:
                            if level.account_name == door_name:
                                # Check if level is unlocked
                                is_sandbox = (
                                    level.account_id == "577945324761"
                                )  # Sandbox is always unlocked
                                if is_sandbox or self.cheat_enabled:
                                    level_unlocked = True
                                else:
                                    # Check if previous level is complete
                                    level_index = self.level_manager.levels.index(level)
                                    if level_index > 0:
                                        prev_level = self.level_manager.levels[level_index - 1]
                                        if (
                                            prev_level.account_id
                                            in self.completed_level_account_ids
                                        ):
                                            level_unlocked = True
                                        else:
                                            locked_reason = f"🔒 Level Locked\n\nComplete {prev_level.account_name} to unlock\n{level.account_name}\n\nPress A/B/Start or ENTER to continue"
                                    else:
                                        level_unlocked = True
                                break

                    if level_unlocked:
                        # Player entered an unlocked door
                        logger.info(f"🚪 Door collision detected! Door name: '{door_name}'")

                        # Check if this is Sandbox and level entry menu is enabled
                        # Door name is "MyHealth - Sandbox", account_id is "577945324761"
                        is_sandbox = "sandbox" in door_name.lower() or (
                            hasattr(door, "account_id") and door.account_id == "577945324761"
                        )
                        logger.info(
                            f"🚪 DEBUG: door_name='{door_name}', is_sandbox={is_sandbox}, "
                            f"auto_start_arcade={self.auto_start_arcade}"
                        )

                        if is_sandbox and self.auto_start_arcade:
                            # AUTO_START_ARCADE: Skip menu, go directly to arcade mode
                            logger.info(
                                f"🕹️ AUTO_START_ARCADE: Entering {door_name} directly in arcade mode"
                            )
                            self._enter_level_with_static_genre(door)
                            self._start_arcade_mode()
                        elif is_sandbox and self.level_entry_menu_controller.enabled:
                            # Show level entry mode selector for Sandbox
                            self._pending_door_entry = door
                            self.game_state.congratulations_message = (
                                self.level_entry_menu_controller.show(door_name)
                            )
                            self.game_state.previous_status = self.game_state.status
                            self.game_state.status = GameStatus.PAUSED
                            logger.info(f"🚪 Showing level entry menu for {door_name}")
                        else:
                            # Direct entry for non-Sandbox levels or when menu disabled
                            # Use static genre mapping for different level types
                            self._enter_level_with_static_genre(door)
                        break
                    else:
                        # Door is locked - show message but DON'T enter
                        if locked_reason:
                            logger.info(f"🔒 Attempted to enter locked door: {door_name}")
                            self.game_state.congratulations_message = locked_reason
                            # Save current status before pausing
                            self.game_state.previous_status = self.game_state.status
                            self.game_state.status = GameStatus.PAUSED
                            # Move player away from door to prevent repeated collision
                            self.player.position.x -= 50  # Push player back
                        break

        # Update projectiles (for zapping third parties)
        for projectile in self.projectiles[:]:
            projectile.update(delta_time)
            # Remove projectiles that are off screen
            if (
                projectile.position.x < 0
                or projectile.position.x > self.game_map.map_width
                or projectile.position.y < 0
                or projectile.position.y > self.game_map.map_height
            ):
                self.projectiles.remove(projectile)

        # Check projectile collisions with third parties
        if self.game_map and hasattr(self.game_map, "third_parties"):
            for projectile in self.projectiles[:]:
                for third_party in self.game_map.third_parties[:]:
                    if not third_party.is_blocking and not third_party.is_protected:
                        if projectile.get_bounds().colliderect(third_party.get_bounds()):
                            # Remove projectile
                            if projectile in self.projectiles:
                                self.projectiles.remove(projectile)

                            # Apply damage (third parties have 10 health)
                            eliminated = third_party.take_damage(projectile.damage)

                            # Only block if health reaches 0
                            if eliminated:
                                self._block_third_party(third_party)

                            break

    def _enter_level(self, door) -> None:
        """
        Transition from lobby to level mode.

        Args:
            door: The door that was entered
        """
        try:
            logger.info(f"🚪 === ENTERING LEVEL - START ===")

            if not self.level_manager:
                logger.warning("No level manager available, cannot enter level")
                return

            # Find the level that matches this door's destination
            # Doors have destination_room_name which should match account name
            door_name = door.destination_room_name
            logger.info(f"🚪 Step 1: Door name = '{door_name}'")
            if not door_name:
                logger.warning(f"Door has no destination name, cannot enter level")
                return

            logger.info(f"🚪 Step 2: Looking for level matching door: '{door_name}'")
            logger.info(f"Available levels: {[l.account_name for l in self.level_manager.levels]}")

            # Find matching level by account name
            current_level = None
            for level in self.level_manager.levels:
                if level.account_name == door_name:
                    current_level = level
                    logger.info(
                        f"✅ Found matching level: {level.account_name} (ID: {level.account_id})"
                    )
                    break

            if not current_level:
                logger.warning(f"Could not find level for door: {door_name}")
                logger.warning(
                    f"Available level names: {[l.account_name for l in self.level_manager.levels]}"
                )
                return

            logger.info(f"🚪 Step 3: Setting level index")
            # Set current level in level manager
            self.level_manager.current_level_index = self.level_manager.levels.index(current_level)

            logger.info(f"🚪 Step 4: Loading zombies for account {current_level.account_id}")
            # Load zombies for this level's account, excluding already quarantined ones
            account_id = current_level.account_id
            level_zombies = [
                z
                for z in self.all_zombies
                if z.account == account_id and z.identity_id not in self.quarantined_identities
            ]
            logger.info(
                f"Loaded {len(level_zombies)} zombies for level {current_level.level_number} (excluding {len([z for z in self.all_zombies if z.account == account_id])-len(level_zombies)} already quarantined)"
            )

            logger.info(
                f"🚪 Step 5: Loading difficulty config for {current_level.environment_type}"
            )
            # Initialize difficulty for this level's environment
            try:
                self.difficulty = get_difficulty_for_environment(current_level.environment_type)
                logger.info(
                    f"Difficulty for {current_level.environment_type}: {self.difficulty.zombie_hp} HP, {self.difficulty.reveal_radius}px reveal"
                )
            except Exception as e:
                logger.error(f"Failed to load difficulty config: {e}", exc_info=True)
                self.difficulty = None

            logger.info(f"🚪 Step 6: Reinitializing GameMap for platformer mode")
            # Switch to platformer mode
            # Reinitialize game map with platformer settings
            # NOTE: Third parties should NOT be in levels, only in lobby
            reveal_radius = self.difficulty.reveal_radius if self.difficulty else 60
            try:
                self.game_map = GameMap(
                    "assets/reinvent_floorplan.png",  # Not used for platformer mode
                    self.screen_width,
                    self.screen_height,
                    {account_id: len(level_zombies)},  # Only this account's zombies
                    {},  # No third parties in levels - they only exist in lobby
                    reveal_radius=reveal_radius,
                    api_client=self.api_client,
                    mode="platformer",  # PLATFORMER MODE for levels!
                )
                logger.info(f"✅ GameMap reinitialized as PLATFORMER level successfully")

                # BUG FIX: Recreate spatial grid for platformer level dimensions
                # The original grid was created with lobby dimensions, but platformer levels
                # can be much wider (up to 27,200px for 512 zombies). Without this fix,
                # zombies beyond the original grid width won't be added to collision cells.
                self.spatial_grid = SpatialGrid(self.game_map.map_width, self.game_map.map_height)
                logger.info(
                    f"✅ Spatial grid recreated for level: {self.game_map.map_width}x{self.game_map.map_height}"
                )
            except Exception as e:
                logger.error(f"❌ CRASH during GameMap init: {e}", exc_info=True)
                raise

            logger.info(f"🚪 Step 7: Initializing approval manager (if needed)")
            # Initialize approval manager if this environment requires approvals
            if self.difficulty and self.difficulty.uses_approval_system:
                try:
                    self.approval_manager = ApprovalManager(
                        approvals_needed=self.difficulty.approvals_needed
                    )
                    logger.info(
                        f"Approval system active: {self.difficulty.approvals_needed} approvals needed"
                    )
                except Exception as e:
                    logger.error(f"Failed to initialize approval manager: {e}", exc_info=True)
                    self.approval_manager = None
            else:
                self.approval_manager = None

            logger.info(f"🚪 Step 8: Creating player at platformer start position")
            # Spawn player at start of platformer level
            player_start_pos = Vector2(100, 100)  # Left side, will fall to ground
            try:
                self.player = Player(
                    player_start_pos,
                    self.game_map.map_width,
                    self.game_map.map_height,
                    self.game_map,
                )
                # Give player 3 seconds of spawn protection (increased for arcade mode)
                self.player.is_invincible = True
                self.player.invincibility_timer = 3.0
                logger.info(f"✅ Player created with 3s spawn protection")
            except Exception as e:
                logger.error(f"❌ CRASH during Player init: {e}", exc_info=True)
                raise

            logger.info(f"🚪 Step 9: Setting active zombies and scattering")
            # Set active zombies
            self.zombies = level_zombies
            try:
                self.game_map.scatter_zombies(self.zombies)
                logger.info(f"✅ Zombies scattered successfully")
            except Exception as e:
                logger.error(f"❌ CRASH during zombie scatter: {e}", exc_info=True)
                raise

            logger.info(f"🚪 Step 10: Updating zombie HP")
            # Update zombie HP based on difficulty
            if self.difficulty:
                for zombie in self.zombies:
                    zombie.health = self.difficulty.zombie_hp
                    zombie.max_health = self.difficulty.zombie_hp

            logger.info(f"🚪 Step 11: Updating game state")
            # Update game state
            self.game_state.status = GameStatus.PLAYING
            self.game_state.zombies_remaining = len(level_zombies)
            self.game_state.total_zombies = len(level_zombies)
            self.game_state.current_level = current_level.level_number
            self.game_state.environment_type = current_level.environment_type
            self.game_state.current_level_account_id = account_id

            logger.info(f"🚪 Step 12: Resetting power-ups and level state")
            # Reset power-ups and other level-specific state
            self.powerup_manager = PowerUpManager()
            self.powerups = []
            self.star_power_touched_zombies.clear()
            self.projectiles = []
            self.boss = None
            self.boss_spawned = False

            # Reset production outage state for fresh level
            self.outage_manager.reset()

            logger.info(f"🚪 Step 13: Spawning power-ups for level")
            # Spawn AWS-themed power-ups (stars and lambda speed) on platforms
            try:
                self.spawn_powerups()
                logger.info(f"✅ Power-up spawning completed: {len(self.powerups)} powerups active")
            except Exception as e:
                logger.error(f"⚠️  Power-up spawning failed: {e}", exc_info=True)
                self.powerups = []  # Continue level without powerups rather than crash
                logger.warning("Continuing level entry without powerups")

            logger.info(f"🚪 Step 14: Creating service nodes for quest (if applicable)")
            # Create service nodes ONLY if there's a quest for this level
            # (quest will only exist if the service is unprotected)
            try:
                self.service_nodes = []
                if self.quest_manager:
                    quest = self.quest_manager.get_quest_for_level(current_level.level_number)
                    if quest:
                        # Quest exists - create service node!
                        if current_level.level_number == 1:
                            # Sandbox Bedrock AgentCore service at x=5000
                            service_node = create_service_node(
                                "bedrock-agentcore", Vector2(5000, SERVICE_ICON_Y)
                            )
                            self.service_nodes = [service_node]
                            logger.info(
                                f"✅ Created Bedrock AgentCore service node for Sandbox (quest active)"
                            )
                        elif current_level.level_number == 6:
                            # Production Bedrock AgentCore service at x=800
                            service_node = create_service_node(
                                "bedrock-agentcore", Vector2(800, SERVICE_ICON_Y)
                            )
                            self.service_nodes = [service_node]
                            logger.info(
                                f"✅ Created Bedrock AgentCore service node for Production (quest active)"
                            )
                    else:
                        logger.info(
                            f"⏭️  No quest for level {current_level.level_number} - service already protected"
                        )
            except Exception as e:
                logger.error(f"⚠️  Service node creation failed: {e}", exc_info=True)
                self.service_nodes = []

            logger.info(f"🚪 Step 15: Initializing JIT Access Quest (if production account)")
            # Initialize JIT Access Quest for production accounts
            self._initialize_jit_quest(account_id)

            logger.info(
                f"🚪 === ENTERED LEVEL {current_level.level_number}: {current_level.account_name} - SUCCESS ==="
            )
        except Exception as e:
            logger.error(f"❌ ❌ ❌ CRASH in _enter_level: {e}", exc_info=True)
            import traceback

            traceback.print_exc()
            # Don't crash - just log and return to lobby
            self.game_state.error_message = f"Failed to enter level: {str(e)}"

    def _return_to_lobby(self, mark_completed: bool = False) -> None:
        """
        Transition from level back to lobby mode.

        Args:
            mark_completed: If True, mark the current level as completed
        """
        logger.info("🏛️  === RETURNING TO LOBBY - START ===")

        # Reset genre controller when returning to lobby
        self.active_genre_controller = None
        self.game_state.current_genre = GenreType.PLATFORMER

        # Reset Story Mode when returning to lobby
        self.game_state.is_story_mode = False
        self.game_state.active_dialogue = None
        self.game_state.dialogue_format_kwargs = {}

        # Check if JIT quest was active but not completed
        if self.game_state.jit_quest and self.game_state.jit_quest.active:
            if not self.game_state.jit_quest.quest_completed:
                unprotected = (
                    self.game_state.jit_quest.total_count
                    - self.game_state.jit_quest.protected_count
                )
                if unprotected > 0:
                    # Quest failed - show warning
                    self.game_state.jit_quest.quest_failed = True
                    logger.warning(
                        f"⚠️ JIT Quest failed: {unprotected} admin roles left unprotected"
                    )

                    # Show failure message
                    self.game_state.congratulations_message = (
                        "⚠️ Audit Failed!\n\n"
                        f"{unprotected} admin/privileged role(s) still have\n"
                        "standing access without JIT protection.\n\n"
                        "This is a SIGNIFICANT DEFICIENCY in your\n"
                        "internal audit findings.\n\n"
                        "Press A/B/Start or ENTER to continue"
                    )
                    # Pause to show message
                    self.game_state.previous_status = GameStatus.LOBBY
                    self.game_state.status = GameStatus.PAUSED

        # Mark current level as completed only if explicitly requested
        if mark_completed:
            completed_account_id = self.game_state.current_level_account_id
            if completed_account_id:
                self.completed_level_account_ids.add(completed_account_id)
                self.game_state.completed_levels.add(completed_account_id)
                logger.info(f"✅ Level {completed_account_id} marked as completed")

        # Reinitialize game map for lobby (main branch style)
        self.game_map = GameMap(
            "assets/reinvent_floorplan.png",
            self.screen_width,
            self.screen_height,
            self.account_data,
            self.third_party_data,
        )

        # Recreate spatial grid for lobby dimensions (matches _enter_level fix)
        self.spatial_grid = SpatialGrid(self.game_map.map_width, self.game_map.map_height)
        logger.info(
            f"✅ Spatial grid recreated for lobby: {self.game_map.map_width}x{self.game_map.map_height}"
        )

        # Mark doors as completed based on completed levels
        if self.game_map and hasattr(self.game_map, "doors") and self.level_manager:
            for door in self.game_map.doors:
                # Find the level that matches this door
                if door.destination_room_name:
                    for level in self.level_manager.levels:
                        if level.account_name == door.destination_room_name:
                            # Check if this level's account ID is completed
                            if level.account_id in self.completed_level_account_ids:
                                door.is_completed = True
                                logger.info(
                                    f"✅ Door to {door.destination_room_name} marked as completed"
                                )
                            break

        # Spawn player in center hallway, away from all doors
        # Use the landing zone (center of map) as safe spawn point
        # This ensures player doesn't immediately re-enter a level door
        spawn_position = Vector2(self.landing_zone.x, self.landing_zone.y)
        self.player = Player(
            spawn_position,
            self.game_map.map_width,
            self.game_map.map_height,
            self.game_map,
        )
        logger.info(
            f"🏛️  Player spawned at lobby center hallway: ({spawn_position.x}, {spawn_position.y})"
        )

        # Clear level-specific entities and restore lobby zombies
        self.projectiles = []
        self.powerups = []
        self.boss = None
        self.boss_spawned = False

        # Restore lobby zombies (visible in lobby for decoration)
        if self.use_map and self.all_zombies:
            self.zombies = self.all_zombies  # Restore all zombies to lobby
            # Make sure they're visible and scattered across rooms
            for zombie in self.zombies:
                zombie.is_hidden = False
            # Re-scatter them across rooms (in case positions were modified)
            self.game_map.scatter_zombies(self.zombies)
            logger.info(f"🏛️  Restored {len(self.zombies)} zombies to lobby")
        else:
            self.zombies = []  # No zombies in classic mode

        # Clear service protection quest data
        self.service_nodes = []
        self.hacker = None
        # Reset all quests to NOT_STARTED
        if self.quest_manager:
            from models import QuestStatus

            for quest in self.quest_manager.quests:
                quest.status = QuestStatus.NOT_STARTED
                quest.hacker_spawned = False
                quest.player_won = False
                quest.time_remaining = quest.time_limit

        # Clear JIT quest data
        self.auditor = None
        self.admin_roles = []
        self.game_state.jit_quest = None

        # Update game state
        self.game_state.status = GameStatus.LOBBY
        self.game_state.zombies_remaining = 0
        self.game_state.total_zombies = 0
        self.game_state.current_level_account_id = None

        # Set door interaction cooldown to prevent immediate re-entry
        # Increased to 2 seconds to ensure player has time to move away from door
        self.door_interaction_cooldown = 2.0  # 2 second cooldown
        logger.info("🚪 Door interaction cooldown set to 2.0 seconds (prevents immediate re-entry)")

        logger.info("✅ Returned to lobby")

    def _update_arcade_mode(self, delta_time: float) -> None:
        """
        Update arcade mode logic.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Update arcade manager (handles timer, countdown, combo tracker, etc.)
        self.arcade_manager.update(delta_time)

        # Get current state for logging
        state = self.arcade_manager.get_state()
        logger.debug(
            f"🎮 Arcade update: active={state.active}, countdown={state.countdown_time:.1f}s, time={state.time_remaining:.1f}s"
        )

        # Check if session ended
        if not self.arcade_manager.is_active():
            # Session ended - show results screen
            logger.info("🎮 Arcade session ended - showing results")
            self._show_arcade_results()
            return

        # Dynamic zombie spawning - maintain minimum count
        visible_count = len([z for z in self.zombies if not z.is_hidden])
        if self.arcade_manager.should_respawn_zombies(visible_count):
            logger.debug(f"🎮 Should respawn zombies (visible: {visible_count})")
            ready_zombies = self.arcade_manager.get_zombies_ready_to_respawn()
            logger.debug(f"🎮 Ready to respawn: {len(ready_zombies)} zombies")
            for zombie in ready_zombies:
                if self.game_map:
                    ground_y = 800  # Platform ground level
                    self.arcade_manager.respawn_zombie(
                        zombie, self.player.position, self.game_map.map_width, ground_y
                    )
                    logger.info(f"♻️  Respawned zombie in arcade mode: {zombie.identity_name}")

        # Photo booth timed captures during active gameplay
        if self.photo_booth:
            elapsed = self.photo_booth.get_arcade_elapsed_time()
            if int(elapsed) % 5 == 0 and int(elapsed) > 0:  # Log every 5 seconds
                logger.info(
                    f"📸 Photo booth status: consent_complete={self.photo_booth.is_consent_complete()}, "
                    f"elapsed={elapsed:.1f}s, gameplay_captured={self.photo_booth.gameplay_captured}, "
                    f"selfie_opted_in={self.photo_booth.selfie_opted_in}, "
                    f"selfie_captured={self.photo_booth.selfie_captured}, "
                    f"camera_available={self.photo_booth.is_camera_available}"
                )

            if self.photo_booth.is_consent_complete():
                # Capture gameplay screenshot at configured delay (default 15s)
                if self.photo_booth.should_capture_gameplay():
                    if self.renderer and hasattr(self.renderer, "screen"):
                        self.photo_booth.capture_gameplay(self.renderer.screen)
                        logger.info("📸 Captured gameplay screenshot during arcade mode")
                    else:
                        logger.warning(
                            f"📸 Cannot capture gameplay: renderer={self.renderer is not None}, has_screen={hasattr(self.renderer, 'screen') if self.renderer else 'N/A'}"
                        )

                # Capture selfie shortly after gameplay screenshot
                if self.photo_booth.should_capture_selfie():
                    logger.info(
                        f"📸 About to capture selfie: opted_in={self.photo_booth.selfie_opted_in}, "
                        f"camera_available={self.photo_booth.is_camera_available}"
                    )
                    result = self.photo_booth.capture_selfie()
                    logger.info(f"📸 Captured selfie during arcade mode, result={result}")

        # Disable quests during arcade mode
        # (Quests are updated in _update_playing, which still runs)

    def _start_arcade_mode(self) -> None:
        """Start arcade mode session with initialization."""
        try:
            logger.info("🎮 ========== STARTING ARCADE MODE SESSION ==========")
            logger.info(f"🎮 Current game state: {self.game_state.status}")
            logger.info(f"🎮 Current level: {self.game_state.current_level}")
            logger.info(f"🎮 Current account: {self.game_state.current_level_account_id}")
            logger.info(f"🎮 Has game_map: {self.game_map is not None}")
            logger.info(f"🎮 Zombie count: {len(self.zombies)}")

            # Disable Story Mode for arcade (no educational dialogues)
            self.game_state.is_story_mode = False

            # Show photo booth consent prompt if enabled
            # Check PhotoBoothState is available (may be None if import failed)
            logger.info(f"📸 DEBUG: photo_booth={self.photo_booth is not None}")
            logger.info(f"📸 DEBUG: PhotoBoothState={PhotoBoothState}")
            if self.photo_booth:
                logger.info(f"📸 DEBUG: photo_booth.state={self.photo_booth.state}")

            if (
                self.photo_booth
                and PhotoBoothState
                and self.photo_booth.state != PhotoBoothState.DISABLED
            ):
                self.photo_booth.reset()
                self.photo_booth.show_consent_prompt()
                self.game_state.photo_booth_consent_active = True
                logger.info("📸 Photo booth consent prompt shown - WAITING FOR INPUT")
                # Don't start arcade yet - wait for consent
                return
            else:
                logger.info("📸 Photo booth disabled or not available - skipping consent")

            # Continue with arcade start
            self._begin_arcade_session()
        except Exception as e:
            logger.error(f"🎮 ❌ ARCADE MODE START FAILED: {e}", exc_info=True)
            # Try to recover by starting without photo booth
            self.game_state.photo_booth_consent_active = False
            self._begin_arcade_session()

    def _begin_arcade_session(self) -> None:
        """Begin the actual arcade session after consent (if applicable)."""
        try:
            # Clear consent flag
            self.game_state.photo_booth_consent_active = False

            # Start arcade manager
            self.arcade_manager.start_session()
            logger.info(f"🎮 Arcade manager started. Is active: {self.arcade_manager.is_active()}")

            # Start photo booth arcade tracking for timed captures
            # Always start tracking if photo booth is available - consent may complete later
            if self.photo_booth:
                self.photo_booth.start_arcade_tracking()
                logger.info(
                    f"📸 Photo booth arcade tracking started (consent_complete={self.photo_booth.is_consent_complete()})"
                )

            # Give player extra spawn protection for arcade mode (covers countdown + start)
            if self.player:
                self.player.is_invincible = True
                self.player.invincibility_timer = 5.0  # 5 seconds: 3s countdown + 2s buffer
                logger.info("🛡️ Player given 5s arcade spawn protection")

            # Make all zombies visible for arcade mode
            visible_count = 0
            for zombie in self.zombies:
                if zombie.is_hidden:
                    zombie.is_hidden = False
                    visible_count += 1
            logger.info(f"🎮 Made {visible_count} zombies visible for arcade mode")

            # Calculate initial zombie count based on level width
            if self.game_map:
                initial_count = self.arcade_manager.calculate_initial_zombie_count(
                    self.game_map.map_width
                )
                logger.info(
                    f"🎮 Arcade mode: {initial_count} zombies calculated for level width {self.game_map.map_width}"
                )
            else:
                logger.warning("🎮 ⚠️  No game_map available for arcade mode!")

            # Spawn arcade power-ups
            if self.game_map:
                ground_y = 800
                arcade_powerups = self.arcade_manager.spawn_arcade_powerups(
                    self.game_map.map_width,
                    ground_y,
                    count=10,  # More power-ups for arcade mode
                )
                self.powerups.extend(arcade_powerups)
                logger.info(f"🎁 Spawned {len(arcade_powerups)} arcade power-ups")

            # Show confirmation message (use resource_message to avoid blocking shooting)
            self.game_state.resource_message = (
                "🎮 ARCADE MODE ACTIVATED!\n\nEliminate as many zombies as possible in 60 seconds!"
            )
            self.game_state.resource_message_timer = 3.0

            logger.info("✅ Arcade session started successfully")
        except Exception as e:
            logger.error(f"🎮 ❌ BEGIN ARCADE SESSION FAILED: {e}", exc_info=True)
            # Show error to user
            self.game_state.resource_message = f"❌ Arcade mode failed to start: {e}"
            self.game_state.resource_message_timer = 5.0

        logger.info("✅ Arcade mode initialized successfully")
        logger.info("🎮 ==================================================")

    def _show_arcade_results(self) -> None:
        """Show arcade mode results screen. Delegates to ArcadeResultsController."""
        # Get stats and create snapshot for the controller
        stats = self.arcade_manager.get_stats()
        queue_size = len(self.arcade_manager.get_elimination_queue())

        # Record stats for re:Invent tracking (only during Dec 1-4, 2025)
        is_new_high_score = False
        try:
            is_new_high_score = record_arcade_session(
                zombies_eliminated=stats.total_eliminations,
                highest_combo=stats.highest_combo,
                duration_seconds=60.0,  # Arcade mode is always 60 seconds
            )
            if is_new_high_score:
                logger.info("🏆 NEW HIGH SCORE achieved!")
        except Exception as e:
            logger.warning(f"📊 Failed to record arcade stats: {e}")

        # Store high score flag for photo booth display
        self.game_state.is_new_high_score = is_new_high_score

        stats_snapshot = ArcadeStatsSnapshot(
            total_eliminations=stats.total_eliminations,
            highest_combo=stats.highest_combo,
            powerups_collected=stats.powerups_collected,
            eliminations_per_second=stats.eliminations_per_second,
            queue_size=queue_size,
            is_new_high_score=is_new_high_score,
        )

        # Generate photo booth composite if enabled and minimum time passed
        if self.photo_booth and self.photo_booth.is_consent_complete():
            logger.info(
                f"📸 Photo booth end-of-arcade status: "
                f"state={self.photo_booth.state}, "
                f"selfie_opted_in={self.photo_booth.selfie_opted_in}, "
                f"selfie_captured={self.photo_booth.selfie_captured}, "
                f"gameplay_captured={self.photo_booth.gameplay_captured}, "
                f"selfie_image={self.photo_booth._selfie_image is not None}, "
                f"camera_available={self.photo_booth.is_camera_available}"
            )
            if self.photo_booth.has_minimum_arcade_time():
                # Only generate if we have a gameplay screenshot
                if self.photo_booth.gameplay_captured:
                    logger.info("📸 Generating photo booth composite...")
                    photo_path = self.photo_booth.generate_composite(
                        stats.total_eliminations,
                        is_new_high_score=is_new_high_score,
                    )
                    if photo_path:
                        logger.info(f"📸 Photo booth image saved: {photo_path}")
                        # Store path for display on results screen
                        self.game_state.photo_booth_path = photo_path
                else:
                    logger.info("📸 No gameplay screenshot captured - skipping photo booth")
            else:
                elapsed = self.photo_booth.get_arcade_elapsed_time()
                logger.info(f"📸 Arcade session too short ({elapsed:.1f}s) - skipping photo booth")

        # Pause game first
        self.game_state.previous_status = self.game_state.status
        self.game_state.status = GameStatus.PAUSED

        # If photo booth image was generated, show summary screen first
        if self.game_state.photo_booth_path:
            logger.info("📸 Showing photo booth summary screen")
            self.game_state.photo_booth_summary_active = True
            self._photo_booth_summary_shown_time = (
                time.time()
            )  # Track when shown for input cooldown
            # Don't show arcade results yet - wait for user to dismiss photo booth
            # Store stats for later use when transitioning to results
            self._pending_arcade_stats = stats_snapshot
        else:
            # No photo booth - show results directly
            self.arcade_results_controller.show(stats_snapshot)
            self.game_state.congratulations_message = self._build_arcade_results_message()

    def _build_arcade_results_message(self) -> str:
        """Build the arcade results message. Delegates to ArcadeResultsController."""
        return self.arcade_results_controller.build_message(
            has_controller=self.joystick is not None
        )

    def _dismiss_photo_booth_summary(self) -> None:
        """Dismiss photo booth summary and show arcade results menu."""
        if not self.game_state.photo_booth_summary_active:
            return

        # Require at least 0.5 seconds before allowing dismissal (prevents instant skip from held button)
        if hasattr(self, "_photo_booth_summary_shown_time"):
            elapsed = time.time() - self._photo_booth_summary_shown_time
            if elapsed < 0.5:
                logger.info(
                    f"📸 Photo booth dismissal blocked - only {elapsed:.2f}s elapsed (need 0.5s)"
                )
                return

        logger.info("📸 Dismissing photo booth summary, showing arcade results")
        self.game_state.photo_booth_summary_active = False

        # Now show the arcade results with the pending stats
        if self._pending_arcade_stats:
            self.arcade_results_controller.show(self._pending_arcade_stats)
            self.game_state.congratulations_message = self._build_arcade_results_message()
            self._pending_arcade_stats = None

    def _navigate_arcade_results_menu(self, direction: int) -> None:
        """Navigate arcade results menu. Delegates to ArcadeResultsController."""
        self.arcade_results_controller.navigate(direction)
        self.game_state.congratulations_message = self._build_arcade_results_message()

    def _update_arcade_results_display(self) -> None:
        """Update the arcade results display. Delegates to ArcadeResultsController."""
        self.game_state.congratulations_message = self._build_arcade_results_message()

    def _execute_arcade_results_option(self) -> None:
        """Execute the selected arcade results option. Delegates to ArcadeResultsController."""
        action = self.arcade_results_controller.select()

        if action == ArcadeResultsAction.QUARANTINE_ALL:
            # Batch quarantine all queued zombies
            queue = self.arcade_manager.get_elimination_queue()
            logger.info(f"🔄 Starting batch quarantine of {len(queue)} identities...")

            # Show progress message
            self.game_state.congratulations_message = (
                f"🔄 Quarantining {len(queue)} identities...\n\n" "Please wait..."
            )

            # Perform batch quarantine
            report = self.api_client.batch_quarantine_identities(queue)

            # Clear queue
            self.arcade_manager.clear_elimination_queue()

            # Show results
            self.game_state.congratulations_message = (
                f"✅ Batch Quarantine Complete!\n\n"
                f"Successful: {report.successful}/{report.total_queued}\n"
                f"Failed: {report.failed}/{report.total_queued}\n\n"
                "Press ENTER/SPACE to continue"
            )

            # Set flag to return to lobby on next input
            self.game_state.previous_status = GameStatus.LOBBY
            logger.info(
                f"✅ Batch quarantine complete: {report.successful} successful, {report.failed} failed"
            )

        elif action == ArcadeResultsAction.DISCARD_QUEUE:
            logger.info("🗑️  Discarding elimination queue")
            self.arcade_manager.clear_elimination_queue()
            self._return_to_lobby()

        elif action == ArcadeResultsAction.REPLAY:
            logger.info("🔄 Restarting arcade mode")
            self.arcade_manager.start_session()
            self.game_state.congratulations_message = None
            self.game_state.status = GameStatus.PLAYING

        elif action == ArcadeResultsAction.EXIT_TO_LOBBY:
            logger.info("🏠 Exiting arcade mode to lobby")
            self._return_to_lobby()

    def _update_playing(self, delta_time: float) -> None:
        """
        Update game logic during PLAYING state.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # If we have an active genre controller (Space Shooter, Maze Chase, etc.)
        # delegate updates to it instead of default platformer logic
        if self.active_genre_controller:
            self.active_genre_controller.update(delta_time, self.player)
            # IMPORTANT: Still update player invincibility timer in genre modes!
            self.player.update_invincibility(delta_time)

            # Check for game over (player health depleted) in genre modes
            if self.player.current_health <= 0:
                logger.info(f"💀 GAME OVER (Genre Mode) - Health: {self.player.current_health}")
                self._show_game_over_screen()
                return

            # Check for level completion
            if self.active_genre_controller.check_completion():
                logger.info("🎮 Genre level complete!")
                self._return_to_lobby(mark_completed=True)
            return

        # Pause gameplay when educational dialogue is active (Story Mode)
        # Player can still see the game but entities don't move
        if self.game_state.is_dialogue_active:
            # Still update camera to keep player centered
            if self.use_map and self.game_map:
                self.game_map.update_camera(self.player.position.x, self.player.position.y)
            return  # Skip all gameplay updates while dialogue is shown

        # Update power-up message timer
        if self.game_state.powerup_message_timer > 0:
            self.game_state.powerup_message_timer -= delta_time
            if self.game_state.powerup_message_timer <= 0:
                self.game_state.powerup_message = None

        # Star Power - clear touched set when effect ends
        star_power_active = self.powerup_manager.is_active(PowerUpType.STAR_POWER)

        # Detect when Star Power ends - clear the touched set for next activation
        if self.star_power_was_active and not star_power_active:
            logger.info(f"⭐ Star Power ended!")
            self.star_power_touched_zombies.clear()

        self.star_power_was_active = star_power_active

        # Update Production Outage system (random "fix prod" events)
        # Disable outages during boss battles and arcade countdown
        if self.boss or (
            self.arcade_manager.is_active() and self.arcade_manager.get_state().in_countdown
        ):
            self.outage_manager.disable()
        else:
            self.outage_manager.enable()

        # Update outage manager - may trigger random outage
        outage_just_ended = self.outage_manager.update(delta_time)

        # If outage is active, freeze player and skip most updates
        if self.outage_manager.is_active():
            # Stop player movement immediately when outage starts
            self.player.velocity.x = 0
            self.player.velocity.y = 0

            # Still update camera to follow player (so screen doesn't jump when outage ends)
            if self.use_map and self.game_map:
                self.game_map.update_camera(self.player.position.x, self.player.position.y)

            # Still update zombies (they keep moving - makes it tense!)
            for zombie in self.zombies:
                if not zombie.is_hidden:
                    zombie.update(delta_time, self.player.position, self.game_map)

            # Don't process any other gameplay updates during outage
            return

        # Update scrolling (classic mode only)
        if not self.use_map:
            self.scroll_offset += self.scroll_speed * delta_time

        # Update player (platformer mode - with gravity)
        self.player.update(delta_time, is_platformer_mode=True)

        # Update player invincibility frames
        self.player.update_invincibility(delta_time)

        # Debug: Log health when low
        if self.player.current_health <= 3:
            logger.info(f"⚠️ LOW HEALTH: {self.player.current_health}/{self.player.max_health}")

        # Check for game over (player health depleted)
        if self.player.current_health <= 0:
            logger.info(f"💀 GAME OVER TRIGGERED - Health: {self.player.current_health}")
            self._show_game_over_screen()
            return  # Stop updating game logic

        # PLATFORMER: Check for solid collision with zombies (can't walk through them)
        player_bounds = self.player.get_bounds()

        for zombie in self.zombies:
            if not zombie.is_hidden:  # Only collide with visible zombies
                zombie_bounds = zombie.get_bounds()
                if player_bounds.colliderect(zombie_bounds):
                    # Check if STAR_POWER is active - if so, quarantine zombie instantly!
                    if self.powerup_manager.is_active(PowerUpType.STAR_POWER):
                        # Star power active - instant quarantine on touch (like projectiles)
                        if zombie not in self.star_power_touched_zombies:
                            logger.info(
                                f"⭐ STAR POWER: Touching {zombie.identity_name} - instant quarantine!"
                            )
                            self.star_power_touched_zombies.add(zombie)
                            self._handle_zombie_elimination(zombie)  # Instant elimination
                        continue  # Don't push player back, zombie is eliminated

                    # Apply damage to player (if not invincible)
                    if self.player.take_damage(1):
                        # Damage was applied - trigger consequences
                        self._on_player_damaged(zombie)

                    # Zombie is solid - push player back
                    # Determine push direction based on player movement
                    if self.player.velocity.x > 0:  # Moving right
                        # Push player to left side of zombie
                        self.player.position.x = zombie_bounds.left - self.player.width
                    elif self.player.velocity.x < 0:  # Moving left
                        # Push player to right side of zombie
                        self.player.position.x = zombie_bounds.right

                    # Stop horizontal movement when hitting zombie
                    self.player.velocity.x = 0

        # Update approval manager (if in production environment)
        if self.approval_manager:
            self.approval_manager.update(delta_time)

            # Check for approval collectible pickup
            player_bounds = self.player.get_bounds()
            if self.approval_manager.collect_approval(player_bounds):
                logger.info(
                    f"Collected approval form! ({self.approval_manager.approvals_collected}/{self.approval_manager.approvals_needed})"
                )

        # Update power-ups
        self.powerup_manager.update(delta_time)
        for powerup in self.powerups:
            powerup.update(delta_time)

        # Update player speed based on Lambda Speed power-up
        speed_multiplier = self.powerup_manager.get_effect_value(PowerUpType.LAMBDA_SPEED) or 1.0
        self.player.set_speed_multiplier(speed_multiplier)

        # Check for power-up collection
        player_bounds = self.player.get_bounds()
        for powerup in self.powerups:
            if not powerup.collected and player_bounds.colliderect(powerup.get_bounds()):
                powerup.collected = True
                self._apply_powerup_effect(powerup)
                # Show power-up message bubble
                self.game_state.powerup_message = powerup.get_description()
                self.game_state.powerup_message_timer = 3.0  # Show for 3 seconds
                logger.info(f"🎁 Collected power-up: {powerup.powerup_type.value}")

        # Check for resource node collision (S3, RDS, etc.)
        # Message appears only while hovering and disappears immediately when leaving
        resource_collision_found = False
        if self.use_map and self.game_map and hasattr(self.game_map, "resource_nodes"):
            for resource in self.game_map.resource_nodes:
                # Get resource bounds (centered on position, extends upward from ground)
                resource_size = resource.get("size", 48)
                resource_pos = resource.get("position")
                resource_x = resource_pos.x
                resource_y = resource_pos.y - resource_size  # Icon extends upward
                resource_bounds = pygame.Rect(
                    int(resource_x), int(resource_y), resource_size, resource_size
                )

                # Check if player is touching or jumping on the resource
                if player_bounds.colliderect(resource_bounds):
                    resource_collision_found = True
                    # Get resource info
                    resource_type = resource.get("type", "Unknown")
                    protection_status = resource.get("protection_status", "unprotected")
                    data_class = resource.get("data_class", None)

                    # Determine service type from resource name (e.g., "rds-backups" -> "rds")
                    resource_lower = resource_type.lower()
                    is_rds = "rds" in resource_lower or "db" in resource_lower
                    is_s3 = "s3" in resource_lower or "bucket" in resource_lower

                    # Generate message based on protection status
                    if protection_status == "protected":
                        # Special message for protected S3 buckets
                        if is_s3:
                            message = "🔒 S3 Bucket\n"
                            message += "This bucket contains sensitive information.\n"
                            message += "This bucket is protected, so sensitive\n"
                            message += "permissions require approval via ChatOps."
                        else:
                            message = f"🔒 Protected: {resource_type}\n"
                            if data_class:
                                message += f"Data Class: {data_class}\n"
                            message += "⚠️ ChatOps approval required\nfor sensitive permissions"
                    elif protection_status == "blocked":
                        # Special message for blocked RDS - works for "rds-backups", "backup-rds", etc.
                        if is_rds:
                            message = "🚫 RDS Service Blocked\n"
                            message += "RDS service is blocked in this account.\n"
                            message += "Nothing can access RDS service,\n"
                            message += "so it's safe."
                        else:
                            message = f"🚫 Blocked: {resource_type}\n"
                            message += "Service is blocked in this account.\n"
                            message += "Access denied by security policy."
                    else:  # unprotected
                        message = f"📦 Resource: {resource_type}\n"
                        if data_class:
                            message += f"⚠️ Data Class: {data_class}\n"
                        message += "Consider adding protection"

                    # Show the message immediately (no timer - appears only while hovering)
                    self.game_state.resource_message = message
                    self.game_state.resource_message_timer = (
                        999.0  # Large value to keep it visible while hovering
                    )
                    break  # Only show one resource message at a time

        # If not colliding with any resource, clear the message immediately
        if not resource_collision_found:
            self.game_state.resource_message = None
            self.game_state.resource_message_timer = 0.0

        # Map mode: update camera and reveal nearby zombies
        if self.use_map and self.game_map:
            self.game_map.update_camera(self.player.position.x, self.player.position.y)
            # Skip reveal during arcade mode - eliminated zombies should stay hidden
            if not self.arcade_manager.is_active():
                self.game_map.reveal_nearby_zombies(self.player.position, self.zombies)

        # Update zombies with AI (only if not in boss battle)
        if self.game_state.status != GameStatus.BOSS_BATTLE:
            for zombie in self.zombies:
                zombie.update(delta_time, player_pos=self.player.position, game_map=self.game_map)

        # Update 3rd parties
        third_parties = self.get_third_parties()
        for third_party in third_parties:
            third_party.update(delta_time, self.game_map)

        # Update service protection quests (skip during arcade mode)
        if not self.arcade_manager.is_active():
            self._update_quests(delta_time)

            # Update JIT Access Quest
            self._update_jit_quest(delta_time)

        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(delta_time)

            # Check wall collision (map mode only)
            if self.use_map and self.game_map:
                if projectile.hits_wall(self.game_map):
                    self.projectiles.remove(projectile)
                    continue  # Skip other checks if hit wall

            # Remove off-screen/off-map projectiles
            if self.use_map and self.game_map:
                # Map mode: check against map bounds
                if projectile.is_off_screen(
                    self.game_map.map_width, self.game_map.map_height, map_mode=True
                ):
                    self.projectiles.remove(projectile)
            else:
                # Classic mode: check against screen bounds
                if projectile.is_off_screen(self.screen_width, self.screen_height, map_mode=False):
                    self.projectiles.remove(projectile)

        # Skip zombie collisions during boss battle
        if self.game_state.status != GameStatus.BOSS_BATTLE:
            # Check collisions (only with revealed zombies in map mode)
            if self.use_map and self.game_map:
                # In map mode: only collide with zombies that are revealed AND on screen
                visible_zombies = [
                    z
                    for z in self.zombies
                    if not z.is_hidden
                    and self.game_map.is_on_screen(z.position.x, z.position.y, z.width, z.height)
                ]
            else:
                visible_zombies = self.zombies

            # DEBUG: ALWAYS log when projectiles exist (even if no visible zombies)
            if len(self.projectiles) > 0:
                logger.info(
                    f"🔍 COLLISION CHECK: {len(self.projectiles)} projectiles vs {len(visible_zombies)} visible zombies (total: {len(self.zombies)} zombies)"
                )

                # Log filtering details
                if self.use_map and len(self.zombies) > 0 and len(visible_zombies) == 0:
                    logger.warning(
                        f"⚠️  ALL ZOMBIES FILTERED OUT! Total zombies: {len(self.zombies)}, but 0 visible"
                    )
                    # Check why zombies are filtered
                    hidden_count = sum(1 for z in self.zombies if z.is_hidden)
                    offscreen_count = sum(
                        1
                        for z in self.zombies
                        if not z.is_hidden
                        and not self.game_map.is_on_screen(
                            z.position.x, z.position.y, z.width, z.height
                        )
                    )
                    logger.warning(f"   Hidden: {hidden_count}, Off-screen: {offscreen_count}")

                # Log first projectile and zombie positions if both exist
                if self.projectiles and visible_zombies:
                    p = self.projectiles[0]
                    z = visible_zombies[0]
                    logger.info(
                        f"  Projectile[0]: pos=({p.position.x:.1f}, {p.position.y:.1f}), bounds={p.get_bounds()}"
                    )
                    logger.info(
                        f"  Zombie[0]: pos=({z.position.x:.1f}, {z.position.y:.1f}), bounds={z.get_bounds()}, is_quarantining={z.is_quarantining}, is_hidden={z.is_hidden}"
                    )

            collisions = check_collisions_with_spatial_grid(
                self.projectiles, visible_zombies, self.spatial_grid
            )

            # DEBUG: Log collision results
            if len(self.projectiles) > 0:
                logger.info(f"🎯 COLLISION RESULT: {len(collisions)} collisions detected")
        else:
            collisions = []

        # Handle zombie collisions
        for projectile, zombie in collisions:
            # Remove projectile
            if projectile in self.projectiles:
                self.projectiles.remove(projectile)

            # Apply damage to zombie
            eliminated = zombie.take_damage(projectile.damage)

            # Only handle elimination if zombie health reached 0
            if eliminated:
                self._handle_zombie_elimination(zombie)

        # Check collisions with 3rd parties
        third_parties = self.get_third_parties()
        if third_parties:
            # Get visible 3rd parties
            if self.use_map and self.game_map:
                visible_third_parties = [
                    tp
                    for tp in third_parties
                    if not tp.is_hidden
                    and self.game_map.is_on_screen(
                        tp.position.x, tp.position.y, tp.width, tp.height
                    )
                ]
            else:
                visible_third_parties = third_parties

            third_party_collisions = check_collisions_with_spatial_grid(
                self.projectiles, visible_third_parties, self.spatial_grid
            )

            # Handle 3rd party collisions
            for projectile, third_party in third_party_collisions:
                # Skip protected third parties (Sonrai)
                if third_party.is_protected:
                    # Remove projectile but don't damage protected entity
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)
                    continue

                # Remove projectile
                if projectile in self.projectiles:
                    self.projectiles.remove(projectile)

                # Apply damage to third party
                eliminated = third_party.take_damage(projectile.damage)

                # Only handle blocking if third party health reached 0
                if eliminated:
                    self._handle_third_party_blocking(third_party)

    def _handle_zombie_elimination(self, zombie: Zombie) -> None:
        """
        Handle a zombie being eliminated.

        Args:
            zombie: The zombie that was hit
        """
        # ARCADE MODE: Queue elimination instead of immediate quarantine
        if self.arcade_manager.is_active():
            # Hide zombie immediately for visual feedback
            zombie.is_hidden = True

            # Queue for batch quarantine at end of session
            # Note: arcade_manager.queue_elimination also updates combo tracker internally
            self.arcade_manager.queue_elimination(zombie)

            # Queue zombie for respawn (dynamic spawning)
            self.arcade_manager.queue_zombie_for_respawn(zombie)

            # Update game state counters
            self.game_state.zombies_remaining -= 1

            logger.info(
                f"🎮 ARCADE: Queued {zombie.identity_name} for batch quarantine (combo: {self.arcade_manager.combo_tracker.get_combo_count()}x)"
            )
            return

        # NORMAL MODE: Immediate quarantine
        # NOTE: Approval system removed - zombies always quarantine when health reaches 0
        # The approval mechanic was blocking gameplay in production environments

        # IMMEDIATE FEEDBACK: Hide zombie right away (no lag)
        zombie.is_hidden = True
        zombie.mark_for_quarantine()

        # STORY MODE: Trigger educational dialogue on first kill
        if self.game_state.is_story_mode:
            # Update educational progress
            self.education_manager.progress.zombies_eliminated += 1

            # Get zombie attributes (use safe getattr for optional fields)
            account_id = getattr(zombie, "account", None)  # Zombie uses 'account' not 'account_id'
            identity_type = getattr(zombie, "identity_type", "User")  # Default to User if not set
            days_since_login = getattr(zombie, "days_since_login", "unknown")

            # Fetch permission data for this zombie (mock data for demo)
            permission_summary = self.iam_client.get_permissions(
                zombie.identity_name, identity_type, account_id
            )

            # Build context with permission data
            context = {
                "zombie_name": zombie.identity_name,
                "zombie_type": identity_type,
                "days_since_login": days_since_login,
                "account_id": account_id or "unknown",
                "permissions_count": permission_summary.total_policies,
                "permissions_list": ", ".join(permission_summary.attached_policies[:3]),
                "has_high_risk": permission_summary.has_high_risk,
                "high_risk_policies": ", ".join(permission_summary.high_risk_policies),
                "permission_summary": permission_summary.get_display_summary(max_policies=3),
            }

            # PRIORITY SYSTEM: Only show one dialogue per zombie kill
            # Check triggers in priority order and stop after first match

            # Priority 1: High-risk policy (most important)
            if permission_summary.has_high_risk:
                high_risk_context = {
                    **context,
                    "policy_name": (
                        permission_summary.high_risk_policies[0]
                        if permission_summary.high_risk_policies
                        else "Unknown"
                    ),
                }
                if self._trigger_education(TriggerType.FIRST_HIGH_RISK_POLICY, high_risk_context):
                    pass  # Dialogue shown, continue to quarantine

            # Priority 2: Milestones (5 kills, 10 kills)
            elif self.education_manager.progress.zombies_eliminated == 5:
                self._trigger_education(TriggerType.MILESTONE_5_KILLS, context)
            elif self.education_manager.progress.zombies_eliminated == 10:
                self._trigger_education(TriggerType.MILESTONE_10_KILLS, context)

            # Priority 3: First Role/User encounter
            elif identity_type.lower() == "role":
                self._trigger_education(TriggerType.FIRST_ROLE_ENCOUNTER, context)
            elif identity_type.lower() == "user":
                self._trigger_education(TriggerType.FIRST_USER_ENCOUNTER, context)

            # Priority 4: First kill (fallback)
            else:
                self._trigger_education(TriggerType.FIRST_ZOMBIE_KILL, context)

        # Quarantine immediately via API (no pause, no delay)
        self._quarantine_zombie(zombie)

    def _handle_third_party_blocking(self, third_party) -> None:
        """
        Handle a 3rd party being blocked.

        Args:
            third_party: The 3rd party that was hit
        """
        # IMMEDIATE FEEDBACK: Hide third party right away (no lag)
        third_party.is_hidden = True
        third_party.is_blocking = True

        # STORY MODE: Trigger educational dialogue on first third-party block
        if self.game_state.is_story_mode:
            context = {
                "third_party_name": getattr(third_party, "name", "Unknown"),
            }
            self._trigger_education(TriggerType.FIRST_THIRD_PARTY_BLOCK, context)

        # Block immediately via API (no pause, no delay)
        self._block_third_party(third_party)

    def _on_player_damaged(self, source_zombie: "Zombie") -> None:
        """
        Handle consequences when player takes damage.

        Args:
            source_zombie: The zombie that dealt the damage
        """
        logger.info(f"💔 Player damaged by {source_zombie.identity_name}!")

        # ARCADE MODE: Subtract from elimination count instead of respawning
        if self.arcade_manager.is_active():
            if self.arcade_manager.eliminations_count > 0:
                # Reduce elimination count by 1 (penalty for getting hit)
                self.arcade_manager.eliminations_count -= 1
                logger.info(
                    f"🎮 ARCADE: -1 elimination penalty! Count: {self.arcade_manager.eliminations_count}"
                )
            return

        # NORMAL MODE: Respawn a quarantined zombie as consequence
        self._respawn_quarantined_zombie()

    def _respawn_quarantined_zombie(self) -> None:
        """Respawn one previously quarantined zombie as damage consequence."""
        # Find a hidden/quarantined zombie to respawn
        quarantined = [z for z in self.zombies if z.is_hidden and not z.is_quarantining]

        if quarantined:
            zombie = quarantined[0]
            zombie.is_hidden = False
            zombie.health = zombie.max_health  # Reset health

            # Remove from quarantined set if tracked
            if zombie.identity_id in self.quarantined_identities:
                self.quarantined_identities.discard(zombie.identity_id)

            # Update counter
            self.game_state.zombies_remaining += 1

            logger.warning(f"⚠️ SECURITY BREACH! {zombie.identity_name} reactivated!")
            self.game_state.resource_message = f"⚠️ {zombie.identity_name} reactivated!"
            self.game_state.resource_message_timer = 2.0
        else:
            logger.info("No quarantined zombies to respawn")

    # NOTE: _on_player_death() removed - replaced by _show_game_over_screen()
    # Old implementation would auto-restart level and reset health
    # New implementation shows game over menu with Retry/Return to Lobby options

    def _show_pause_menu(self) -> None:
        """Show Zelda-style pause menu with options. Delegates to PauseMenuController."""
        # Determine if arcade mode option should be shown
        include_arcade = (
            self.game_state.status == GameStatus.PLAYING
            and self.game_state.current_level_account_id == "577945324761"
            and not self.arcade_manager.is_active()
        )

        # Show the menu via controller
        self.pause_menu_controller.show(include_arcade_option=include_arcade)

        # Build and set the pause message
        self.game_state.congratulations_message = self._build_pause_menu_message()
        self.game_state.previous_status = self.game_state.status
        self.game_state.status = GameStatus.PAUSED
        logger.info("⏸️  Game paused - showing menu")

    def _build_pause_menu_message(self) -> str:
        """Build the pause menu message. Delegates to PauseMenuController."""
        return self.pause_menu_controller.build_message(has_controller=self.joystick is not None)

    def _navigate_pause_menu(self, direction: int) -> None:
        """Navigate the pause menu. Delegates to PauseMenuController."""
        logger.info(f"🎮 _navigate_pause_menu called with direction={direction}")
        self.pause_menu_controller.navigate(direction)
        # Update the menu display
        self.game_state.congratulations_message = self._build_pause_menu_message()
        logger.info(
            f"🎮 After navigation: selected_index={self.pause_menu_controller.selected_index}, option='{self.pause_menu_controller.get_selected_option()}'"
        )

    def _execute_pause_menu_option(self) -> None:
        """Execute the selected pause menu option. Delegates to PauseMenuController."""
        logger.info(
            f"🎮 _execute_pause_menu_option called: selected_index={self.pause_menu_controller.selected_index}"
        )
        action = self.pause_menu_controller.select()

        if action == PauseMenuAction.RESUME:
            self.dismiss_message()
        elif action == PauseMenuAction.START_ARCADE:
            logger.info("🎮 ========== PAUSE MENU: Starting arcade mode ==========")
            logger.info(f"🎮 Previous status: {self.game_state.previous_status}")
            logger.info(f"🎮 Current status: {self.game_state.status}")
            self.game_state.congratulations_message = None
            self.game_state.status = self.game_state.previous_status
            logger.info(f"🎮 Status restored to: {self.game_state.status}")
            self._start_arcade_mode()
            logger.info(f"🎮 After start, arcade active: {self.arcade_manager.is_active()}")
            logger.info("🎮 ========================================================")
        elif action == PauseMenuAction.RETURN_TO_LOBBY:
            if self.game_state.previous_status in (
                GameStatus.PLAYING,
                GameStatus.BOSS_BATTLE,
            ):
                self.game_state.congratulations_message = None
                self._return_to_lobby()
            else:
                self.dismiss_message()
        elif action == PauseMenuAction.SAVE_GAME:
            self._save_game()
            logger.info("✅ Game saved from pause menu")
            # Update display with save confirmation (controller already set the flag)
            self.game_state.congratulations_message = self._build_pause_menu_message()
        elif action == PauseMenuAction.QUIT_GAME:
            logger.info("Saving game before quit...")
            self._save_game()
            self.running = False

    def _handle_level_entry_selection(self) -> None:
        """Handle level entry menu selection (Arcade or Story mode)."""
        action = self.level_entry_menu_controller.select()
        door = self._pending_door_entry

        if action == LevelEntryAction.ARCADE_MODE:
            logger.info("🕹️ Level entry: ARCADE MODE selected")
            self.level_entry_menu_controller.hide()
            self.game_state.congratulations_message = None
            self._pending_door_entry = None

            # Enter level with static genre, then start arcade mode
            if door:
                self._enter_level_with_static_genre(door)
                self._start_arcade_mode()

        elif action == LevelEntryAction.STORY_MODE:
            logger.info("📖 Level entry: STORY MODE selected")
            self.level_entry_menu_controller.hide()
            self.game_state.congratulations_message = None
            self._pending_door_entry = None

            # Enable Story Mode for educational dialogues
            self.game_state.is_story_mode = True
            logger.info("📚 Story Mode enabled - educational dialogues active")

            # Enter level with static genre
            if door:
                self._enter_level_with_static_genre(door)

    def _enter_level_with_static_genre(self, door) -> None:
        """Enter level with genre determined by level number.

        Args:
            door: Door being entered
        """
        from models import GenreType

        # Find level number for this door
        level_num = 1  # Default
        if self.level_manager:
            for level in self.level_manager.levels:
                if level.account_name == door.destination_room_name:
                    level_num = level.level_number
                    break

        # Get genre for this level
        genre = self.LEVEL_GENRE_MAP.get(level_num, GenreType.PLATFORMER)
        self.game_state.current_genre = genre
        logger.info(f"🎮 Level {level_num} genre: {genre.value}")

        if genre == GenreType.FIGHTING:
            # Boss battle mode - special handling
            logger.info(f"🥊 Entering BOSS BATTLE mode!")
            self._enter_level(door)
            # Spawn boss immediately for fighting mode
            if self.level_manager:
                level = self.level_manager.get_current_level()
                if level:
                    boss_type = BOSS_LEVEL_MAP.get(level.level_number, BossType.WANNACRY)
                    self._spawn_boss(boss_type)
        elif genre == GenreType.SPACE_SHOOTER:
            # Space shooter mode
            logger.info(f"🚀 Entering SPACE SHOOTER mode!")
            self._enter_level(door)
            self._init_space_shooter_controller()
        elif genre == GenreType.RACING:
            # Racing mode (Mario Kart style)
            logger.info(f"🏎️ Entering RACING mode!")
            self._enter_level(door)
            self._init_racing_controller()
        elif genre == GenreType.MAZE_CHASE:
            # Maze chase mode
            logger.info(f"👻 Entering MAZE CHASE mode!")
            self._enter_level(door)
            # TODO: Initialize maze chase controller
        else:
            # Standard platformer
            self._enter_level(door)

    def _init_space_shooter_controller(self) -> None:
        """Initialize space shooter controller for current level."""
        from models import GenreType
        from space_shooter_controller import SpaceShooterController

        self.active_genre_controller = SpaceShooterController(
            GenreType.SPACE_SHOOTER, self.screen_width, self.screen_height
        )

        # Set callback for zombie elimination to trigger quarantine API
        self.active_genre_controller.on_zombie_eliminated_callback = (
            self._on_space_shooter_zombie_eliminated
        )

        # Initialize with current zombies
        if self.level_manager:
            level = self.level_manager.get_current_level()
            if level:
                self.active_genre_controller.initialize_level(
                    level.account_id,
                    self.zombies,
                    self.screen_width,
                    self.screen_height,
                )
                logger.info(f"🚀 Space shooter initialized with {len(self.zombies)} zombies")

    def _on_space_shooter_zombie_eliminated(self, zombie) -> None:
        """Handle zombie elimination from space shooter mode - triggers quarantine API."""
        logger.info(f"🚀 Space shooter: Zombie {zombie.identity_name} eliminated!")

        # Mark zombie for quarantine (visual feedback already done by space shooter)
        zombie.mark_for_quarantine()

        # Use the standard quarantine method which handles:
        # - Removing from zombies list
        # - Updating game state counters
        # - Calling the API
        self._quarantine_zombie(zombie)

    def _init_racing_controller(self) -> None:
        """Initialize racing controller for current level."""
        from models import GenreType
        from racing_controller import RacingController

        self.active_genre_controller = RacingController(
            GenreType.RACING, self.screen_width, self.screen_height
        )

        # Set callback for zombie elimination to trigger quarantine API
        self.active_genre_controller.on_zombie_eliminated_callback = (
            self._on_racing_zombie_eliminated
        )

        # Initialize with current zombies
        if self.level_manager:
            level = self.level_manager.get_current_level()
            if level:
                self.active_genre_controller.initialize_level(
                    level.account_id,
                    self.zombies,
                    self.screen_width,
                    self.screen_height,
                )
                logger.info(f"🏎️ Racing initialized with {len(self.zombies)} zombies as racers")

    def _on_racing_zombie_eliminated(self, zombie) -> None:
        """Handle zombie elimination from racing mode - triggers quarantine API."""
        logger.info(f"🏎️ Racing: Racer {zombie.identity_name} eliminated!")

        # Mark zombie for quarantine
        zombie.mark_for_quarantine()

        # Use the standard quarantine method
        self._quarantine_zombie(zombie)

    def _handle_level_entry_cancel(self) -> None:
        """Handle level entry menu cancellation (return to lobby)."""
        logger.info("❌ Level entry: CANCELLED - returning to lobby")
        self.level_entry_menu_controller.cancel()
        self.game_state.congratulations_message = None
        self._pending_door_entry = None

        # Resume lobby state
        self.game_state.status = GameStatus.LOBBY

        # Push player away from door to prevent immediate re-trigger
        self.player.position.x -= 50

    def _show_game_over_screen(self) -> None:
        """Show game over screen when player health reaches 0."""
        logger.info("💀 GAME OVER - Player health depleted!")

        # Pause game
        self.game_state.previous_status = self.game_state.status
        self.game_state.status = GameStatus.PAUSED

        # Build game over message
        message = (
            "💀 SECURITY BREACH!\n\n"
            "All zombies have been released!\n"
            "All 3rd parties are now allowed!\n"
            "Services are unprotected!\n\n"
            f"Zombies Quarantined: {self.game_state.zombies_quarantined}\n\n"
            "▶ Retry Level\n"
            "  Return to Lobby"
        )

        self.game_state.congratulations_message = message
        self.game_over_menu_active = True

    def _navigate_game_over_menu(self, direction: int) -> None:
        """Navigate game over menu options."""
        if not hasattr(self, "game_over_selected_index"):
            self.game_over_selected_index = 0

        # Two options: Retry (0) or Return to Lobby (1)
        self.game_over_selected_index = (self.game_over_selected_index + direction) % 2

        # Rebuild message with new selection
        retry_text = "▶ Retry Level" if self.game_over_selected_index == 0 else "  Retry Level"
        lobby_text = (
            "▶ Return to Lobby" if self.game_over_selected_index == 1 else "  Return to Lobby"
        )

        message = (
            "💀 SECURITY BREACH!\n\n"
            "All zombies have been released!\n"
            "All 3rd parties are now allowed!\n"
            "Services are unprotected!\n\n"
            f"Zombies Quarantined: {self.game_state.zombies_quarantined}\n\n"
            f"{retry_text}\n"
            f"{lobby_text}"
        )

        self.game_state.congratulations_message = message

    def _execute_game_over_option(self) -> None:
        """Execute selected game over menu option."""
        if not hasattr(self, "game_over_selected_index"):
            self.game_over_selected_index = 0

        if self.game_over_selected_index == 0:
            # Retry Level
            logger.info("🔄 Retrying level...")
            self.game_over_menu_active = False
            self.game_state.congratulations_message = None

            # Reset player health
            self.player.current_health = self.player.max_health

            # Reset player position to start
            self.player.position.x = 100
            self.player.position.y = 400

            # Resume game
            self.game_state.status = self.game_state.previous_status

        elif self.game_over_selected_index == 1:
            # Return to Lobby
            logger.info("🏠 Returning to lobby...")
            self.game_over_menu_active = False
            self.game_state.congratulations_message = None
            self._return_to_lobby()

    def dismiss_message(self) -> None:
        """Dismiss the congratulations message and resume gameplay."""
        if self.game_state.status == GameStatus.PAUSED and self.game_state.congratulations_message:
            # No need to quarantine/block - already done immediately when entity was hit
            # Just clear the message and resume
            self.game_state.congratulations_message = None
            self.game_state.pending_elimination = None
            # Restore previous status (LOBBY or PLAYING) instead of hardcoding PLAYING
            if self.game_state.previous_status:
                self.game_state.status = self.game_state.previous_status
                self.game_state.previous_status = None
            else:
                # Fallback to PLAYING if previous_status wasn't set
                self.game_state.status = GameStatus.PLAYING

    def _advance_or_dismiss_dialogue(self) -> None:
        """Advance educational dialogue to next page or dismiss if complete."""
        if not self.game_state.is_dialogue_active:
            return

        dialogue = self.game_state.active_dialogue
        if dialogue.is_complete():
            # Dismiss dialogue
            self.education_manager.dismiss_dialogue()
            self.game_state.active_dialogue = None
            self.game_state.dialogue_format_kwargs = {}
            logger.info("📚 Educational dialogue dismissed")
        else:
            # Advance to next page
            dialogue.next_page()
            logger.info(f"📚 Advanced to dialogue page {dialogue.current_page + 1}")

    def _trigger_education(self, trigger_type: TriggerType, context: dict = None) -> bool:
        """
        Trigger an educational dialogue if conditions are met.

        Args:
            trigger_type: The type of educational trigger
            context: Optional context data (zombie_name, zombie_type, etc.)

        Returns:
            True if dialogue was triggered, False otherwise
        """
        if not self.game_state.is_story_mode:
            return False

        dialogue = self.education_manager.check_trigger(trigger_type, context)
        if dialogue:
            self.game_state.active_dialogue = dialogue
            self.game_state.dialogue_format_kwargs = context or {}
            logger.info(f"📚 Triggered educational dialogue: {trigger_type.value}")
            return True
        return False

    def _quarantine_zombie(self, zombie: Zombie) -> None:
        """
        Quarantine a zombie via the API (runs in background thread to prevent lag).

        Args:
            zombie: The zombie to quarantine
        """
        # OPTIMISTIC UPDATE: Update game state immediately for smooth gameplay
        # The API call happens in background - if it fails, we log it but don't freeze the game
        if zombie in self.zombies:
            self.zombies.remove(zombie)
            self.game_state.zombies_remaining -= 1
            self.game_state.zombies_quarantined += 1
            self.quarantined_identities.add(zombie.identity_id)

            # Check for boss spawn (all zombies cleared)
            if self.game_state.zombies_remaining == 0 and not self.boss_spawned:
                self._spawn_boss()
                logger.info("All zombies cleared! Spawning boss...")

        # Fire-and-forget API call in background thread
        def do_quarantine():
            try:
                # Extract root scope from full scope path
                root_scope = None
                if zombie.scope:
                    scope_parts = zombie.scope.split("/")
                    if len(scope_parts) >= 2:
                        root_scope = f"{scope_parts[0]}/{scope_parts[1]}"

                logger.info(f"🔍 [ASYNC] Quarantining: {zombie.identity_name}")

                result = self.api_client.quarantine_identity(
                    identity_id=zombie.identity_id,
                    identity_name=zombie.identity_name,
                    account=zombie.account,
                    scope=zombie.scope,
                    root_scope=root_scope,
                )

                if result.success:
                    logger.info(f"✅ [ASYNC] Quarantined {zombie.identity_name}")
                    # Save in background too (non-blocking)
                    self._save_game()
                else:
                    logger.error(f"❌ [ASYNC] Quarantine failed: {result.error_message}")

            except Exception as e:
                logger.error(f"❌ [ASYNC] Exception during quarantine: {e}")

        # Start background thread (daemon=True so it won't block game exit)
        thread = threading.Thread(target=do_quarantine, daemon=True)
        thread.start()

    def _block_third_party(self, third_party) -> None:
        """
        Block a 3rd party via the API (runs in background thread to prevent lag).

        Args:
            third_party: The 3rd party to block
        """
        # OPTIMISTIC UPDATE: Update game state immediately for smooth gameplay
        third_parties = self.get_third_parties()
        if third_party in third_parties:
            third_parties.remove(third_party)
            self.game_state.third_parties_blocked += 1
            self.blocked_third_parties.add(third_party.name)

        # Fire-and-forget API call in background thread
        def do_block():
            try:
                logger.info(f"🔍 [ASYNC] Blocking 3rd party: {third_party.name}")

                result = self.api_client.block_third_party(
                    third_party_id=third_party.third_party_id,
                    third_party_name=third_party.name,
                )

                if result.success:
                    logger.info(f"✅ [ASYNC] Blocked {third_party.name}")
                    self._save_game()
                else:
                    logger.error(f"❌ [ASYNC] Block failed: {result.error_message}")

            except Exception as e:
                logger.error(f"❌ [ASYNC] Exception during block: {e}")

        # Start background thread (daemon=True so it won't block game exit)
        thread = threading.Thread(target=do_block, daemon=True)
        thread.start()

    def handle_input(self, events: List[pygame.event.Event], screen: pygame.Surface = None) -> None:
        """
        Handle input events (keyboard and 8-bit controller).

        Args:
            events: List of Pygame events
            screen: Optional pygame surface for screenshot capture
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            # Handle controller hot-plugging
            elif event.type == pygame.JOYDEVICEADDED:
                # Controller connected - reinitialize
                logger.info(f"🎮 JOYDEVICEADDED event received (device_index={event.device_index})")
                print(f"🎮 Controller device added (device_index={event.device_index})")
                if self.joystick is None:
                    try:
                        joystick = pygame.joystick.Joystick(event.device_index)
                        joystick.init()
                        self.joystick = joystick
                        logger.info(f"🎮 ✅ Controller connected: {joystick.get_name()}")
                        print(f"🎮 ✅ Controller connected: {joystick.get_name()}")
                    except Exception as e:
                        logger.error(f"🎮 ❌ Failed to initialize controller: {e}")
                        print(f"🎮 ❌ Failed to initialize controller: {e}")

            elif event.type == pygame.JOYDEVICEREMOVED:
                # Controller disconnected
                logger.info(f"🎮 JOYDEVICEREMOVED event received (instance_id={event.instance_id})")
                print(f"🎮 Controller device removed")
                if self.joystick and self.joystick.get_instance_id() == event.instance_id:
                    logger.info(f"🎮 Controller disconnected: {self.joystick.get_name()}")
                    print(f"🎮 Controller disconnected: {self.joystick.get_name()}")
                    self.joystick = None
                    # Check if another controller is available
                    if pygame.joystick.get_count() > 0:
                        joystick = pygame.joystick.Joystick(0)
                        joystick.init()
                        self.joystick = joystick
                        logger.info(f"🎮 Switched to controller: {joystick.get_name()}")
                        print(f"🎮 Switched to controller: {joystick.get_name()}")

            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)

                # Handle photo booth consent input
                if (
                    getattr(self.game_state, "photo_booth_consent_active", False)
                    and self.photo_booth
                ):
                    if event.key in (
                        pygame.K_y,
                        pygame.K_a,
                        pygame.K_RETURN,
                        pygame.K_SPACE,
                    ):  # Y, A, ENTER, SPACE = Yes
                        logger.info("📸 User opted IN to selfie (keyboard)")
                        self.photo_booth.handle_consent_input(opted_in=True)
                        self._begin_arcade_session()
                        continue
                    elif event.key in (
                        pygame.K_n,
                        pygame.K_b,
                        pygame.K_ESCAPE,
                    ):  # N, B, ESC = No
                        logger.info("📸 User opted OUT of selfie (keyboard)")
                        self.photo_booth.handle_consent_input(opted_in=False)
                        self._begin_arcade_session()
                        continue

                # Handle photo booth summary dismissal (INSERT COIN TO CONTINUE)
                if getattr(self.game_state, "photo_booth_summary_active", False):
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_a):
                        logger.info("📸 User dismissed photo booth summary (keyboard)")
                        self._dismiss_photo_booth_summary()
                        continue

                # Handle educational dialogue input (Story Mode)
                if self.game_state.is_dialogue_active:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_a):
                        self._advance_or_dismiss_dialogue()
                        continue

                # Handle level entry menu navigation
                if self.level_entry_menu_controller.active:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.game_state.congratulations_message = (
                            self.level_entry_menu_controller.navigate(-1)
                        )
                        continue
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.game_state.congratulations_message = (
                            self.level_entry_menu_controller.navigate(1)
                        )
                        continue
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._handle_level_entry_selection()
                        continue
                    elif event.key == pygame.K_ESCAPE:
                        self._handle_level_entry_cancel()
                        continue

                # Handle pause menu navigation (if paused with menu active)
                if self.game_state.status == GameStatus.PAUSED:
                    # Check if we're showing arcade results menu
                    if (
                        self.arcade_results_options
                        and self.game_state.congratulations_message
                        and "ARCADE MODE COMPLETE" in self.game_state.congratulations_message
                    ):
                        # UP arrow or W - move selection up
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self._navigate_arcade_results_menu(-1)
                            continue
                        # DOWN arrow or S - move selection down
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self._navigate_arcade_results_menu(1)
                            continue
                        # ENTER or SPACE - execute selected option
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self._execute_arcade_results_option()
                            continue
                    # Check if we're showing the actual pause menu (not a different message)
                    elif (
                        self.game_state.congratulations_message
                        and "SECURITY BREACH" in self.game_state.congratulations_message
                    ):
                        # Game Over Menu Navigation
                        if event.key == pygame.K_UP:
                            self._navigate_game_over_menu(-1)
                            continue
                        elif event.key == pygame.K_DOWN:
                            self._navigate_game_over_menu(1)
                            continue
                        elif event.key == pygame.K_RETURN:
                            self._execute_game_over_option()
                            continue
                    elif (
                        self.game_state.congratulations_message
                        and "PAUSED" in self.game_state.congratulations_message
                    ):
                        # Pause Menu Navigation
                        if event.key == pygame.K_UP:
                            self._navigate_pause_menu(-1)
                            continue
                        elif event.key == pygame.K_DOWN:
                            self._navigate_pause_menu(1)
                            continue
                        elif event.key == pygame.K_RETURN:
                            self._execute_pause_menu_option()
                            continue
                        elif event.key == pygame.K_ESCAPE:
                            self.dismiss_message()
                            continue

                # Cheat code detection - delegates to CheatCodeController
                cheat_result = self.cheat_code_controller.process_key(event.key)

                if cheat_result.action == CheatCodeAction.UNLOCK_ALL_LEVELS:
                    self.game_state.congratulations_message = cheat_result.message
                    self.game_state.previous_status = self.game_state.status
                    self.game_state.status = GameStatus.PAUSED

                elif cheat_result.action == CheatCodeAction.SKIP_LEVEL:
                    if self.game_state.status == GameStatus.PLAYING and self.level_manager:
                        current_level = self.level_manager.levels[
                            self.level_manager.current_level_index
                        ]
                        logger.info(f"🔓 CHEAT: Skipping level {current_level.account_name}")
                        self._return_to_lobby(mark_completed=True)

                elif cheat_result.action == CheatCodeAction.SPAWN_BOSS:
                    self._spawn_boss()

                elif cheat_result.action == CheatCodeAction.START_ARCADE:
                    # Only activate in Sandbox account
                    if self.game_state.status == GameStatus.PLAYING:
                        if self.game_state.current_level_account_id == "577945324761":
                            self._start_arcade_mode()
                        else:
                            logger.info("⚠️  Arcade mode only available in Sandbox account")

                elif cheat_result.action == CheatCodeAction.TRIGGER_OUTAGE:
                    # Manually trigger a production outage (for testing)
                    if self.game_state.status == GameStatus.PLAYING:
                        self.outage_manager.trigger()
                        logger.info("🚨 CHEAT: Production outage triggered!")

                # Handle boss dialogue dismissal (ENTER key only)
                if event.key == pygame.K_RETURN:
                    if self.boss_dialogue_controller.is_showing:
                        # Dismiss dialogue and spawn the cyber boss
                        self.boss_dialogue_controller.dismiss()
                        self._spawn_cyber_boss()
                        continue

                # Handle message dismissal and quest trigger (ENTER or SPACE key)
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    # Check for quest dialog dismissal and hacker spawn
                    if self.quest_manager and self.game_state.quest_message:
                        from models import QuestStatus

                        active_quest = self.quest_manager.get_quest_for_level(
                            self.game_state.current_level
                        )
                        if active_quest and active_quest.status == QuestStatus.TRIGGERED:
                            # Dismiss quest dialog
                            self.game_state.quest_message = None

                            # Spawn hacker ON GROUND near player for side-by-side race!
                            spawn_x = self.player.position.x - 50  # Slightly behind player
                            spawn_y = 832 - 32  # On the ground (ground_y - hacker_height)
                            self.hacker = Hacker(
                                spawn_position=Vector2(spawn_x, spawn_y),
                                target_position=active_quest.service_position,
                            )

                            # Start the race!
                            active_quest.status = QuestStatus.ACTIVE
                            active_quest.hacker_spawned = True

                            # Spawn powerups along the race path to help player win
                            self._spawn_hacker_challenge_powerups(
                                self.player.position.x,
                                active_quest.service_position.x,
                            )

                            logger.info(
                                f"⌨️  RACE STARTED! Hacker spawned at ({spawn_x}, {spawn_y})"
                            )
                            continue
                    # If there's a pause message showing, dismiss it
                    elif self.game_state.status == GameStatus.PAUSED:
                        self.dismiss_message()
                        continue

                # PLATFORMER CONTROLS: Jump with UP or W (only in level mode, not lobby)
                if event.key in (pygame.K_UP, pygame.K_w):
                    if self.game_state.status in (
                        GameStatus.PLAYING,
                        GameStatus.BOSS_BATTLE,
                    ):
                        self.player.jump()
                    # In LOBBY mode, UP/W is handled by continuous movement for top-down navigation

                # Handle firing (works in lobby, playing, and boss battle)
                # But not when quest dialog is showing (handled above)
                if event.key == pygame.K_SPACE:
                    # Skip if quest dialog is showing (already handled above)
                    if self.quest_manager and self.game_state.quest_message:
                        continue
                    if self.game_state.status in (
                        GameStatus.LOBBY,
                        GameStatus.PLAYING,
                        GameStatus.BOSS_BATTLE,
                    ):
                        projectile = self.player.fire_projectile()
                        self.projectiles.append(projectile)

                # F12 - Screenshot (deferred until after render completes)
                if event.key == pygame.K_F12:
                    self.evidence_capture.request_screenshot()
                    continue

                # F9 - Toggle Recording
                elif event.key == pygame.K_F9:
                    current_time = time.time()
                    result = self.evidence_capture.toggle_recording(current_time)
                    if result:
                        logger.info(f"🎬 Recording saved: {result}")
                    continue

                # ESC key - Pause/Resume or Quit
                if event.key == pygame.K_ESCAPE:
                    if self.game_state.status == GameStatus.PAUSED:
                        # Resume game
                        self.dismiss_message()
                    elif self.game_state.status in (
                        GameStatus.PLAYING,
                        GameStatus.BOSS_BATTLE,
                    ):
                        # Show pause menu
                        self._show_pause_menu()
                    else:
                        # In lobby - quit game
                        logger.info("Saving game before exit...")
                        self._save_game()
                        self.running = False

                # L key - Return to lobby (from levels only)
                elif event.key == pygame.K_l:
                    if self.game_state.status in (
                        GameStatus.PLAYING,
                        GameStatus.BOSS_BATTLE,
                    ):
                        logger.info("🏠 L key pressed - returning to lobby")
                        self._return_to_lobby()

                # M key - Toggle Landing Zone View (lobby only)
                elif event.key == pygame.K_m:
                    if self.game_state.status == GameStatus.LOBBY and self.game_map:
                        self.game_map.toggle_landing_zone_view()
                        if self.game_map.landing_zone_view:
                            logger.info("🗺️ Entered Landing Zone View (zoomed out)")
                            # Reveal all zombies in landing zone view (but not during arcade mode)
                            if not self.arcade_manager.is_active():
                                for zombie in self.zombies:
                                    zombie.is_hidden = False
                        else:
                            logger.info("🔍 Exited Landing Zone View (normal zoom)")

            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)

            # Controller button events
            elif event.type == pygame.JOYBUTTONDOWN:
                # Log ALL button presses for debugging (even if joystick is None)
                logger.info(
                    f"🎮 JOYBUTTONDOWN event: button={event.button}, joystick={self.joystick is not None}"
                )

                # Handle photo booth consent input (controller)
                consent_active = getattr(self.game_state, "photo_booth_consent_active", False)
                logger.info(
                    f"📸 CONSENT CHECK: active={consent_active}, photo_booth={self.photo_booth is not None}, button={event.button}"
                )
                if consent_active and self.photo_booth:
                    logger.info(
                        f"📸 PRE-CONSENT: state={self.photo_booth.state}, "
                        f"camera_available={self.photo_booth.is_camera_available}, "
                        f"webcam_exists={self.photo_booth._webcam is not None}"
                    )
                    # Accept EITHER A (0) or B (1) as "Yes" for selfie - some controllers have swapped buttons
                    # This ensures the user can opt-in regardless of button mapping
                    if event.button == 0 or event.button == 1:
                        logger.info(f"📸 User opted IN to selfie (button {event.button})")
                        self.photo_booth.handle_consent_input(opted_in=True)
                        logger.info(
                            f"📸 POST-CONSENT: selfie_opted_in={self.photo_booth.selfie_opted_in}, "
                            f"state={self.photo_booth.state}"
                        )
                        self._begin_arcade_session()
                        continue

                # Handle photo booth summary dismissal (INSERT COIN TO CONTINUE)
                if getattr(self.game_state, "photo_booth_summary_active", False):
                    if event.button == 0 or event.button == 1:  # A or B button = dismiss
                        logger.info(
                            f"📸 User dismissed photo booth summary (button {event.button})"
                        )
                        self._dismiss_photo_booth_summary()
                        continue

                # Handle educational dialogue input (Story Mode) - controller
                if self.game_state.is_dialogue_active:
                    if event.button == 0:  # A button = advance/dismiss dialogue
                        self._advance_or_dismiss_dialogue()
                        continue

                # Handle level entry menu navigation (controller)
                if self.level_entry_menu_controller.active:
                    # D-pad UP (11) - navigate up
                    if event.button == 11:
                        self.game_state.congratulations_message = (
                            self.level_entry_menu_controller.navigate(-1)
                        )
                        continue
                    # D-pad DOWN (12) - navigate down
                    elif event.button == 12:
                        self.game_state.congratulations_message = (
                            self.level_entry_menu_controller.navigate(1)
                        )
                        continue
                    # A button (0) - confirm selection
                    elif event.button == 0:
                        self._handle_level_entry_selection()
                        continue
                    # B button (1) - cancel
                    elif event.button == 1:
                        self._handle_level_entry_cancel()
                        continue

                # Evidence capture - works even without joystick initialized
                # X button (2) or Star button (10) = Screenshot (deferred until after render)
                if event.button == 2 or event.button == 10:
                    self.evidence_capture.request_screenshot()
                    logger.info(f"📸 Screenshot requested by button {event.button}")
                    continue
                # Y button (3) = Toggle Recording
                elif event.button == 3:
                    current_time = time.time()
                    result = self.evidence_capture.toggle_recording(current_time)
                    if result:
                        logger.info(f"🎬 Recording saved: {result}")
                    continue

                if self.joystick:
                    # Log button press for debugging
                    logger.info(f"🎮 Controller button pressed: {event.button}")

                    # Check for controller cheat codes (D-pad only)
                    cheat_result = self.cheat_code_controller.process_controller_button(
                        event.button
                    )
                    if cheat_result.action == CheatCodeAction.SPAWN_BOSS:
                        # Spawn boss if in appropriate level
                        # Note: Don't show cheat message - _spawn_boss() handles the boss dialogue flow
                        if self.game_state.status == GameStatus.PLAYING:
                            self._spawn_boss()
                        continue

                    # Handle pause menu navigation with controller
                    if self.game_state.status == GameStatus.PAUSED:
                        # Check if we're showing arcade results menu
                        if (
                            self.arcade_results_options
                            and self.game_state.congratulations_message
                            and "ARCADE MODE COMPLETE" in self.game_state.congratulations_message
                        ):
                            # D-pad UP (11) - navigate up
                            if event.button == 11:
                                self._navigate_arcade_results_menu(-1)
                                continue
                            # D-pad DOWN (12) - navigate down
                            elif event.button == 12:
                                self._navigate_arcade_results_menu(1)
                                continue
                            # A button (0) or B button (1) - confirm selection
                            elif event.button in (0, 1):
                                self._execute_arcade_results_option()
                                continue
                        # Check if we're showing game over menu
                        elif (
                            self.game_state.congratulations_message
                            and "SECURITY BREACH" in self.game_state.congratulations_message
                        ):
                            # D-pad UP (11) - navigate up
                            if event.button == 11:
                                self._navigate_game_over_menu(-1)
                                continue
                            # D-pad DOWN (12) - navigate down
                            elif event.button == 12:
                                self._navigate_game_over_menu(1)
                                continue
                            # A button (0) - confirm selection
                            elif event.button == 0:
                                self._execute_game_over_option()
                                continue
                        # Check if we're showing the actual pause menu
                        elif (
                            self.game_state.congratulations_message
                            and "PAUSED" in self.game_state.congratulations_message
                        ):
                            # D-pad UP (11) - navigate up
                            if event.button == 11:
                                self._navigate_pause_menu(-1)
                                continue
                            # D-pad DOWN (12) - navigate down
                            elif event.button == 12:
                                self._navigate_pause_menu(1)
                                continue
                            # A button (0) - confirm selection
                            elif event.button == 0:
                                self._execute_pause_menu_option()
                                continue
                            # B button (1) or Start (7) - cancel and return to game
                            elif event.button == 1 or event.button == 7:
                                self.dismiss_message()
                                continue

                    # A button (0) - Universal message dismissal (like ENTER) OR Fire
                    if event.button == 0:
                        # PRIORITY 1: Boss dialogue dismissal
                        if self.boss_dialogue_controller.is_showing:
                            self.boss_dialogue_controller.dismiss()
                            self._spawn_cyber_boss()
                            continue

                        # PRIORITY 2: Universal message dismissal (works like ENTER key)
                        if self.game_state.congratulations_message:
                            self.dismiss_message()
                            continue  # Don't process other A button actions

                        # If no message, A button fires projectile
                        if self.game_state.status in (
                            GameStatus.LOBBY,
                            GameStatus.PLAYING,
                            GameStatus.BOSS_BATTLE,
                        ):
                            projectile = self.player.fire_projectile()
                            self.projectiles.append(projectile)
                    # B button (1) - Jump (only in level mode) OR dismiss messages OR start quest
                    elif event.button == 1:
                        # Check for quest dialog dismissal and hacker spawn
                        if self.quest_manager and self.game_state.quest_message:
                            from models import QuestStatus

                            active_quest = self.quest_manager.get_quest_for_level(
                                self.game_state.current_level
                            )
                            if active_quest and active_quest.status == QuestStatus.TRIGGERED:
                                # Dismiss quest dialog
                                self.game_state.quest_message = None

                                # Spawn hacker ON GROUND near player for side-by-side race!
                                spawn_x = self.player.position.x - 50  # Slightly behind player
                                spawn_y = 832 - 32  # On the ground (ground_y - hacker_height)
                                self.hacker = Hacker(
                                    spawn_position=Vector2(spawn_x, spawn_y),
                                    target_position=active_quest.service_position,
                                )

                                # Start the race!
                                active_quest.status = QuestStatus.ACTIVE
                                active_quest.hacker_spawned = True

                                # Spawn powerups along the race path to help player win
                                self._spawn_hacker_challenge_powerups(
                                    self.player.position.x,
                                    active_quest.service_position.x,
                                )

                                logger.info(
                                    f"🎮 RACE STARTED! Hacker spawned at ({spawn_x}, {spawn_y})"
                                )
                                continue
                        # If there's a message showing, dismiss it
                        elif (
                            self.game_state.status == GameStatus.PAUSED
                            and self.game_state.congratulations_message
                        ):
                            self.dismiss_message()
                        elif self.game_state.status in (
                            GameStatus.PLAYING,
                            GameStatus.BOSS_BATTLE,
                        ):
                            self.player.jump()
                    # Start/Select button (6, 7, or 9 depending on controller) - Pause menu / Dismiss messages
                    # Button 6 = Select on some controllers, Start on others
                    # Button 7 = Start on 8BitDo SN30 Pro
                    # Button 9 = Start on some Xbox-style controllers
                    elif event.button in (6, 7, 9):
                        logger.info(
                            f"🎮 Start/Pause button pressed (button {event.button}), game state: {self.game_state.status}"
                        )
                        if self.game_state.status == GameStatus.PAUSED:
                            self.dismiss_message()
                        elif self.game_state.status in (
                            GameStatus.LOBBY,
                            GameStatus.PLAYING,
                            GameStatus.BOSS_BATTLE,
                        ):
                            # Toggle pause menu
                            logger.info("🎮 Showing pause menu...")
                            self._show_pause_menu()

                    # Star/Home button (10) - Disabled to prevent accidental lobby exit
                    # Users should use pause menu (Start → Return to Lobby)
                    elif event.button == 10:
                        logger.info("ℹ️ Star button - use Start for pause menu")
                        pass  # Disabled

        # Handle continuous movement
        # LOBBY MODE: Top-down movement (4-directional)
        # Skip continuous movement if paused (prevents interference with menu navigation)
        if self.game_state.status == GameStatus.LOBBY:
            # Check keyboard input
            keyboard_left = pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed
            keyboard_right = pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed
            keyboard_up = pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed
            keyboard_down = pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed

            # Check controller unlock combo (L1 + R1 + Start)
            if self.joystick and not self.controller_unlock_combo_triggered:
                if self.cheat_code_controller.check_controller_unlock_combo(self.joystick):
                    self.controller_unlock_combo_triggered = True
                    self.cheat_code_controller.enable_unlock()
                    logger.info("🔓 CONTROLLER UNLOCK COMBO ACTIVATED! (L + R + Start)")
                    self.game_state.congratulations_message = (
                        "🔓 CHEAT ACTIVATED\n\n"
                        "All Levels Unlocked!\n\n"
                        "(L + R + Start)\n\n"
                        "Press A to continue"
                    )
                    self.game_state.previous_status = self.game_state.status
                    self.game_state.status = GameStatus.PAUSED

            # Check controller D-pad/analog stick
            controller_left = False
            controller_right = False
            controller_up = False
            controller_down = False
            if self.joystick:
                # D-pad buttons (for controllers without hat, like 8BitDo in X-input mode)
                if self.joystick.get_numbuttons() > 14:
                    if self.joystick.get_button(11):  # D-pad UP
                        controller_up = True
                    if self.joystick.get_button(12):  # D-pad DOWN
                        controller_down = True
                    if self.joystick.get_button(13):  # D-pad LEFT
                        controller_left = True
                    if self.joystick.get_button(14):  # D-pad RIGHT
                        controller_right = True

                # D-pad (hat) - primary for 8BitDo
                if self.joystick.get_numhats() > 0:
                    hat = self.joystick.get_hat(0)
                    if hat[0] < 0:
                        controller_left = True
                    elif hat[0] > 0:
                        controller_right = True
                    if hat[1] > 0:
                        controller_up = True  # Hat Y-axis: positive = UP (pressed up)
                    elif hat[1] < 0:
                        controller_down = True  # Hat Y-axis: negative = DOWN (pressed down)

                # Left analog stick (axis 0 and 1) - backup
                if self.joystick.get_numaxes() > 1:
                    axis_x = self.joystick.get_axis(0)
                    axis_y = self.joystick.get_axis(1)
                    if axis_x < -0.3:  # Deadzone
                        controller_left = True
                    elif axis_x > 0.3:
                        controller_right = True
                    if axis_y < -0.3:
                        controller_up = True  # Stick Y-axis: negative = UP (push stick up)
                    elif axis_y > 0.3:
                        controller_down = True  # Stick Y-axis: positive = DOWN (push stick down)

                # Right analog stick (axis 3 or 4) - zoom control in lobby
                # Axis 3 is typically right stick Y on most controllers
                if self.joystick.get_numaxes() > 3 and self.game_map:
                    right_stick_y = self.joystick.get_axis(3)
                    if right_stick_y < -0.5:  # Right stick UP = zoom out
                        if not self.game_map.landing_zone_view:
                            self.game_map.toggle_landing_zone_view()
                            logger.info("🗺️ Right stick UP - Entered Landing Zone View")
                            # Reveal zombies (but not during arcade mode)
                            if not self.arcade_manager.is_active():
                                for zombie in self.zombies:
                                    zombie.is_hidden = False
                    elif right_stick_y > 0.5:  # Right stick DOWN = zoom in
                        if self.game_map.landing_zone_view:
                            self.game_map.toggle_landing_zone_view()
                            logger.info("🔍 Right stick DOWN - Exited Landing Zone View")

            # Horizontal movement (keyboard or controller)
            if keyboard_left or controller_left:
                self.player.move_left()
            elif keyboard_right or controller_right:
                self.player.move_right()
            else:
                self.player.stop_horizontal()

            # Vertical movement (keyboard or controller)
            if keyboard_up or controller_up:
                self.player.move_up()
                logger.info(
                    f"UP pressed in lobby, velocity.y = {self.player.velocity.y}, position.y = {self.player.position.y}"
                )
            elif keyboard_down or controller_down:
                self.player.move_down()
                logger.info(
                    f"DOWN pressed in lobby, velocity.y = {self.player.velocity.y}, position.y = {self.player.position.y}"
                )
            else:
                self.player.stop_vertical()

        # LEVEL MODE: Platformer movement (left/right + jump)
        elif self.game_state.status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
            # Block input during production outage (player is "fixing prod")
            if self.outage_manager.is_active():
                self.player.stop_horizontal()
                return  # Don't process any movement input during outage

            # If genre controller is active, delegate input to it
            if self.active_genre_controller:
                from genre_controller import InputState

                keyboard_left = (
                    pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed
                )
                keyboard_right = (
                    pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed
                )
                keyboard_up = pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed
                keyboard_down = (
                    pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed
                )
                keyboard_shoot = pygame.K_SPACE in self.keys_pressed
                input_state = InputState(
                    left=keyboard_left,
                    right=keyboard_right,
                    up=keyboard_up,
                    down=keyboard_down,
                    shoot=keyboard_shoot,
                    jump=keyboard_up,  # Jump = up for platformer genres
                )
                self.active_genre_controller.handle_input(input_state, self.player)
                return  # Skip default platformer input handling

            # Check keyboard input
            keyboard_left = pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed
            keyboard_right = pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed
            keyboard_down = pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed

            # Check controller D-pad/analog stick
            controller_left = False
            controller_right = False
            controller_down = False
            controller_jump = False  # Continuous jump button check
            if self.joystick:
                # D-pad buttons (for controllers without hat, like 8BitDo in X-input mode)
                if self.joystick.get_numbuttons() > 14:
                    if self.joystick.get_button(12):  # D-pad DOWN
                        controller_down = True
                    if self.joystick.get_button(13):  # D-pad LEFT
                        controller_left = True
                    if self.joystick.get_button(14):  # D-pad RIGHT
                        controller_right = True

                # D-pad (hat)
                if self.joystick.get_numhats() > 0:
                    hat = self.joystick.get_hat(0)
                    if hat[0] < 0:
                        controller_left = True
                    elif hat[0] > 0:
                        controller_right = True
                    if hat[1] < 0:
                        controller_down = True

                # Left analog stick (axis 0 and 1)
                if self.joystick.get_numaxes() > 0:
                    axis_x = self.joystick.get_axis(0)
                    if axis_x < -0.3:  # Deadzone
                        controller_left = True
                    elif axis_x > 0.3:
                        controller_right = True

                if self.joystick.get_numaxes() > 1:
                    axis_y = self.joystick.get_axis(1)
                    if axis_y > 0.3:  # Down on stick
                        controller_down = True

                # Check B button (1) for jump - continuous state
                if self.joystick.get_numbuttons() > 1:
                    if self.joystick.get_button(1):  # B button held
                        controller_jump = True

            # Check keyboard jump
            keyboard_jump = pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed

            # Apply movement
            if keyboard_left or controller_left:
                self.player.move_left()
            elif keyboard_right or controller_right:
                self.player.move_right()
            else:
                self.player.stop_horizontal()

            # Handle jumping (continuous check allows jump+move simultaneously)
            if keyboard_jump or controller_jump:
                self.player.jump()

            # Handle crouching
            if keyboard_down or controller_down:
                self.player.crouch()
            else:
                self.player.stand_up()

    def is_running(self) -> bool:
        """
        Check if the game is still running.

        Returns:
            True if running, False otherwise
        """
        return self.running

    def get_game_state(self) -> GameState:
        """
        Get the current game state.

        Returns:
            Current GameState
        """
        return self.game_state

    def get_player(self) -> Player:
        """Get the player instance."""
        return self.player

    def get_zombies(self) -> List[Zombie]:
        """Get the list of zombies."""
        return self.zombies

    def get_projectiles(self) -> List[Projectile]:
        """Get the list of projectiles."""
        return self.projectiles

    def get_powerups(self) -> List:
        """Get the list of active power-ups."""
        return self.powerups

    def get_boss(self) -> Optional[Boss]:
        """Get the boss instance (None if no boss active)."""
        return self.boss

    def get_scroll_offset(self) -> float:
        """Get the current scroll offset."""
        return self.scroll_offset

    # Backwards compatibility properties for pause menu (delegates to PauseMenuController)
    @property
    def pause_menu_options(self) -> List[str]:
        """Get pause menu options. Backwards compatibility for PauseMenuController."""
        return self.pause_menu_controller.options

    @pause_menu_options.setter
    def pause_menu_options(self, value: List[str]) -> None:
        """Set pause menu options. Backwards compatibility for PauseMenuController."""
        self.pause_menu_controller.options = value

    @property
    def pause_menu_selected_index(self) -> int:
        """Get pause menu selected index. Backwards compatibility for PauseMenuController."""
        return self.pause_menu_controller.selected_index

    @pause_menu_selected_index.setter
    def pause_menu_selected_index(self, value: int) -> None:
        """Set pause menu selected index. Backwards compatibility for PauseMenuController."""
        self.pause_menu_controller.selected_index = value

    # Backwards compatibility properties for arcade results menu (delegates to ArcadeResultsController)
    @property
    def arcade_results_options(self) -> List[str]:
        """Get arcade results options. Backwards compatibility for ArcadeResultsController."""
        return self.arcade_results_controller.options

    @arcade_results_options.setter
    def arcade_results_options(self, value: List[str]) -> None:
        """Set arcade results options. Backwards compatibility for ArcadeResultsController."""
        self.arcade_results_controller.options = value

    @property
    def arcade_results_selected_index(self) -> int:
        """Get arcade results selected index. Backwards compatibility for ArcadeResultsController."""
        return self.arcade_results_controller.selected_index

    @arcade_results_selected_index.setter
    def arcade_results_selected_index(self, value: int) -> None:
        """Set arcade results selected index. Backwards compatibility for ArcadeResultsController."""
        self.arcade_results_controller.selected_index = value

    # Backwards compatibility property for cheat system (delegates to CheatCodeController)
    @property
    def cheat_enabled(self) -> bool:
        """Get cheat unlock state. Backwards compatibility for CheatCodeController."""
        return self.cheat_code_controller.unlock_enabled

    @cheat_enabled.setter
    def cheat_enabled(self, value: bool) -> None:
        """Set cheat unlock state. Backwards compatibility for CheatCodeController."""
        if value:
            self.cheat_code_controller.enable_unlock()
        else:
            self.cheat_code_controller.disable_unlock()

    # Backwards compatibility properties for boss dialogue (delegates to BossDialogueController)
    @property
    def showing_boss_dialogue(self) -> bool:
        """Get boss dialogue visibility. Backwards compatibility for BossDialogueController."""
        return self.boss_dialogue_controller.is_showing

    @property
    def boss_dialogue_content(self) -> Optional[dict]:
        """Get boss dialogue content as dict. Backwards compatibility for BossDialogueController."""
        if self.boss_dialogue_controller.content:
            return {
                "title": self.boss_dialogue_controller.content.title,
                "description": self.boss_dialogue_controller.content.description,
                "how_attacked": self.boss_dialogue_controller.content.how_attacked,
                "victims": self.boss_dialogue_controller.content.victims,
                "prevention": self.boss_dialogue_controller.content.prevention,
                "mechanic": self.boss_dialogue_controller.content.mechanic,
            }
        return None

    @property
    def boss_dialogue_shown(self) -> bool:
        """Check if dialogue was shown. Backwards compatibility for BossDialogueController."""
        return self.boss_dialogue_controller.has_been_shown

    def distribute_zombies(self) -> None:
        """Distribute zombies across the level space."""
        if not self.zombies:
            logger.warning("No zombies to distribute!")
            return

        if self.use_map and self.game_map:
            # Map mode: scatter zombies randomly across the floorplan
            self.game_map.scatter_zombies(self.zombies)
            logger.info(f"Scattered {len(self.zombies)} zombies across the re:invent floorplan")
        else:
            # Classic mode: distribute zombies across a wide horizontal space
            # Start from 200 pixels so some are visible immediately
            level_width = self.screen_width * 10  # 10 screens wide
            spacing = level_width / len(self.zombies)

            for i, zombie in enumerate(self.zombies):
                # Distribute horizontally starting from x=200
                x = 200 + (i * spacing)
                # Vary vertical position across 5 rows
                y = 100 + ((i % 5) * 80)

                zombie.position = Vector2(x, y)
                zombie.is_hidden = False  # All visible in classic mode

            logger.info(
                f"Distributed {len(self.zombies)} zombies. First zombie at ({self.zombies[0].position.x}, {self.zombies[0].position.y})"
            )

    def spawn_powerups(self) -> None:
        """
        Spawn AWS-themed power-ups ON platforms for exploration reward.

        Validates all dependencies before spawning to ensure stability.
        Gracefully handles missing platforms or invalid game state.
        """
        # Validation 1: Check if using map-based mode
        if not self.use_map:
            logger.debug("Not using map mode - powerups skipped")
            return

        # Validation 2: Check game map exists
        if not self.game_map:
            logger.warning("Cannot spawn powerups - no game map initialized")
            return

        # Validation 3: Check platform positions attribute exists
        if not hasattr(self.game_map, "platform_positions"):
            logger.error("GameMap missing platform_positions attribute - powerups skipped")
            return

        # Validation 4: Check platform positions is not None or empty
        if not self.game_map.platform_positions:
            logger.warning("No platforms available for power-up placement (empty list)")
            return

        # Validation 5: Verify we're in platformer mode (not lobby)
        if hasattr(self.game_map, "mode") and self.game_map.mode != "platformer":
            logger.debug(f"Powerups only spawn in platformer mode (current: {self.game_map.mode})")
            return

        try:
            import random

            from powerup import PowerUp, PowerUpType

            # More power-ups in sandbox for help (1 per 50 zombies, minimum 6, maximum 12)
            num_powerups = min(12, max(6, len(self.zombies) // 50))

            # Prioritize EARLY platforms (first 3000 pixels) so players see powerups quickly
            early_platforms = [p for p in self.game_map.platform_positions if 100 < p[0] < 3000]
            later_platforms = [p for p in self.game_map.platform_positions if p[0] >= 3000]

            if not early_platforms:
                logger.warning("No early platforms available for powerup spawning")
                return

            # Spawn most powerups (70%) in early section, rest scattered later
            num_early = int(num_powerups * 0.7)
            num_later = num_powerups - num_early

            selected_platforms = []
            if early_platforms:
                selected_platforms.extend(
                    random.sample(early_platforms, min(num_early, len(early_platforms)))
                )
            if later_platforms and num_later > 0:
                selected_platforms.extend(
                    random.sample(later_platforms, min(num_later, len(later_platforms)))
                )

            # Create power-ups on selected platforms
            # Star Power (*) should be RARE (AWS wildcard reference)
            # Lambda Speed (λ) should be COMMON for early gameplay boost
            self.powerups = []

            # Star power is rare - only 15% chance (1-2 stars in a typical level)
            star_ratio = 0.15

            for platform_x, platform_y, platform_width in selected_platforms:
                # Place power-up on top of platform (slightly above surface)
                powerup_x = platform_x
                powerup_y = platform_y - 40  # Above platform top

                # Choose power-up type with weighted distribution
                if random.random() < star_ratio:
                    powerup_type = PowerUpType.STAR_POWER  # Star power (best!)
                else:
                    # Lambda speed boost for the remaining power-ups
                    powerup_type = PowerUpType.LAMBDA_SPEED

                powerup = PowerUp(Vector2(powerup_x, powerup_y), powerup_type)
                self.powerups.append(powerup)

            star_count = sum(1 for p in self.powerups if p.powerup_type == PowerUpType.STAR_POWER)
            logger.info(
                f"✨ Spawned {len(self.powerups)} power-ups ON platforms ({star_count} stars)"
            )

        except Exception as e:
            logger.error(f"Failed to spawn powerups: {e}", exc_info=True)
            self.powerups = []  # Ensure powerups list exists even on failure

    def _spawn_hacker_challenge_powerups(self, start_x: float, end_x: float) -> None:
        """
        Spawn powerups along the path for the hacker challenge race.

        Places Lambda Speed and Star Power powerups on the ground between the
        player's current position and the service icon to help them win the race.

        Args:
            start_x: Player's starting x position
            end_x: Service icon's x position (race finish line)
        """
        try:
            import random

            # Ground level for platformer
            ground_y = 832

            # Calculate distance and spawn 4-6 powerups along the path
            distance = end_x - start_x
            num_powerups = 5  # Good amount to help win the race

            # Space powerups evenly along the race path
            spacing = distance / (num_powerups + 1)

            challenge_powerups = []
            for i in range(num_powerups):
                # Position powerup along the path
                powerup_x = start_x + spacing * (i + 1)
                # Place slightly above ground level so they're visible and collectible
                powerup_y = ground_y - 48

                # 40% Star Power (invincibility helps a lot!), 60% Lambda Speed
                if random.random() < 0.4:
                    powerup_type = PowerUpType.STAR_POWER
                else:
                    powerup_type = PowerUpType.LAMBDA_SPEED

                powerup = PowerUp(Vector2(powerup_x, powerup_y), powerup_type)
                challenge_powerups.append(powerup)

            # Add to existing powerups
            self.powerups.extend(challenge_powerups)

            star_count = sum(
                1 for p in challenge_powerups if p.powerup_type == PowerUpType.STAR_POWER
            )
            speed_count = len(challenge_powerups) - star_count

            logger.info(
                f"🎁 Spawned {len(challenge_powerups)} hacker challenge powerups "
                f"({star_count} stars, {speed_count} speed boosts) from x={start_x:.0f} to x={end_x:.0f}"
            )

        except Exception as e:
            logger.error(f"Failed to spawn hacker challenge powerups: {e}", exc_info=True)

    def _apply_powerup_effect(self, powerup: PowerUp) -> None:
        """
        Apply the effect of a collected power-up.

        Args:
            powerup: The power-up that was collected
        """
        # Activate timed effects through the power-up manager
        self.powerup_manager.activate(powerup)

        # Security Group was removed - no health system in platformer mode
        # All power-ups are now just timed effects (handled by power-up manager)

    def get_game_map(self) -> Optional[GameMap]:
        """Get the game map instance (None if not in map mode)."""
        return self.game_map if self.use_map else None

    def get_third_parties(self) -> List:
        """Get the list of 3rd party entities from the game map."""
        if self.use_map and self.game_map and hasattr(self.game_map, "third_parties"):
            return self.game_map.third_parties
        return []

    def get_service_nodes(self) -> List[ServiceNode]:
        """Get the list of service nodes for service protection quests."""
        return self.service_nodes

    def get_hacker(self):
        """Get the hacker character (if spawned)."""
        return self.hacker

    def get_active_quest(self):
        """Get the currently active service protection quest."""
        return self.quest_manager.get_active_quest() if self.quest_manager else None

    def _spawn_boss(self) -> None:
        """Spawn a boss - cyber attack themed boss with dialogue, or fallback to wizard boss."""
        if self.boss_spawned:
            return

        self.boss_spawned = True

        # Check if current level has a cyber boss
        current_level = self.game_state.current_level
        self.boss_type = BOSS_LEVEL_MAP.get(current_level)

        if self.boss_type:
            # Cyber boss - show educational dialogue first
            logger.info(f"🕷️  Preparing {self.boss_type.value} boss for level {current_level}")

            # Get dialogue content and show via controller
            dialogue_data = get_boss_dialogue(self.boss_type)
            self.boss_dialogue_controller.show(dialogue_data)

            # Pause game during dialogue
            self.game_state.status = GameStatus.BOSS_BATTLE

            return  # Don't spawn boss yet - wait for dialogue to be dismissed

        # Fallback: Old wizard boss (for levels without cyber boss mapping)
        logger.info(f"🧙 Spawning fallback wizard boss for level {current_level}")

        # Calculate boss spawn position (near player, above screen so he can drop down)
        if self.use_map and self.game_map:
            # Spawn boss above player's current position (in the sky)
            player_x = self.player.position.x
            # Spawn boss slightly ahead of player (to the right)
            boss_x = player_x + 300  # 300px ahead of player

            # Get ground level
            tiles_high = self.game_map.map_height // 16
            ground_height = 8
            ground_y = (tiles_high - ground_height) * 16

            # Start boss high in the sky (will fall down)
            boss_y = 100  # Start high up, will fall to ground
            boss_pos = Vector2(boss_x, boss_y)

            # Set boss ground level for collision
            self.boss_ground_y = ground_y - 80  # Will be set when boss is created
        else:
            # Classic mode - spawn above screen center
            boss_x = self.screen_width // 2
            boss_y = -100  # Start above screen
            boss_pos = Vector2(boss_x, boss_y)
            self.boss_ground_y = self.screen_height // 2

        # Create wizard boss
        self.boss = Boss(boss_pos, "Wizard Boss")

        # Set ground level for boss
        if self.use_map and self.game_map:
            tiles_high = self.game_map.map_height // 16
            ground_height = 8
            ground_y = (tiles_high - ground_height) * 16
            self.boss.ground_y = ground_y - self.boss.height

        # Boss entrance animation state
        self.boss_entrance_timer = 2.0  # 2 seconds of cloud effect
        self.boss_on_cloud = True  # Boss starts on cloud, then lands

        # Transition to boss battle state
        self.game_state.status = GameStatus.BOSS_BATTLE
        logger.info(f"🧙 Wizard Boss spawning at ({boss_pos.x}, {boss_pos.y}) - dropping from sky!")

    def _spawn_cyber_boss(self) -> None:
        """Actually spawn the cyber boss after dialogue is dismissed."""
        if not self.boss_type:
            logger.error("Cannot spawn cyber boss: boss_type not set!")
            return

        # Calculate spawn positions based on boss type
        if self.boss_type == BossType.SCATTERED_SPIDER:
            # Scattered Spider: 5 spiders in a formation
            if self.use_map and self.game_map:
                level_width = self.game_map.map_width
                tiles_high = self.game_map.map_height // 16
                ground_height = 8
                ground_y = (tiles_high - ground_height) * 16
            else:
                level_width = self.screen_width
                ground_y = self.screen_height // 2

            # Create Scattered Spider boss (factory creates spawn positions internally)
            self.boss = create_cyber_boss(self.boss_type, level_width, ground_y)
            logger.info(f"🕷️  Scattered Spider boss spawned with 5 mini-spiders!")

        else:
            # Other cyber bosses (Heartbleed, WannaCry, etc.)
            # Calculate level dimensions and boss spawn position
            if self.use_map and self.game_map:
                # Spawn boss to the right of player's current position
                boss_x = self.player.position.x + 400  # 400px to the right of player
                tiles_high = self.game_map.map_height // 16
                ground_height = 8
                ground_y = (tiles_high - ground_height) * 16
                boss_y = ground_y - 100
            else:
                # Classic mode - spawn in center of screen
                boss_x = self.screen_width // 2
                ground_y = self.screen_height // 2
                boss_y = ground_y - 100

            # Create cyber boss at calculated position
            from cyber_boss import Vector2

            if self.boss_type == BossType.HEARTBLEED:
                boss = HeartbleedBoss(Vector2(boss_x, boss_y))
                boss.ground_y = ground_y
                self.boss = boss
            elif self.boss_type == BossType.WANNACRY:
                boss = WannaCryBoss(Vector2(boss_x, boss_y))
                boss.ground_y = ground_y
                self.boss = boss
            else:
                # Try factory for other types
                level_width = self.screen_width
                self.boss = create_cyber_boss(self.boss_type, level_width, ground_y)

                # Fallback to WannaCry if boss type not implemented
                if self.boss is None:
                    logger.warning(
                        f"⚠️ Boss type {self.boss_type.value} not implemented, falling back to WannaCry"
                    )
                    boss = WannaCryBoss(Vector2(boss_x, boss_y))
                    boss.ground_y = ground_y
                    self.boss = boss

            logger.info(f"🎮 {self.boss_type.value} boss spawned at ({boss_x}, {boss_y})!")

        # Check if boss was actually created (Scattered Spider path)
        if self.boss is None:
            logger.error("❌ Failed to create boss! Returning to playing state.")
            self.game_state.status = GameStatus.PLAYING
            self.boss_spawned = False
            return

        # Boss is active, battle begins
        self.game_state.status = GameStatus.BOSS_BATTLE

    def _check_boss_player_collision(self) -> None:
        """Check if boss is touching player and apply damage."""
        if not self.boss or self.boss.is_defeated:
            return

        # Don't damage if player is invincible
        if self.player.is_invincible:
            return

        player_bounds = self.player.get_bounds()
        player_center_x = self.player.position.x + self.player.width // 2
        player_center_y = self.player.position.y + self.player.height // 2

        # Handle Scattered Spider (swarm of 5 spiders)
        if isinstance(self.boss, ScatteredSpiderBoss):
            for spider in self.boss.get_all_spiders():
                spider_bounds = pygame.Rect(
                    int(spider.position.x),
                    int(spider.position.y),
                    spider.width,
                    spider.height,
                )
                if player_bounds.colliderect(spider_bounds):
                    # Spider touched player - deal damage
                    if self.player.take_damage(1):
                        logger.info(
                            f"🕷️ Player hit by {spider.movement_type} spider! "
                            f"Health: {self.player.current_health}/{self.player.max_health}"
                        )
                    return  # Only take damage from one spider per frame

        # Handle WannaCry special attacks (puddles and sob wave)
        elif isinstance(self.boss, WannaCryBoss):
            # Check direct boss contact
            boss_bounds = self.boss.get_bounds()
            if player_bounds.colliderect(boss_bounds):
                if self.player.take_damage(1):
                    logger.info(
                        f"💧 Player touched by WannaCry! "
                        f"Health: {self.player.current_health}/{self.player.max_health}"
                    )
                return

            # Check puddle damage (tears on ground)
            for puddle in self.boss.puddles:
                puddle_bounds = pygame.Rect(
                    int(puddle["x"] - puddle["radius"]),
                    int(puddle["y"] - 10),
                    int(puddle["radius"] * 2),
                    20,
                )
                if player_bounds.colliderect(puddle_bounds):
                    if self.player.take_damage(1):
                        logger.info(
                            f"💦 Player stepped in tear puddle! "
                            f"Health: {self.player.current_health}/{self.player.max_health}"
                        )
                    return

            # Check sob wave damage (expanding circle attack)
            if self.boss.sob_wave and self.boss.sob_wave.get("active", False):
                wave = self.boss.sob_wave
                wave_center_x = wave["x"]
                wave_center_y = wave["y"]
                wave_radius = wave["radius"]

                # Calculate distance from player center to wave center
                import math

                dist = math.sqrt(
                    (player_center_x - wave_center_x) ** 2 + (player_center_y - wave_center_y) ** 2
                )

                # Player is hit if within the wave ring (outer edge)
                wave_thickness = 30  # Wave is 30 pixels thick
                if wave_radius - wave_thickness <= dist <= wave_radius + wave_thickness:
                    if self.player.take_damage(1):
                        logger.info(
                            f"😭 Player hit by sob wave! "
                            f"Health: {self.player.current_health}/{self.player.max_health}"
                        )
                    return

        # Handle Heartbleed special attacks (bleeding particles)
        elif isinstance(self.boss, HeartbleedBoss):
            # Check direct boss contact
            boss_bounds = self.boss.get_bounds()
            if player_bounds.colliderect(boss_bounds):
                if self.player.take_damage(1):
                    logger.info(
                        f"💔 Player touched by Heartbleed! "
                        f"Health: {self.player.current_health}/{self.player.max_health}"
                    )
                return

            # Check bleeding particle damage
            for particle in self.boss.bleeding_particles:
                particle_bounds = pygame.Rect(
                    int(particle["x"] - 5),
                    int(particle["y"] - 5),
                    10,
                    10,
                )
                if player_bounds.colliderect(particle_bounds):
                    if self.player.take_damage(1):
                        logger.info(
                            f"💉 Player hit by bleeding data! "
                            f"Health: {self.player.current_health}/{self.player.max_health}"
                        )
                    return

        else:
            # Standard boss collision (fallback for other bosses)
            boss_bounds = self.boss.get_bounds()
            if player_bounds.colliderect(boss_bounds):
                # Boss touched player - deal damage
                if self.player.take_damage(1):
                    boss_name = getattr(self.boss, "name", "Boss")
                    logger.info(
                        f"💀 Player hit by {boss_name}! "
                        f"Health: {self.player.current_health}/{self.player.max_health}"
                    )

    def _update_boss_battle(self, delta_time: float) -> None:
        """
        Update game logic during boss battle.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        if not self.boss or self.boss.is_defeated:
            # Boss defeated - transition to victory
            if self.boss and self.boss.is_defeated:
                # Boss defeated - return to lobby
                logger.info("🎉 Boss defeated! Returning to lobby...")

                # STORY MODE: Trigger level completion education before returning
                if self.game_state.is_story_mode:
                    kills = self.education_manager.progress.zombies_eliminated
                    self._trigger_education(
                        TriggerType.LEVEL_COMPLETE,
                        {"zombies_eliminated": str(kills)},
                    )

                self._return_to_lobby(mark_completed=True)
                logger.info("Victory! Boss defeated!")
            return

        # Update player (platformer mode - with gravity)
        self.player.update(delta_time, is_platformer_mode=True)
        self.player.update_invincibility(delta_time)  # Update invincibility timer

        # Debug: Log health when low
        if self.player.current_health <= 3:
            logger.info(
                f"⚠️ LOW HEALTH (Boss): {self.player.current_health}/{self.player.max_health}"
            )

        # Check for game over (player health depleted)
        if self.player.current_health <= 0:
            logger.info(
                f"💀 GAME OVER TRIGGERED (Boss Battle) - Health: {self.player.current_health}"
            )
            self._show_game_over_screen()
            return  # Stop updating game logic

        # Update boss
        if self.boss:
            self.boss.update(delta_time, self.player.position, self.game_map)

        # Check boss-to-player collision (boss damages player)
        if self.boss and not self.boss.is_defeated:
            self._check_boss_player_collision()

        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(delta_time)

            # Remove off-screen projectiles
            if self.use_map and self.game_map:
                if projectile.is_off_screen(
                    self.game_map.map_width, self.game_map.map_height, map_mode=True
                ):
                    self.projectiles.remove(projectile)
            else:
                if projectile.is_off_screen(self.screen_width, self.screen_height, map_mode=False):
                    self.projectiles.remove(projectile)

        # Check projectile collisions with boss
        if self.boss:
            # Handle swarm boss (Scattered Spider) - check collision with each spider
            if isinstance(self.boss, ScatteredSpiderBoss):
                for projectile in self.projectiles[:]:
                    proj_bounds = projectile.get_bounds()
                    hit = False

                    # Check collision with each spider in the swarm
                    for spider in self.boss.get_all_spiders():
                        spider_bounds = pygame.Rect(
                            spider.position.x,
                            spider.position.y,
                            spider.width,
                            spider.height,
                        )
                        if proj_bounds.colliderect(spider_bounds):
                            # Hit a spider
                            spider.health -= projectile.damage
                            hit = True

                            if spider.health <= 0:
                                # Spider defeated
                                self.boss.spiders.remove(spider)
                                logger.info(
                                    f"🕷️  Mini-spider defeated! {len(self.boss.spiders)} remaining"
                                )

                            break  # Projectile can only hit one spider

                    if hit and projectile in self.projectiles:
                        self.projectiles.remove(projectile)

            else:
                # Standard boss collision
                boss_bounds = self.boss.get_bounds()
                for projectile in self.projectiles[:]:
                    proj_bounds = projectile.get_bounds()
                    if proj_bounds.colliderect(boss_bounds):
                        # Hit boss
                        self.projectiles.remove(projectile)
                        defeated = self.boss.take_damage(projectile.damage)
                        if defeated:
                            # Boss defeated
                            logger.info("Boss defeated!")

        # Update camera - follow player, but also show boss if boss is far away
        if self.use_map and self.game_map:
            # During boss battle, camera should show both player and boss
            if self.boss and not self.boss.is_defeated:
                # Center camera between player and boss
                if isinstance(self.boss, ScatteredSpiderBoss):
                    # For swarm boss, use average position of all spiders
                    spiders = self.boss.get_all_spiders()
                    if spiders:
                        avg_spider_x = sum(s.position.x for s in spiders) / len(spiders)
                        center_x = (self.player.position.x + avg_spider_x) / 2
                    else:
                        center_x = self.player.position.x
                else:
                    # Standard boss - use boss position
                    center_x = (self.player.position.x + self.boss.position.x) / 2
                self.game_map.update_camera(center_x, self.player.position.y)
            else:
                self.game_map.update_camera(self.player.position.x, self.player.position.y)

    def _save_game(self) -> None:
        """Save current game state to disk."""
        try:
            # Get current level account number (None if in lobby)
            current_level = None
            if self.game_state.status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
                if self.level_manager:
                    level = self.level_manager.get_current_level()
                    if level:
                        current_level = level.account_id

            # Get completed and unlocked levels
            completed_levels = []
            unlocked_levels = []
            if self.level_manager:
                for level in self.level_manager.levels:
                    if level.is_completed:
                        completed_levels.append(level.account_id)
                    if level.is_unlocked:
                        unlocked_levels.append(level.account_id)

            # Save game state
            self.save_manager.save_game(
                player_score=self.game_state.score,
                player_eliminations=self.game_state.eliminations,
                damage_multiplier=self.game_state.damage_multiplier,
                player_position=self.player.position,
                game_status=self.game_state.status,
                current_level=current_level,
                play_time=self.game_state.play_time,
                completed_levels=completed_levels,
                unlocked_levels=unlocked_levels,
                quarantined_identities=self.quarantined_identities,
                blocked_third_parties=self.blocked_third_parties,
            )

        except Exception as e:
            logger.error(f"Failed to save game: {e}")

    def restore_game_state(self, save_data: dict) -> None:
        """
        Restore game state from saved data.

        Args:
            save_data: Dictionary of saved game state from SaveManager.load_game()
        """
        try:
            # Restore player stats
            player_data = save_data.get("player", {})
            self.game_state.score = player_data.get("score", 0)
            self.game_state.eliminations = player_data.get("eliminations", 0)
            self.game_state.damage_multiplier = player_data.get("damage_multiplier", 1.0)

            # Always spawn at landing zone in lobby - don't restore saved position
            # This prevents spawning inside room boundaries from old saves
            self.player.position = Vector2(self.landing_zone.x, self.landing_zone.y)
            logger.info(
                f"🏛️ Player spawned at landing zone ({self.landing_zone.x}, {self.landing_zone.y})"
            )

            # Restore game state
            game_state_data = save_data.get("game_state", {})
            self.game_state.play_time = game_state_data.get("play_time", 0.0)

            # Restore progress
            progress_data = save_data.get("progress", {})
            completed_levels = progress_data.get("completed_levels", [])
            unlocked_levels = progress_data.get("unlocked_levels", [])

            # Update level manager
            if self.level_manager:
                for level in self.level_manager.levels:
                    if level.account_id in completed_levels:
                        level.is_completed = True
                    if level.account_id in unlocked_levels:
                        level.is_unlocked = True

            # Restore quarantined identities and blocked third parties
            self.quarantined_identities = set(save_data.get("quarantined_identities", []))
            self.blocked_third_parties = set(save_data.get("blocked_third_parties", []))

            logger.info(f"✅ Game state restored:")
            logger.info(f"   Score: {self.game_state.score}")
            logger.info(f"   Eliminations: {self.game_state.eliminations}")
            logger.info(f"   Quarantined identities: {len(self.quarantined_identities)}")
            logger.info(f"   Blocked third parties: {len(self.blocked_third_parties)}")
            logger.info(f"   Completed levels: {len(completed_levels)}")

        except Exception as e:
            logger.error(f"Failed to restore game state: {e}")
