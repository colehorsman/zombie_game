"""
Photo Booth Configuration.

Loads settings from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass


@dataclass
class PhotoBoothConfig:
    """Configuration for photo booth feature."""

    enabled: bool = True
    camera_index: int = 0
    event_name: str = "AWS re:Invent 2025"
    booth_number: str = "435"
    qr_url: str = "https://sonraisecurity.com/zombie-blaster"
    hashtag: str = "#SonraiZombieBlaster"
    output_dir: str = ".kiro/evidence/booth_photos"
    consent_timeout: float = 5.0  # seconds
    min_arcade_time: float = 10.0  # minimum seconds of arcade play before photo capture
    screenshot_delay: float = 15.0  # seconds into arcade mode to capture gameplay screenshot

    @classmethod
    def from_env(cls) -> "PhotoBoothConfig":
        """Load configuration from environment variables."""
        return cls(
            enabled=os.getenv("PHOTO_BOOTH_ENABLED", "true").lower() == "true",
            camera_index=int(os.getenv("PHOTO_BOOTH_CAMERA_INDEX", "0")),
            event_name=os.getenv("PHOTO_BOOTH_EVENT_NAME", "AWS re:Invent 2025"),
            booth_number=os.getenv("PHOTO_BOOTH_BOOTH_NUMBER", "435"),
            qr_url=os.getenv("PHOTO_BOOTH_QR_URL", "https://sonraisecurity.com/zombie-blaster"),
            hashtag=os.getenv("PHOTO_BOOTH_HASHTAG", "#SonraiZombieBlaster"),
            output_dir=os.getenv("PHOTO_BOOTH_OUTPUT_DIR", ".kiro/evidence/booth_photos"),
            consent_timeout=float(os.getenv("PHOTO_BOOTH_CONSENT_TIMEOUT", "5.0")),
            min_arcade_time=float(os.getenv("PHOTO_BOOTH_MIN_ARCADE_TIME", "10.0")),
            screenshot_delay=float(os.getenv("PHOTO_BOOTH_SCREENSHOT_DELAY", "15.0")),
        )
