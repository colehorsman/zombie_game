"""
Photo Booth Controller.

Manages the photo booth capture flow including consent,
webcam capture, and composite generation.
"""

import logging
import time
from enum import Enum
from typing import Optional

import pygame
from PIL import Image

from .compositor import PhotoBoothCompositor
from .config import PhotoBoothConfig

# Try to import OpenCV, but don't fail if not available
try:
    import cv2

    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("OpenCV not available - webcam capture disabled")


class PhotoBoothState(Enum):
    """Photo booth state machine states."""

    DISABLED = "disabled"
    INACTIVE = "inactive"
    AWAITING_CONSENT = "awaiting_consent"
    CONSENT_GIVEN = "consent_given"
    CONSENT_DECLINED = "consent_declined"
    CAPTURING = "capturing"
    COMPOSITING = "compositing"
    COMPLETE = "complete"
    ERROR = "error"


class PhotoBoothController:
    """
    Manages photo booth capture and compositing.

    Lifecycle:
        1. __init__(config) - Create controller
        2. initialize() - Setup webcam (call once)
        3. show_consent_prompt() - Start consent flow
        4. handle_consent_input() - Process user choice
        5. capture_selfie() - Capture webcam (if opted in)
        6. capture_gameplay() - Capture game screen
        7. generate_composite() - Create final image
        8. cleanup() - Release resources
    """

    def __init__(self, config: Optional[PhotoBoothConfig] = None):
        """
        Initialize photo booth controller.

        Args:
            config: Configuration (loads from env if None)
        """
        self.config = config or PhotoBoothConfig.from_env()
        self._state = (
            PhotoBoothState.DISABLED if not self.config.enabled else PhotoBoothState.INACTIVE
        )
        self._selfie_opted_in = False
        self._webcam = None
        self._camera_available = False

        # Captured images
        self._selfie_image: Optional[Image.Image] = None
        self._gameplay_image: Optional[Image.Image] = None
        self._composite_path: Optional[str] = None

        # Timing
        self._consent_prompt_start: float = 0.0
        self._arcade_start_time: float = 0.0
        self._gameplay_captured: bool = False
        self._selfie_captured: bool = False

        # Compositor
        self._compositor = PhotoBoothCompositor()

        self._logger = logging.getLogger(__name__)

    @property
    def state(self) -> PhotoBoothState:
        """Current state of the photo booth."""
        return self._state

    @property
    def selfie_opted_in(self) -> bool:
        """Whether player opted in to selfie."""
        return self._selfie_opted_in

    @property
    def is_camera_available(self) -> bool:
        """Whether webcam is available."""
        return self._camera_available

    @property
    def composite_path(self) -> Optional[str]:
        """Path to generated composite image."""
        return self._composite_path

    @property
    def consent_time_remaining(self) -> float:
        """Seconds remaining in consent prompt."""
        if self._state != PhotoBoothState.AWAITING_CONSENT:
            return 0.0
        elapsed = time.time() - self._consent_prompt_start
        remaining = self.config.consent_timeout - elapsed
        return max(0.0, remaining)

    def initialize(self) -> bool:
        """
        Initialize webcam and resources.

        Returns:
            True if initialization successful (webcam is optional)
        """
        self._logger.info(f"📸 initialize() called, config.enabled={self.config.enabled}")

        if not self.config.enabled:
            self._state = PhotoBoothState.DISABLED
            self._logger.info("📸 Photo booth disabled by config")
            return True

        self._state = PhotoBoothState.INACTIVE

        # Try to initialize webcam
        if CV2_AVAILABLE:
            try:
                self._logger.info(f"📸 Opening webcam at index {self.config.camera_index}")
                self._webcam = cv2.VideoCapture(self.config.camera_index)
                if self._webcam.isOpened():
                    self._camera_available = True
                    self._logger.info(
                        f"📸 Webcam initialized successfully (index {self.config.camera_index})"
                    )
                    # Test read to ensure camera is really working
                    ret, _ = self._webcam.read()
                    if ret:
                        self._logger.info("📸 Webcam test read successful")
                    else:
                        self._logger.warning("📸 Webcam opened but test read failed")
                else:
                    self._webcam.release()
                    self._webcam = None
                    self._camera_available = False
                    self._logger.warning("📸 Webcam not available - selfie capture disabled")
            except Exception as e:
                self._logger.error(f"📸 Failed to initialize webcam: {e}", exc_info=True)
                self._webcam = None
                self._camera_available = False
        else:
            self._camera_available = False
            self._logger.info("📸 OpenCV not installed - selfie capture disabled")

        self._logger.info(
            f"📸 initialize() complete: camera_available={self._camera_available}, "
            f"webcam={self._webcam is not None}, state={self._state}"
        )
        return True

    def cleanup(self) -> None:
        """Release all resources."""
        if self._webcam is not None:
            try:
                self._webcam.release()
            except Exception:
                pass
            self._webcam = None

        self._camera_available = False
        self._selfie_image = None
        self._gameplay_image = None
        self._state = PhotoBoothState.DISABLED
        self._logger.info("Photo booth resources cleaned up")

    def show_consent_prompt(self) -> None:
        """Begin consent prompt flow."""
        if self._state == PhotoBoothState.DISABLED:
            return

        self._state = PhotoBoothState.AWAITING_CONSENT
        self._consent_prompt_start = time.time()
        self._selfie_opted_in = False
        self._logger.info("Showing photo booth consent prompt")

    def handle_consent_input(self, opted_in: bool) -> None:
        """
        Process user's consent decision.

        Args:
            opted_in: True if user wants selfie, False otherwise
        """
        self._logger.info(
            f"📸 handle_consent_input called: opted_in={opted_in}, "
            f"current_state={self._state}, camera_available={self._camera_available}, "
            f"webcam={self._webcam is not None}"
        )

        if self._state != PhotoBoothState.AWAITING_CONSENT:
            self._logger.warning(
                f"📸 Ignoring consent input - not in AWAITING_CONSENT state (current: {self._state})"
            )
            return

        self._selfie_opted_in = opted_in and self._camera_available
        self._state = (
            PhotoBoothState.CONSENT_GIVEN if opted_in else PhotoBoothState.CONSENT_DECLINED
        )

        self._logger.info(
            f"📸 Consent processed: selfie_opted_in={self._selfie_opted_in}, new_state={self._state}"
        )

        if opted_in and not self._camera_available:
            self._logger.warning("📸 User opted in but camera not available - selfie disabled")
        elif opted_in:
            self._logger.info("📸 User opted IN to selfie - will capture during gameplay")

    def check_consent_timeout(self) -> bool:
        """
        Check if consent prompt has timed out.

        Returns:
            True if timeout exceeded (auto-decline triggered)
        """
        if self._state != PhotoBoothState.AWAITING_CONSENT:
            return False

        if self.consent_time_remaining <= 0:
            self._logger.info("Consent prompt timed out - defaulting to no selfie")
            self.handle_consent_input(opted_in=False)
            return True

        return False

    def is_consent_complete(self) -> bool:
        """Check if consent flow is complete (user made a choice, regardless of current capture state)."""
        # Include all states that come AFTER consent was given/declined
        # This ensures we can still generate composite even after capturing
        return self._state in (
            PhotoBoothState.CONSENT_GIVEN,
            PhotoBoothState.CONSENT_DECLINED,
            PhotoBoothState.CAPTURING,
            PhotoBoothState.COMPOSITING,
            PhotoBoothState.COMPLETE,
        )

    def capture_selfie(self) -> bool:
        """
        Capture webcam image.

        Returns:
            True if capture successful or not opted in
            False if capture failed
        """
        self._logger.info(
            f"📸 capture_selfie called: opted_in={self._selfie_opted_in}, "
            f"camera_available={self._camera_available}, webcam={self._webcam is not None}"
        )

        if not self._selfie_opted_in:
            self._logger.info("📸 capture_selfie: skipping - not opted in")
            return True  # Not an error, just skipped

        if not self._camera_available or self._webcam is None:
            self._logger.warning(
                f"📸 Cannot capture selfie - camera_available={self._camera_available}, "
                f"webcam={self._webcam is not None}"
            )
            return False

        # Verify webcam is still open
        if not self._webcam.isOpened():
            self._logger.error("📸 Webcam was closed unexpectedly! Attempting to reopen...")
            try:
                self._webcam = cv2.VideoCapture(self.config.camera_index)
                if not self._webcam.isOpened():
                    self._logger.error("📸 Failed to reopen webcam")
                    return False
                self._logger.info("📸 Successfully reopened webcam")
            except Exception as e:
                self._logger.error(f"📸 Failed to reopen webcam: {e}")
                return False

        self._state = PhotoBoothState.CAPTURING

        try:
            # Read frame from webcam
            self._logger.info("📸 Reading frame from webcam...")
            ret, frame = self._webcam.read()

            if not ret or frame is None:
                self._logger.error(
                    f"📸 Failed to read from webcam: ret={ret}, frame={frame is not None}"
                )
                return False

            # Convert BGR (OpenCV) to RGB (PIL)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self._selfie_image = Image.fromarray(frame_rgb)
            self._selfie_captured = True

            self._logger.info(f"📸 Selfie captured successfully: {self._selfie_image.size}")
            return True

        except Exception as e:
            self._logger.error(f"📸 Webcam capture error: {e}", exc_info=True)
            return False

    def capture_gameplay(self, screen: pygame.Surface) -> bool:
        """
        Capture current gameplay screen.

        Args:
            screen: Pygame surface to capture

        Returns:
            True if capture successful
        """
        try:
            # Convert pygame surface to PIL Image
            # Get raw pixel data
            raw_str = pygame.image.tostring(screen, "RGB")
            size = screen.get_size()

            self._gameplay_image = Image.frombytes("RGB", size, raw_str)
            self._gameplay_captured = True

            self._logger.info(f"Gameplay captured: {self._gameplay_image.size}")
            return True

        except Exception as e:
            self._logger.error(f"Gameplay capture error: {e}")
            return False

    def generate_composite(self, zombie_count: int) -> Optional[str]:
        """
        Generate final photo booth composite.

        Args:
            zombie_count: Number of zombies eliminated

        Returns:
            Path to saved composite image, or None on failure
        """
        self._logger.info(
            f"📸 generate_composite called: zombie_count={zombie_count}, "
            f"selfie_image={self._selfie_image is not None}, "
            f"gameplay_image={self._gameplay_image is not None}, "
            f"selfie_opted_in={self._selfie_opted_in}, "
            f"selfie_captured={self._selfie_captured}"
        )

        if self._gameplay_image is None:
            self._logger.error("📸 Cannot generate composite - no gameplay image")
            return None

        self._state = PhotoBoothState.COMPOSITING

        try:
            # Generate composite
            self._logger.info(
                f"📸 Generating composite with selfie={'YES' if self._selfie_image else 'NO'}"
            )
            composite = self._compositor.generate(
                selfie=self._selfie_image,
                gameplay=self._gameplay_image,
                zombie_count=zombie_count,
                config=self.config,
            )

            # Save to file
            self._composite_path = self._compositor.save(composite, self.config)

            self._state = PhotoBoothState.COMPLETE
            self._logger.info(f"📸 Composite saved to: {self._composite_path}")

            return self._composite_path

        except Exception as e:
            self._logger.error(f"📸 Composite generation error: {e}", exc_info=True)
            self._state = PhotoBoothState.ERROR
            return None

    def reset(self) -> None:
        """Reset controller for next arcade session."""
        self._selfie_opted_in = False
        self._selfie_image = None
        self._gameplay_image = None
        self._composite_path = None
        self._consent_prompt_start = 0.0
        self._arcade_start_time = 0.0
        self._gameplay_captured = False
        self._selfie_captured = False

        if self.config.enabled:
            self._state = PhotoBoothState.INACTIVE
        else:
            self._state = PhotoBoothState.DISABLED

    def start_arcade_tracking(self) -> None:
        """Start tracking arcade session time for delayed captures."""
        self._arcade_start_time = time.time()
        self._gameplay_captured = False
        self._selfie_captured = False
        self._logger.info("📸 Started arcade time tracking for photo booth")

    def get_arcade_elapsed_time(self) -> float:
        """Get elapsed time since arcade session started."""
        if self._arcade_start_time == 0.0:
            return 0.0
        return time.time() - self._arcade_start_time

    def should_capture_gameplay(self) -> bool:
        """Check if it's time to capture gameplay screenshot."""
        if self._gameplay_captured:
            return False
        elapsed = self.get_arcade_elapsed_time()
        return elapsed >= self.config.screenshot_delay

    def should_capture_selfie(self) -> bool:
        """Check if it's time to capture selfie."""
        if self._selfie_captured:
            return False
        if not self._selfie_opted_in:
            # Only log once per second to avoid spam
            elapsed = self.get_arcade_elapsed_time()
            if int(elapsed) % 5 == 0 and int(elapsed) > 0:
                self._logger.debug(f"📸 should_capture_selfie: selfie_opted_in=False, skipping")
            return False
        elapsed = self.get_arcade_elapsed_time()
        target_time = self.config.screenshot_delay + 1.0
        # Capture selfie slightly after gameplay screenshot
        if elapsed >= target_time:
            self._logger.info(
                f"📸 should_capture_selfie: YES - elapsed={elapsed:.1f}s >= target={target_time}s"
            )
            return True
        return False

    def has_minimum_arcade_time(self) -> bool:
        """Check if minimum arcade time has passed for photo generation."""
        elapsed = self.get_arcade_elapsed_time()
        return elapsed >= self.config.min_arcade_time

    @property
    def gameplay_captured(self) -> bool:
        """Whether gameplay screenshot has been captured."""
        return self._gameplay_captured

    @property
    def selfie_captured(self) -> bool:
        """Whether selfie has been captured."""
        return self._selfie_captured
