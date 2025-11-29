"""
Photo Booth Configuration.

Loads settings from environment variables with sensible defaults.
"""

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


def detect_best_camera() -> int:
    """
    Auto-detect the best available camera.

    Prefers external cameras (higher index, typically better FPS) over built-in.
    Returns the camera index with the highest FPS, or 0 if detection fails.
    """
    try:
        import cv2
    except ImportError:
        print("📷 CAMERA DETECTION: OpenCV not available")
        return 0

    print("📷 CAMERA DETECTION: Scanning for cameras...")
    best_camera = 0
    best_fps = 0.0
    cameras_found = []

    # Check first 5 camera indices
    for i in range(5):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    # Try to get camera name/backend
                    backend = cap.getBackendName()
                    camera_info = f"Camera {i}: {width}x{height} @ {fps} FPS (backend: {backend})"
                    cameras_found.append(camera_info)
                    print(f"📷 FOUND: {camera_info}")
                    logger.info(f"📷 Camera {i}: {width}x{height} @ {fps} FPS")

                    # Prefer higher FPS (external cameras usually have better FPS)
                    # Also prefer higher index if FPS is similar (external usually higher index)
                    if fps > best_fps or (fps == best_fps and i > best_camera):
                        best_fps = fps
                        best_camera = i
                cap.release()
        except Exception as e:
            print(f"📷 Camera {i}: Error - {e}")

    if cameras_found:
        print(f"📷 CAMERA DETECTION: Found {len(cameras_found)} camera(s)")
        print(f"📷 CAMERA DETECTION: Selected camera {best_camera} (FPS: {best_fps})")
        logger.info(f"📷 Selected camera {best_camera} (best FPS: {best_fps})")
    else:
        print("📷 CAMERA DETECTION: No cameras found!")

    return best_camera


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
    min_arcade_time: float = 5.0  # minimum seconds of arcade play before photo capture
    screenshot_delay: float = 5.0  # seconds into arcade mode to capture gameplay screenshot

    @classmethod
    def from_env(cls) -> "PhotoBoothConfig":
        """Load configuration from environment variables."""
        # Auto-detect camera if not explicitly set
        camera_env = os.getenv("PHOTO_BOOTH_CAMERA_INDEX")
        if camera_env is not None:
            camera_index = int(camera_env)
        elif os.getenv("PHOTO_BOOTH_AUTO_DETECT_CAMERA", "true").lower() == "true":
            camera_index = detect_best_camera()
        else:
            camera_index = 0

        return cls(
            enabled=os.getenv("PHOTO_BOOTH_ENABLED", "true").lower() == "true",
            camera_index=camera_index,
            event_name=os.getenv("PHOTO_BOOTH_EVENT_NAME", "AWS re:Invent 2025"),
            booth_number=os.getenv("PHOTO_BOOTH_BOOTH_NUMBER", "435"),
            qr_url=os.getenv("PHOTO_BOOTH_QR_URL", "https://sonraisecurity.com/zombie-blaster"),
            hashtag=os.getenv("PHOTO_BOOTH_HASHTAG", "#SonraiZombieBlaster"),
            output_dir=os.getenv("PHOTO_BOOTH_OUTPUT_DIR", ".kiro/evidence/booth_photos"),
            consent_timeout=float(os.getenv("PHOTO_BOOTH_CONSENT_TIMEOUT", "5.0")),
            min_arcade_time=float(os.getenv("PHOTO_BOOTH_MIN_ARCADE_TIME", "10.0")),
            screenshot_delay=float(os.getenv("PHOTO_BOOTH_SCREENSHOT_DELAY", "15.0")),
        )
