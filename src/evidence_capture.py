"""
Evidence Capture System for Sonrai Zombie Blaster.

Provides screenshot and screen recording capabilities for evidence gathering.
Supports both controller (X/Y buttons) and keyboard (F12/F9) input.

Usage:
    evidence = EvidenceCapture()

    # Screenshot
    filename = evidence.take_screenshot(screen)

    # Recording
    evidence.toggle_recording(current_time)  # Start
    evidence.capture_frame(screen, current_time)  # Each frame
    filename = evidence.toggle_recording(current_time)  # Stop and save
"""

import logging
import math
import os
from datetime import datetime
from typing import List, Optional

import pygame

logger = logging.getLogger(__name__)


class EvidenceCapture:
    """Manages screenshot and recording capture for evidence gathering."""

    # Directories
    EVIDENCE_DIR = ".kiro/evidence"
    SCREENSHOTS_DIR = ".kiro/evidence/screenshots"
    RECORDINGS_DIR = ".kiro/evidence/recordings"

    # Recording settings
    MAX_RECORDING_SECONDS: int = 60
    RECORDING_FPS: int = 30

    # Flash settings
    FLASH_DURATION: float = 0.15  # Seconds

    def __init__(self):
        """Initialize evidence capture system."""
        # State
        self.is_recording: bool = False
        self.recording_start_time: float = 0.0
        self.recording_frames: List[pygame.Surface] = []
        self.last_frame_time: float = 0.0

        # Visual feedback
        self.flash_alpha: int = 0

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create evidence directories if they don't exist."""
        os.makedirs(self.SCREENSHOTS_DIR, exist_ok=True)
        os.makedirs(self.RECORDINGS_DIR, exist_ok=True)

    def _generate_filename(self, extension: str) -> str:
        """Generate filename with timestamp: ZB_YYYYMMDD_HHMMSS.ext"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"ZB_{timestamp}.{extension}"

    # =========================================================================
    # SCREENSHOT
    # =========================================================================

    def take_screenshot(self, screen: pygame.Surface) -> Optional[str]:
        """
        Capture screenshot and save to file.

        Args:
            screen: The pygame surface to capture

        Returns:
            Filename if successful, None if failed
        """
        try:
            filename = self._generate_filename("png")
            filepath = os.path.join(self.SCREENSHOTS_DIR, filename)
            pygame.image.save(screen, filepath)
            self.flash_alpha = 255  # Trigger flash effect
            logger.info(f"📸 Screenshot saved: {filepath}")
            return filename
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {e}")
            return None

    # =========================================================================
    # RECORDING
    # =========================================================================

    def start_recording(self, current_time: float) -> None:
        """Start recording frames."""
        if self.is_recording:
            return
        self.is_recording = True
        self.recording_start_time = current_time
        self.recording_frames = []
        self.last_frame_time = current_time
        logger.info("🔴 Recording started...")

    def stop_recording(self) -> Optional[str]:
        """
        Stop recording and save to file.

        Returns:
            Filename if successful, None if no frames or failed
        """
        if not self.is_recording:
            return None
        self.is_recording = False

        if not self.recording_frames:
            logger.warning("⚠️ No frames captured, recording discarded")
            return None

        return self._save_recording()

    def toggle_recording(self, current_time: float) -> Optional[str]:
        """
        Toggle recording state.

        Args:
            current_time: Current game time

        Returns:
            Filename if recording was stopped and saved, None otherwise
        """
        if self.is_recording:
            return self.stop_recording()
        else:
            self.start_recording(current_time)
            return None

    def capture_frame(self, screen: pygame.Surface, current_time: float) -> None:
        """
        Capture frame if recording and enough time has passed.

        Args:
            screen: The pygame surface to capture
            current_time: Current game time
        """
        if not self.is_recording:
            return

        # Check if max duration reached
        elapsed = current_time - self.recording_start_time
        if elapsed >= self.MAX_RECORDING_SECONDS:
            logger.info(
                f"⏱️ Max recording duration ({self.MAX_RECORDING_SECONDS}s) reached"
            )
            self.stop_recording()
            return

        # Capture at recording FPS (not every frame)
        frame_interval = 1.0 / self.RECORDING_FPS
        if current_time - self.last_frame_time >= frame_interval:
            # Copy the screen surface
            frame = screen.copy()
            self.recording_frames.append(frame)
            self.last_frame_time = current_time

    def _save_recording(self) -> Optional[str]:
        """Save recorded frames as GIF."""
        filename = self._generate_filename("gif")
        filepath = os.path.join(self.RECORDINGS_DIR, filename)

        frame_count = len(self.recording_frames)
        logger.info(f"🎬 Saving {frame_count} frames as GIF...")

        try:
            from PIL import Image

            images = []
            for frame in self.recording_frames:
                # Convert pygame surface to PIL Image
                data = pygame.image.tostring(frame, "RGB")
                size = frame.get_size()
                img = Image.frombytes("RGB", size, data)
                images.append(img)

            if images:
                # Save as animated GIF
                images[0].save(
                    filepath,
                    save_all=True,
                    append_images=images[1:],
                    duration=int(1000 / self.RECORDING_FPS),  # ms per frame
                    loop=0,
                )
                logger.info(f"🎬 Recording saved: {filepath}")

        except ImportError:
            logger.warning("⚠️ Pillow not installed, saving frames as PNGs")
            filename = self._save_frames_as_pngs()

        except Exception as e:
            logger.error(f"❌ Recording save failed: {e}")
            filename = self._save_frames_as_pngs()

        self.recording_frames = []  # Clear memory
        return filename

    def _save_frames_as_pngs(self) -> str:
        """Fallback: save frames as numbered PNGs in a folder."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"ZB_{timestamp}"
        folder_path = os.path.join(self.RECORDINGS_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        for i, frame in enumerate(self.recording_frames):
            filepath = os.path.join(folder_path, f"frame_{i:04d}.png")
            pygame.image.save(frame, filepath)

        logger.info(f"🎬 Frames saved to: {folder_path}/")
        return folder_name + "/"

    # =========================================================================
    # VISUAL FEEDBACK
    # =========================================================================

    def update_flash(self, delta_time: float) -> None:
        """Update screenshot flash effect (fade out)."""
        if self.flash_alpha > 0:
            # Fade out over FLASH_DURATION
            fade_rate = 255 / self.FLASH_DURATION
            self.flash_alpha = max(0, self.flash_alpha - fade_rate * delta_time)

    def get_recording_duration(self, current_time: float) -> float:
        """Get current recording duration in seconds."""
        if not self.is_recording:
            return 0.0
        return current_time - self.recording_start_time

    def render_flash(self, screen: pygame.Surface) -> None:
        """Render white flash overlay when screenshot taken."""
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface(screen.get_size())
            flash_surface.fill((255, 255, 255))
            flash_surface.set_alpha(int(self.flash_alpha))
            screen.blit(flash_surface, (0, 0))

    def render_recording_indicator(
        self, screen: pygame.Surface, current_time: float
    ) -> None:
        """Render red recording dot and timer in top-right corner."""
        if not self.is_recording:
            return

        # Position in top-right corner
        x = screen.get_width() - 120
        y = 25

        # Pulsing red dot
        pulse = (math.sin(current_time * 4) + 1) / 2  # 0 to 1
        red_intensity = int(180 + 75 * pulse)  # 180-255

        # Draw red circle with white border
        pygame.draw.circle(screen, (red_intensity, 0, 0), (x, y), 10)
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 10, 2)

        # Draw "REC" text
        font = pygame.font.Font(None, 28)
        rec_text = font.render("REC", True, (255, 50, 50))
        screen.blit(rec_text, (x + 18, y - 10))

        # Draw timer
        duration = self.get_recording_duration(current_time)
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        timer_text = font.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
        screen.blit(timer_text, (x + 60, y - 10))

        # Draw max duration indicator
        remaining = self.MAX_RECORDING_SECONDS - duration
        if remaining <= 10:
            # Warning when < 10 seconds left
            warn_text = font.render(f"({int(remaining)}s left)", True, (255, 200, 0))
            screen.blit(warn_text, (x - 10, y + 15))
