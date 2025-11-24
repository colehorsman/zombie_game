"""Core game engine and game loop."""

import logging
import time
from typing import List, Optional

import pygame

from models import GameState, GameStatus, Vector2
from player import Player
from zombie import Zombie
from projectile import Projectile
from collision import check_collisions_with_spatial_grid, SpatialGrid
from sonrai_client import SonraiAPIClient
from game_map import GameMap
from level_manager import LevelManager
from difficulty_config import EnvironmentDifficulty, get_difficulty_for_environment
from approval import ApprovalManager
from powerup import PowerUp, PowerUpManager, PowerUpType, spawn_random_powerups
from boss import Boss
from save_manager import SaveManager
from service_protection_quest import (
    ServiceProtectionQuestManager,
    ServiceNode,
    create_bedrock_protection_quest,
    create_service_node,
    SERVICE_ICON_Y
)
from hacker import Hacker


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
        approval_manager: ApprovalManager = None
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
                third_party_data
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

            # LOBBY: Spawn player near entrance (bottom-left area, close to Sandbox door)
            # Sandbox room is typically the first/largest room in top-left
            # Spawn player in bottom-left quadrant for easy access
            self.landing_zone = Vector2(
                self.game_map.map_width // 4,  # Left quarter of map
                self.game_map.map_height * 3 // 4  # Bottom quarter of map
            )
            player_start_pos = self.landing_zone
            logger.info(f"🏛️  Spawning player at LOBBY landing zone ({player_start_pos.x}, {player_start_pos.y})")
            self.player = Player(player_start_pos, self.game_map.map_width, self.game_map.map_height, self.game_map)

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
        self.star_power_touched_zombies = set()  # Track which zombies we've already touched during current Star Power
        self.star_power_was_active = False  # Track when Star Power ends to clear touched set

        # Count 3rd parties
        third_parties_count = 0
        if use_map and self.game_map and hasattr(self.game_map, 'third_parties'):
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
            environment_type=environment_type if level_manager else "lobby"
        )
        
        # Track which level account IDs have been completed
        self.completed_level_account_ids = set()

        # Save/load game state
        self.save_manager = SaveManager()
        self.quarantined_identities = set()  # Track identity IDs that have been quarantined
        self.blocked_third_parties = set()  # Track third-party names that have been blocked
        self.last_autosave_time = 0.0  # Track last autosave for periodic saves
        self.autosave_interval = 30.0  # Autosave every 30 seconds

        # Cheat code system
        self.cheat_enabled = False  # All levels unlocked via cheat
        self.cheat_buffer = []  # Track recent key presses for cheat detection
        self.cheat_codes = {
            'UNLOCK': [pygame.K_u, pygame.K_n, pygame.K_l, pygame.K_o, pygame.K_c, pygame.K_k],  # "UNLOCK"
            'SKIP': [pygame.K_s, pygame.K_k, pygame.K_i, pygame.K_p],  # "SKIP"
        }

        # Timing
        self.start_time = time.time()
        self.running = True

        # Input state
        self.keys_pressed = set()

        # Controller support (8-bit style)
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            logger.info(f"🎮 Controller detected: {self.joystick.get_name()}")
        else:
            logger.info("⌨️  No controller detected, using keyboard")

        # Scrolling (only for classic mode)
        self.scroll_speed = 50.0  # pixels per second
        self.scroll_offset = 0.0

        # Boss battle
        self.boss: Optional[Boss] = None
        self.boss_spawned = False

        # Konami code cheat (up up down down left right left right)
        self.konami_code = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN,
                           pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT]
        self.konami_input = []  # Track current input sequence
        self.konami_timeout = 2.0  # Reset sequence after 2 seconds of no input
        self.last_konami_input_time = 0.0

        # Pause menu (Zelda-style)
        self.pause_menu_options = ["Return to Game", "Return to Lobby", "Save Game", "Quit Game"]
        self.pause_menu_selected_index = 0

        # Service Protection Quests
        self.quest_manager: Optional[ServiceProtectionQuestManager] = None
        self.service_nodes: List[ServiceNode] = []
        self.hacker: Optional[Hacker] = None

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
            logger.info(f"🔍 Checking protection status for Sandbox account {sandbox_level.account_id}...")
            unprotected_services = self.api_client.get_unprotected_services(sandbox_level.account_id)

            if "bedrock-agentcore" in unprotected_services:
                # Service is unprotected - create quest!
                sandbox_quest = create_bedrock_protection_quest(
                    quest_id="sandbox_bedrock_agentcore",
                    level=1,
                    trigger_pos=Vector2(200, 400),
                    service_pos=Vector2(5000, SERVICE_ICON_Y)
                )
                self.quest_manager.add_quest(sandbox_quest)
                logger.info(f"✅ Created Sandbox Bedrock AgentCore quest (service is unprotected)")
            else:
                logger.info(f"⏭️  Skipping Sandbox quest - bedrock-agentcore already protected")

        # Production quest (Level 6) - only create if bedrock-agentcore is unprotected
        production_level = next((l for l in self.level_manager.levels if l.level_number == 6), None)
        if production_level:
            logger.info(f"🔍 Checking protection status for Production account {production_level.account_id}...")
            unprotected_services = self.api_client.get_unprotected_services(production_level.account_id)

            if "bedrock-agentcore" in unprotected_services:
                # Service is unprotected - create quest!
                production_quest = create_bedrock_protection_quest(
                    quest_id="production_bedrock_agentcore",
                    level=6,
                    trigger_pos=Vector2(300, 400),
                    service_pos=Vector2(800, SERVICE_ICON_Y)
                )
                self.quest_manager.add_quest(production_quest)
                logger.info(f"✅ Created Production Bedrock AgentCore quest (service is unprotected)")
            else:
                logger.info(f"⏭️  Skipping Production quest - bedrock-agentcore already protected")

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
                    "Press ENTER to begin the race!"
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
                hacker_dist = self._distance(
                    self.hacker.position,
                    active_quest.service_position
                )
                if hacker_dist < 50:  # Hacker reached icon
                    self._handle_quest_failure(active_quest, "Hacker reached service first!")
                    return

            # Check if player near service (auto-protect within 80px)
            player_dist = self._distance(
                self.player.position,
                active_quest.service_position
            )
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

        # Pause game to show failure message
        self.game_state.status = GameStatus.PAUSED

        # Show mission failed message
        self.game_state.congratulations_message = (
            "❌ Mission Failed: AgentCore Compromised\n\n"
            "The hacker reached Bedrock AgentCore first and created "
            "unauthorized AI agent runtimes with code interpreters!\n\n"
            "Your sensitive data is now being exfiltrated through "
            "gateway targets.\n\n"
            "Press ENTER to continue"
        )

        logger.info(f"❌ QUEST FAILED: {reason}")

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
                service_name=f"{quest.service_type.capitalize()} Service"
            )

            if result.success:
                # Success! Player won the race
                service_node.protected = True
                quest.status = QuestStatus.COMPLETED
                quest.player_won = True
                self.game_state.services_protected += 1

                # Stop hacker
                self.hacker = None

                # Pause game to show success message
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
                    "Press ENTER to continue"
                )

                logger.info(f"✅ PLAYER WON THE RACE! Service protected at x={service_node.position.x}")
                logger.info(f"🎉 Showing success message to player")
            else:
                # API error - show error message but don't fail quest
                error_msg = result.error_message or "Unknown error"
                logger.error(f"Failed to protect service: {error_msg}")
                self.game_state.quest_message = (
                    f"⚠️ Protection Failed\n\n"
                    f"Error: {error_msg}\n\n"
                    "Try again!"
                )
                self.game_state.quest_message_timer = 3.0

        except Exception as e:
            logger.error(f"Exception protecting service: {e}")

    def update(self, delta_time: float) -> None:
        """
        Update game state for one frame.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Periodic autosave (every 30 seconds during gameplay)
        current_time = time.time()
        if current_time - self.last_autosave_time >= self.autosave_interval:
            if self.game_state.status in (GameStatus.LOBBY, GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
                self._save_game()
                self.last_autosave_time = current_time

        # Update play time
        if self.game_state.status == GameStatus.PLAYING:
            self.game_state.play_time = time.time() - self.start_time

        # Update resource message timer (only if not in "always show" mode)
        # Timer of 999.0 means "show while hovering" - don't decrement it
        if self.game_state.resource_message_timer > 0 and self.game_state.resource_message_timer < 999.0:
            self.game_state.resource_message_timer -= delta_time
            if self.game_state.resource_message_timer <= 0:
                self.game_state.resource_message = None

        # Handle different game states
        if self.game_state.status == GameStatus.LOBBY:
            self._update_lobby(delta_time)
        elif self.game_state.status == GameStatus.PLAYING:
            self._update_playing(delta_time)  # LEVEL mode (platformer)
        elif self.game_state.status == GameStatus.BOSS_BATTLE:
            self._update_boss_battle(delta_time)
        elif self.game_state.status == GameStatus.PAUSED:
            # Game is paused, don't update entities
            pass

    def _update_lobby(self, delta_time: float) -> None:
        """
        Update game logic during LOBBY state (top-down navigation).
        
        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        # Update camera to follow player
        if self.use_map and self.game_map:
            self.game_map.update_camera(self.player.position.x, self.player.position.y)
        
        # Update player (top-down movement - no gravity)
        self.player.update(delta_time, is_platformer_mode=False)
        
        # Update zombies (they're visible in lobby but not interactive - just for display)
        # Don't update zombie AI or reveal logic in lobby - they're just decorative
        # Zombies will become interactive when entering a level
        
        # Update third parties (they walk around in lobby)
        if self.game_map and hasattr(self.game_map, 'third_parties'):
            for third_party in self.game_map.third_parties:
                third_party.update(delta_time, self.game_map)
        
        # Check for door collisions
        if self.game_map and hasattr(self.game_map, 'doors'):
            player_bounds = self.player.get_bounds()
            logger.debug(f"Checking {len(self.game_map.doors)} doors for collision with player at ({self.player.position.x}, {self.player.position.y})")
            for door in self.game_map.doors:
                if door.check_collision(player_bounds):
                    logger.info(f"🚪 Door collision! Door at ({door.position.x}, {door.position.y}) → {door.destination_room_name}")
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
                                is_sandbox = level.account_id == "577945324761"  # Sandbox is always unlocked
                                if is_sandbox or self.cheat_enabled:
                                    level_unlocked = True
                                else:
                                    # Check if previous level is complete
                                    level_index = self.level_manager.levels.index(level)
                                    if level_index > 0:
                                        prev_level = self.level_manager.levels[level_index - 1]
                                        if prev_level.account_id in self.completed_level_account_ids:
                                            level_unlocked = True
                                        else:
                                            locked_reason = f"🔒 Level Locked\\n\\nComplete {prev_level.account_name} to unlock\\n{level.account_name}\\n\\nPress ESC to continue"
                                    else:
                                        level_unlocked = True
                                break

                    if level_unlocked:
                        # Player entered an unlocked door - transition to level mode
                        logger.info(f"🚪 Door collision detected! Door name: '{door_name}'")
                        self._enter_level(door)
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
            if (projectile.position.x < 0 or projectile.position.x > self.game_map.map_width or
                projectile.position.y < 0 or projectile.position.y > self.game_map.map_height):
                self.projectiles.remove(projectile)
        
        # Check projectile collisions with third parties
        if self.game_map and hasattr(self.game_map, 'third_parties'):
            for projectile in self.projectiles[:]:
                for third_party in self.game_map.third_parties[:]:
                    if not third_party.is_blocking and not third_party.is_protected:
                        if projectile.get_bounds().colliderect(third_party.get_bounds()):
                            self._block_third_party(third_party)
                            if projectile in self.projectiles:
                                self.projectiles.remove(projectile)
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
                    logger.info(f"✅ Found matching level: {level.account_name} (ID: {level.account_id})")
                    break

            if not current_level:
                logger.warning(f"Could not find level for door: {door_name}")
                logger.warning(f"Available level names: {[l.account_name for l in self.level_manager.levels]}")
                return

            logger.info(f"🚪 Step 3: Setting level index")
            # Set current level in level manager
            self.level_manager.current_level_index = self.level_manager.levels.index(current_level)

            logger.info(f"🚪 Step 4: Loading zombies for account {current_level.account_id}")
            # Load zombies for this level's account
            account_id = current_level.account_id
            level_zombies = [z for z in self.all_zombies if z.account == account_id]
            logger.info(f"Loaded {len(level_zombies)} zombies for level {current_level.level_number}")

            logger.info(f"🚪 Step 5: Loading difficulty config for {current_level.environment_type}")
            # Initialize difficulty for this level's environment
            try:
                self.difficulty = get_difficulty_for_environment(current_level.environment_type)
                logger.info(f"Difficulty for {current_level.environment_type}: {self.difficulty.zombie_hp} HP, {self.difficulty.reveal_radius}px reveal")
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
                    mode="platformer"  # PLATFORMER MODE for levels!
                )
                logger.info(f"✅ GameMap reinitialized as PLATFORMER level successfully")
            except Exception as e:
                logger.error(f"❌ CRASH during GameMap init: {e}", exc_info=True)
                raise

            logger.info(f"🚪 Step 7: Initializing approval manager (if needed)")
            # Initialize approval manager if this environment requires approvals
            if self.difficulty and self.difficulty.uses_approval_system:
                try:
                    self.approval_manager = ApprovalManager(approvals_needed=self.difficulty.approvals_needed)
                    logger.info(f"Approval system active: {self.difficulty.approvals_needed} approvals needed")
                except Exception as e:
                    logger.error(f"Failed to initialize approval manager: {e}", exc_info=True)
                    self.approval_manager = None
            else:
                self.approval_manager = None

            logger.info(f"🚪 Step 8: Creating player at platformer start position")
            # Spawn player at start of platformer level
            player_start_pos = Vector2(100, 100)  # Left side, will fall to ground
            try:
                self.player = Player(player_start_pos, self.game_map.map_width, self.game_map.map_height, self.game_map)
                logger.info(f"✅ Player created successfully")
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
                            service_node = create_service_node("bedrock-agentcore", Vector2(5000, SERVICE_ICON_Y))
                            self.service_nodes = [service_node]
                            logger.info(f"✅ Created Bedrock AgentCore service node for Sandbox (quest active)")
                        elif current_level.level_number == 6:
                            # Production Bedrock AgentCore service at x=800
                            service_node = create_service_node("bedrock-agentcore", Vector2(800, SERVICE_ICON_Y))
                            self.service_nodes = [service_node]
                            logger.info(f"✅ Created Bedrock AgentCore service node for Production (quest active)")
                    else:
                        logger.info(f"⏭️  No quest for level {current_level.level_number} - service already protected")
            except Exception as e:
                logger.error(f"⚠️  Service node creation failed: {e}", exc_info=True)
                self.service_nodes = []

            logger.info(f"🚪 === ENTERED LEVEL {current_level.level_number}: {current_level.account_name} - SUCCESS ===")
        except Exception as e:
            logger.error(f"❌ ❌ ❌ CRASH in _enter_level: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            # Don't crash - just log and return to lobby
            self.game_state.error_message = f"Failed to enter level: {str(e)}"

    def _return_to_lobby(self) -> None:
        """
        Transition from level back to lobby mode.
        """
        logger.info("🏛️  Returning to lobby...")
        
        # Mark current level as completed
        completed_account_id = self.game_state.current_level_account_id
        if completed_account_id:
            self.completed_level_account_ids.add(completed_account_id)
            self.game_state.completed_levels.add(completed_account_id)
        
        # Reinitialize game map for lobby (main branch style)
        self.game_map = GameMap(
            "assets/reinvent_floorplan.png",
            self.screen_width,
            self.screen_height,
            self.account_data,
            self.third_party_data
        )
        
        # Mark doors as completed based on completed levels
        if self.game_map and hasattr(self.game_map, 'doors') and self.level_manager:
            for door in self.game_map.doors:
                # Find the level that matches this door
                if door.destination_room_name:
                    for level in self.level_manager.levels:
                        if level.account_name == door.destination_room_name:
                            # Check if this level's account ID is completed
                            if level.account_id in self.completed_level_account_ids:
                                door.is_completed = True
                                logger.info(f"✅ Door to {door.destination_room_name} marked as completed")
                            break
        
        # Spawn player at landing zone
        self.player = Player(self.landing_zone, self.game_map.map_width, self.game_map.map_height, self.game_map)
        
        # Clear level-specific entities
        self.zombies = []  # No zombies in lobby
        self.projectiles = []
        self.powerups = []
        self.boss = None
        self.boss_spawned = False

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
        
        # Update game state
        self.game_state.status = GameStatus.LOBBY
        self.game_state.zombies_remaining = 0
        self.game_state.total_zombies = 0
        self.game_state.current_level_account_id = None
        
        logger.info("✅ Returned to lobby")

    def _update_playing(self, delta_time: float) -> None:
        """
        Update game logic during PLAYING state.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
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

        # Update scrolling (classic mode only)
        if not self.use_map:
            self.scroll_offset += self.scroll_speed * delta_time

        # Update player (platformer mode - with gravity)
        self.player.update(delta_time, is_platformer_mode=True)

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
                            logger.info(f"⭐ STAR POWER: Touching {zombie.identity_name} - instant quarantine!")
                            self.star_power_touched_zombies.add(zombie)
                            self._handle_zombie_elimination(zombie)  # Instant elimination
                        continue  # Don't push player back, zombie is eliminated

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
                logger.info(f"Collected approval form! ({self.approval_manager.approvals_collected}/{self.approval_manager.approvals_needed})")

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
        if self.use_map and self.game_map and hasattr(self.game_map, 'resource_nodes'):
            for resource in self.game_map.resource_nodes:
                # Get resource bounds (centered on position, extends upward from ground)
                resource_size = resource.get('size', 48)
                resource_pos = resource.get('position')
                resource_x = resource_pos.x
                resource_y = resource_pos.y - resource_size  # Icon extends upward
                resource_bounds = pygame.Rect(int(resource_x), int(resource_y), resource_size, resource_size)

                # Check if player is touching or jumping on the resource
                if player_bounds.colliderect(resource_bounds):
                    resource_collision_found = True
                    # Get resource info
                    resource_type = resource.get('type', 'Unknown')
                    protection_status = resource.get('protection_status', 'unprotected')
                    data_class = resource.get('data_class', None)

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
                    self.game_state.resource_message_timer = 999.0  # Large value to keep it visible while hovering
                    break  # Only show one resource message at a time

        # If not colliding with any resource, clear the message immediately
        if not resource_collision_found:
            self.game_state.resource_message = None
            self.game_state.resource_message_timer = 0.0

        # Map mode: update camera and reveal nearby zombies
        if self.use_map and self.game_map:
            self.game_map.update_camera(self.player.position.x, self.player.position.y)
            self.game_map.reveal_nearby_zombies(self.player.position, self.zombies)

        # Update zombies with AI (only if not in boss battle)
        if self.game_state.status != GameStatus.BOSS_BATTLE:
            for zombie in self.zombies:
                zombie.update(delta_time, player_pos=self.player.position, game_map=self.game_map)

        # Update 3rd parties
        third_parties = self.get_third_parties()
        for third_party in third_parties:
            third_party.update(delta_time, self.game_map)

        # Update service protection quests
        self._update_quests(delta_time)

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
                if projectile.is_off_screen(self.game_map.map_width, self.game_map.map_height, map_mode=True):
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
                    z for z in self.zombies
                    if not z.is_hidden and self.game_map.is_on_screen(z.position.x, z.position.y, z.width, z.height)
                ]
            else:
                visible_zombies = self.zombies

            collisions = check_collisions_with_spatial_grid(
                self.projectiles,
                visible_zombies,
                self.spatial_grid
            )
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
                    tp for tp in third_parties
                    if not tp.is_hidden and self.game_map.is_on_screen(tp.position.x, tp.position.y, tp.width, tp.height)
                ]
            else:
                visible_third_parties = third_parties

            third_party_collisions = check_collisions_with_spatial_grid(
                self.projectiles,
                visible_third_parties,
                self.spatial_grid
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
        # Check if production environment requires approvals
        if self.difficulty and self.difficulty.uses_approval_system:
            if not self.approval_manager or not self.approval_manager.has_enough_approvals():
                # Not enough approvals - show warning message
                approvals_remaining = self.approval_manager.get_approvals_remaining() if self.approval_manager else self.difficulty.approvals_needed
                logger.warning(f"Cannot quarantine - need {approvals_remaining} more approval(s)")
                # Don't mark zombie for quarantine
                return

        # IMMEDIATE FEEDBACK: Hide zombie right away (no lag)
        zombie.is_hidden = True
        zombie.mark_for_quarantine()

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

        # Block immediately via API (no pause, no delay)
        self._block_third_party(third_party)

    def _show_pause_menu(self) -> None:
        """Show Zelda-style pause menu with options."""
        # Reset menu selection to first option
        self.pause_menu_selected_index = 0

        # Build pause menu message
        pause_message = self._build_pause_menu_message()

        # Set pause state
        self.game_state.congratulations_message = pause_message
        self.game_state.previous_status = self.game_state.status
        self.game_state.status = GameStatus.PAUSED
        logger.info("⏸️  Game paused - showing menu")

    def _build_pause_menu_message(self) -> str:
        """Build the pause menu message with current selection highlighted."""
        menu_message = "⏸️  PAUSED\\n\\n"

        for i, option in enumerate(self.pause_menu_options):
            if i == self.pause_menu_selected_index:
                # Highlight selected option with arrow
                menu_message += f"▶ {option}\\n"
            else:
                # Unselected option
                menu_message += f"  {option}\\n"

        menu_message += "\\nUse ↑↓ to select, ENTER to confirm"
        return menu_message

    def _navigate_pause_menu(self, direction: int) -> None:
        """
        Navigate the pause menu up or down.

        Args:
            direction: -1 for up, 1 for down
        """
        self.pause_menu_selected_index = (self.pause_menu_selected_index + direction) % len(self.pause_menu_options)
        # Update the menu display
        self.game_state.congratulations_message = self._build_pause_menu_message()
        logger.debug(f"Menu selection: {self.pause_menu_options[self.pause_menu_selected_index]}")

    def _execute_pause_menu_option(self) -> None:
        """Execute the currently selected pause menu option."""
        selected_option = self.pause_menu_options[self.pause_menu_selected_index]
        logger.info(f"Executing menu option: {selected_option}")

        if selected_option == "Return to Game":
            # Resume the game
            self.dismiss_message()
        elif selected_option == "Return to Lobby":
            # Return to lobby (only if in a level)
            if self.game_state.previous_status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
                self.game_state.congratulations_message = None
                self.game_state.status = self.game_state.previous_status
                self._return_to_lobby()
            else:
                # Already in lobby, just resume
                self.dismiss_message()
        elif selected_option == "Save Game":
            # Save the game
            self._save_game()
            # Show brief confirmation in the menu
            logger.info("✅ Game saved from pause menu")
            # Rebuild menu with save confirmation
            menu_message = "⏸️  PAUSED\\n\\n"
            menu_message += "✅ Game Saved!\\n\\n"
            for i, option in enumerate(self.pause_menu_options):
                if i == self.pause_menu_selected_index:
                    menu_message += f"▶ {option}\\n"
                else:
                    menu_message += f"  {option}\\n"
            menu_message += "\\nUse ↑↓ to select, ENTER to confirm"
            self.game_state.congratulations_message = menu_message
        elif selected_option == "Quit Game":
            # Save and quit
            logger.info("Saving game before quit...")
            self._save_game()
            self.running = False

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

    def _quarantine_zombie(self, zombie: Zombie) -> None:
        """
        Quarantine a zombie via the API.

        Args:
            zombie: The zombie to quarantine
        """
        try:
            # Extract root scope from full scope path
            # e.g., "aws/r-ui1v/ou-ui1v-abc123/577945324761" -> "aws/r-ui1v"
            root_scope = None
            if zombie.scope:
                scope_parts = zombie.scope.split("/")
                if len(scope_parts) >= 2:
                    root_scope = f"{scope_parts[0]}/{scope_parts[1]}"

            result = self.api_client.quarantine_identity(
                identity_id=zombie.identity_id,
                identity_name=zombie.identity_name,
                account=zombie.account,
                scope=zombie.scope,  # Use zombie's scope from API
                root_scope=root_scope  # Extract root from full scope
            )

            if result.success:
                # Successfully quarantined - remove zombie permanently
                if zombie in self.zombies:
                    self.zombies.remove(zombie)
                    self.game_state.zombies_remaining -= 1
                    self.game_state.zombies_quarantined += 1

                    # Track quarantined identity for save/load
                    self.quarantined_identities.add(zombie.identity_id)

                    logger.info(f"Successfully quarantined {zombie.identity_name}")

                    # Save game state after successful quarantine
                    self._save_game()

                    # Check for boss spawn (all zombies cleared)
                    if self.game_state.zombies_remaining == 0 and not self.boss_spawned:
                        self._spawn_boss()
                        logger.info("All zombies cleared! Spawning boss...")
            else:
                # Quarantine failed - restore zombie
                zombie.is_quarantining = False
                self.game_state.error_message = f"Failed to quarantine {zombie.identity_name}"
                logger.error(f"Quarantine failed: {result.error_message}")

        except Exception as e:
            # Error during quarantine - restore zombie
            zombie.is_quarantining = False
            self.game_state.error_message = f"Error: {str(e)}"
            logger.error(f"Exception during quarantine: {e}")

    def _block_third_party(self, third_party) -> None:
        """
        Block a 3rd party via the API.

        Args:
            third_party: The 3rd party to block
        """
        try:
            result = self.api_client.block_third_party(
                third_party_id=third_party.third_party_id,
                third_party_name=third_party.name
            )

            if result.success:
                # Successfully blocked - remove 3rd party permanently
                third_parties = self.get_third_parties()
                if third_party in third_parties:
                    third_parties.remove(third_party)
                    self.game_state.third_parties_blocked += 1

                    # Track blocked third party for save/load
                    self.blocked_third_parties.add(third_party.name)

                    logger.info(f"Successfully blocked 3rd party {third_party.name}")

                    # Save game state after successful block
                    self._save_game()
            else:
                # Block failed - restore 3rd party
                third_party.is_blocking = False
                self.game_state.error_message = f"Failed to block {third_party.name}"
                logger.error(f"Block failed: {result.error_message}")

        except Exception as e:
            # Error during block - restore 3rd party
            third_party.is_blocking = False
            self.game_state.error_message = f"Error: {str(e)}"
            logger.error(f"Exception during block: {e}")

    def handle_input(self, events: List[pygame.event.Event]) -> None:
        """
        Handle input events (keyboard and 8-bit controller).

        Args:
            events: List of Pygame events
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)

                # Handle pause menu navigation (if paused with menu active)
                if self.game_state.status == GameStatus.PAUSED:
                    # Check if we're showing the actual pause menu (not a different message)
                    if self.game_state.congratulations_message and "PAUSED" in self.game_state.congratulations_message:
                        # UP arrow - move selection up
                        if event.key == pygame.K_UP:
                            self._navigate_pause_menu(-1)
                            continue
                        # DOWN arrow - move selection down
                        elif event.key == pygame.K_DOWN:
                            self._navigate_pause_menu(1)
                            continue
                        # ENTER - execute selected option
                        elif event.key == pygame.K_RETURN:
                            self._execute_pause_menu_option()
                            continue
                        # ESC - cancel and return to game
                        elif event.key == pygame.K_ESCAPE:
                            self.dismiss_message()
                            continue

                # Konami code detection (up up down down left right left right)
                current_time = time.time()
                if current_time - self.last_konami_input_time > self.konami_timeout:
                    # Reset sequence if too much time passed
                    self.konami_input = []
                
                self.last_konami_input_time = current_time
                self.konami_input.append(event.key)
                
                # Keep only last 8 inputs
                if len(self.konami_input) > 8:
                    self.konami_input = self.konami_input[-8:]

                # Check for admin cheat codes (UNLOCK, SKIP)
                self.cheat_buffer.append(event.key)
                if len(self.cheat_buffer) > 6:  # Max cheat code length
                    self.cheat_buffer = self.cheat_buffer[-6:]

                # Check UNLOCK cheat (unlocks all levels)
                if self.cheat_buffer == self.cheat_codes['UNLOCK']:
                    self.cheat_enabled = True
                    self.game_state.congratulations_message = "🔓 CHEAT ACTIVATED\\n\\nAll Levels Unlocked!\\n\\nPress ESC to continue"
                    # Save current status before pausing
                    self.game_state.previous_status = self.game_state.status
                    self.game_state.status = GameStatus.PAUSED
                    logger.info("🔓 CHEAT: All levels unlocked!")
                    self.cheat_buffer = []

                # Check SKIP cheat (skip current level)
                if self.cheat_buffer == self.cheat_codes['SKIP']:
                    if self.game_state.status == GameStatus.PLAYING and self.level_manager:
                        # Mark current level as complete and return to lobby
                        current_level = self.level_manager.levels[self.level_manager.current_level_index]
                        self.completed_level_account_ids.add(current_level.account_id)
                        logger.info(f"🔓 CHEAT: Skipping level {current_level.account_name}")
                        self._return_to_lobby()
                    self.cheat_buffer = []

                # Check if Konami code matches
                if len(self.konami_input) >= 8:
                    if self.konami_input[-8:] == self.konami_code:
                        logger.info("🎮 KONAMI CODE ACTIVATED! Spawning boss...")
                        self._spawn_boss()
                        self.konami_input = []  # Reset

                # Handle message dismissal
                if event.key == pygame.K_RETURN:
                    # Check for quest dialog dismissal and hacker spawn
                    if self.quest_manager and self.game_state.quest_message:
                        from models import QuestStatus
                        active_quest = self.quest_manager.get_quest_for_level(self.game_state.current_level)
                        if active_quest and active_quest.status == QuestStatus.TRIGGERED:
                            # Dismiss quest dialog
                            self.game_state.quest_message = None

                            # Spawn hacker ON GROUND near player for side-by-side race!
                            # Both start from ~same position, both run toward service
                            # Player: 4800px @ 120px/s = 40s, Hacker: 4800px @ 130px/s = 37s
                            # Very close 3-second race - player can win!
                            spawn_x = self.player.position.x - 50  # Slightly behind player
                            spawn_y = 832 - 32  # On the ground (ground_y - hacker_height)
                            self.hacker = Hacker(
                                spawn_position=Vector2(spawn_x, spawn_y),
                                target_position=active_quest.service_position
                            )

                            # Start the race!
                            active_quest.status = QuestStatus.ACTIVE
                            active_quest.hacker_spawned = True

                            logger.info(f"🎮 RACE STARTED! Hacker spawned at ({spawn_x}, {spawn_y})")
                            logger.info(f"🎮 Hacker object created: {self.hacker is not None}")
                            logger.info(f"🎮 Hacker position: {self.hacker.position if self.hacker else 'None'}")
                            continue

                    if self.game_state.status == GameStatus.PAUSED:
                        self.dismiss_message()

                # PLATFORMER CONTROLS: Jump with UP or W (only in level mode, not lobby)
                if event.key in (pygame.K_UP, pygame.K_w):
                    if self.game_state.status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
                        self.player.jump()
                    # In LOBBY mode, UP/W is handled by continuous movement for top-down navigation

                # Handle firing (works in lobby, playing, and boss battle)
                if event.key == pygame.K_SPACE:
                    if self.game_state.status in (GameStatus.LOBBY, GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
                        projectile = self.player.fire_projectile()
                        self.projectiles.append(projectile)

                # ESC key - Pause/Resume or Quit
                if event.key == pygame.K_ESCAPE:
                    if self.game_state.status == GameStatus.PAUSED:
                        # Resume game
                        self.dismiss_message()
                    elif self.game_state.status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
                        # Show pause menu
                        self._show_pause_menu()
                    else:
                        # In lobby - quit game
                        logger.info("Saving game before exit...")
                        self._save_game()
                        self.running = False

                # L key - Return to lobby (from levels only)
                elif event.key == pygame.K_l:
                    if self.game_state.status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
                        logger.info("🏠 L key pressed - returning to lobby")
                        self._return_to_lobby()

            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)

            # Controller button events
            elif event.type == pygame.JOYBUTTONDOWN:
                if self.joystick:
                    # Handle pause menu navigation with controller
                    if self.game_state.status == GameStatus.PAUSED:
                        if self.game_state.congratulations_message and "PAUSED" in self.game_state.congratulations_message:
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

                    # A button (0) - Fire (works in all modes)
                    if event.button == 0:
                        if self.game_state.status in (GameStatus.LOBBY, GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
                            projectile = self.player.fire_projectile()
                            self.projectiles.append(projectile)
                    # B button (1) - Jump (only in level mode)
                    elif event.button == 1:
                        if self.game_state.status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
                            self.player.jump()
                    # Start button (7) - Pause menu / Dismiss messages
                    elif event.button == 7:
                        if self.game_state.status == GameStatus.PAUSED:
                            self.dismiss_message()
                        elif self.game_state.status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
                            # Toggle pause menu
                            self._show_pause_menu()
                    # Star/Home button (10) - Return to lobby (only in levels)
                    elif event.button == 10:
                        if self.game_state.status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
                            logger.info("⭐ Star button pressed - returning to lobby")
                            self._return_to_lobby()

        # Handle continuous movement
        # LOBBY MODE: Top-down movement (4-directional)
        if self.game_state.status == GameStatus.LOBBY:
            # Check keyboard input
            keyboard_left = pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed
            keyboard_right = pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed
            keyboard_up = pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed
            keyboard_down = pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed

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
                    if hat[1] < 0:
                        controller_up = True  # Hat Y-axis: negative = UP
                    elif hat[1] > 0:
                        controller_down = True  # Hat Y-axis: positive = DOWN

                # Left analog stick (axis 0 and 1) - backup
                if self.joystick.get_numaxes() > 1:
                    axis_x = self.joystick.get_axis(0)
                    axis_y = self.joystick.get_axis(1)
                    if axis_x < -0.3:  # Deadzone
                        controller_left = True
                    elif axis_x > 0.3:
                        controller_right = True
                    if axis_y < -0.3:
                        controller_up = True  # Stick Y-axis: negative = UP
                    elif axis_y > 0.3:
                        controller_down = True  # Stick Y-axis: positive = DOWN

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
                logger.info(f"UP pressed in lobby, velocity.y = {self.player.velocity.y}, position.y = {self.player.position.y}")
            elif keyboard_down or controller_down:
                self.player.move_down()
                logger.info(f"DOWN pressed in lobby, velocity.y = {self.player.velocity.y}, position.y = {self.player.position.y}")
            else:
                self.player.stop_vertical()
        
        # LEVEL MODE: Platformer movement (left/right + jump)
        elif self.game_state.status in (GameStatus.PLAYING, GameStatus.BOSS_BATTLE):
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

            logger.info(f"Distributed {len(self.zombies)} zombies. First zombie at ({self.zombies[0].position.x}, {self.zombies[0].position.y})")

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
        if not hasattr(self.game_map, 'platform_positions'):
            logger.error("GameMap missing platform_positions attribute - powerups skipped")
            return

        # Validation 4: Check platform positions is not None or empty
        if not self.game_map.platform_positions:
            logger.warning("No platforms available for power-up placement (empty list)")
            return

        # Validation 5: Verify we're in platformer mode (not lobby)
        if hasattr(self.game_map, 'mode') and self.game_map.mode != "platformer":
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
                selected_platforms.extend(random.sample(early_platforms, min(num_early, len(early_platforms))))
            if later_platforms and num_later > 0:
                selected_platforms.extend(random.sample(later_platforms, min(num_later, len(later_platforms))))

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
            logger.info(f"✨ Spawned {len(self.powerups)} power-ups ON platforms ({star_count} stars)")

        except Exception as e:
            logger.error(f"Failed to spawn powerups: {e}", exc_info=True)
            self.powerups = []  # Ensure powerups list exists even on failure

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
        if self.use_map and self.game_map and hasattr(self.game_map, 'third_parties'):
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
        """Spawn the wizard boss - drops from sky with clouds."""
        if self.boss_spawned:
            return

        self.boss_spawned = True

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
                self._return_to_lobby()
                logger.info("Victory! Boss defeated!")
            return

        # Update player (platformer mode - with gravity)
        self.player.update(delta_time, is_platformer_mode=True)

        # Update boss
        if self.boss:
            self.boss.update(delta_time, self.player.position, self.game_map)

        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(delta_time)

            # Remove off-screen projectiles
            if self.use_map and self.game_map:
                if projectile.is_off_screen(self.game_map.map_width, self.game_map.map_height, map_mode=True):
                    self.projectiles.remove(projectile)
            else:
                if projectile.is_off_screen(self.screen_width, self.screen_height, map_mode=False):
                    self.projectiles.remove(projectile)

        # Check projectile collisions with boss
        if self.boss:
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
                blocked_third_parties=self.blocked_third_parties
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

            # Restore player position
            position_data = player_data.get("position", {})
            if position_data:
                self.player.position = Vector2(
                    position_data.get("x", self.landing_zone.x),
                    position_data.get("y", self.landing_zone.y)
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
