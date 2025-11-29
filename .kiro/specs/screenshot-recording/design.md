# Screenshot & Recording System - Design

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Game Engine                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              EvidenceCapture System                  │   │
│  │                                                      │   │
│  │   [X/F12] → Screenshot → .kiro/evidence/screenshots/ │   │
│  │   [Y/F9]  → Recording  → .kiro/evidence/recordings/  │   │
│  │                                                      │   │
│  │   ┌─────────────┐  ┌─────────────┐                  │   │
│  │   │ Screenshot  │  │  Recorder   │                  │   │
│  │   │   Manager   │  │   Manager   │                  │   │
│  │   └─────────────┘  └─────────────┘                  │   │
│  │         │                 │                          │   │
│  │         ▼                 ▼                          │   │
│  │   [Flash Effect]   [REC Indicator]                   │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Model

### EvidenceCapture Class

```python
import os
import pygame
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field

@dataclass
class EvidenceCapture:
    """Manages screenshot and recording capture for evidence gathering."""

    # Directories
    EVIDENCE_DIR = ".kiro/evidence"
    SCREENSHOTS_DIR = ".kiro/evidence/screenshots"
    RECORDINGS_DIR = ".kiro/evidence/recordings"

    # Recording settings
    MAX_RECORDING_SECONDS: int = 60
    RECORDING_FPS: int = 30

    # State
    is_recording: bool = False
    recording_start_time: float = 0.0
    recording_frames: List[pygame.Surface] = field(default_factory=list)
    last_frame_time: float = 0.0

    # Visual feedback
    flash_alpha: int = 0  # For screenshot flash effect
    flash_duration: float = 0.15  # Seconds

    def __post_init__(self):
        """Ensure directories exist."""
        os.makedirs(self.SCREENSHOTS_DIR, exist_ok=True)
        os.makedirs(self.RECORDINGS_DIR, exist_ok=True)

    def _generate_filename(self, extension: str) -> str:
        """Generate filename with timestamp: ZB_YYYYMMDD_HHMMSS.ext"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"ZB_{timestamp}.{extension}"

    def take_screenshot(self, screen: pygame.Surface) -> str:
        """Capture screenshot and save to file. Returns filename."""
        filename = self._generate_filename("png")
        filepath = os.path.join(self.SCREENSHOTS_DIR, filename)
        pygame.image.save(screen, filepath)
        self.flash_alpha = 255  # Trigger flash effect
        return filename

    def start_recording(self, current_time: float) -> None:
        """Start recording frames."""
        if self.is_recording:
            return
        self.is_recording = True
        self.recording_start_time = current_time
        self.recording_frames = []
        self.last_frame_time = current_time

    def stop_recording(self) -> Optional[str]:
        """Stop recording and save to file. Returns filename or None."""
        if not self.is_recording:
            return None
        self.is_recording = False
        if not self.recording_frames:
            return None
        return self._save_recording()

    def toggle_recording(self, current_time: float) -> Optional[str]:
        """Toggle recording state. Returns filename if stopped."""
        if self.is_recording:
            return self.stop_recording()
        else:
            self.start_recording(current_time)
            return None

    def capture_frame(self, screen: pygame.Surface, current_time: float) -> None:
        """Capture frame if recording and enough time has passed."""
        if not self.is_recording:
            return

        # Check if max duration reached
        elapsed = current_time - self.recording_start_time
        if elapsed >= self.MAX_RECORDING_SECONDS:
            self.stop_recording()
            return

        # Capture at recording FPS (not every frame)
        frame_interval = 1.0 / self.RECORDING_FPS
        if current_time - self.last_frame_time >= frame_interval:
            # Copy the screen surface
            frame = screen.copy()
            self.recording_frames.append(frame)
            self.last_frame_time = current_time

    def _save_recording(self) -> str:
        """Save recorded frames as GIF."""
        filename = self._generate_filename("gif")
        filepath = os.path.join(self.RECORDINGS_DIR, filename)

        # Convert pygame surfaces to PIL images and save as GIF
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
                    loop=0
                )
        except ImportError:
            # Fallback: save frames as individual PNGs
            return self._save_frames_as_pngs()

        self.recording_frames = []  # Clear memory
        return filename

    def _save_frames_as_pngs(self) -> str:
        """Fallback: save frames as numbered PNGs."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = os.path.join(self.RECORDINGS_DIR, f"ZB_{timestamp}")
        os.makedirs(folder, exist_ok=True)

        for i, frame in enumerate(self.recording_frames):
            filepath = os.path.join(folder, f"frame_{i:04d}.png")
            pygame.image.save(frame, filepath)

        self.recording_frames = []
        return f"ZB_{timestamp}/"

    def get_recording_duration(self, current_time: float) -> float:
        """Get current recording duration in seconds."""
        if not self.is_recording:
            return 0.0
        return current_time - self.recording_start_time

    def update_flash(self, delta_time: float) -> None:
        """Update screenshot flash effect."""
        if self.flash_alpha > 0:
            # Fade out over flash_duration
            fade_rate = 255 / self.flash_duration
            self.flash_alpha = max(0, self.flash_alpha - fade_rate * delta_time)
```

## Visual Feedback

### Screenshot Flash Effect

```python
def render_screenshot_flash(self, screen: pygame.Surface) -> None:
    """Render white flash overlay when screenshot taken."""
    if self.evidence_capture.flash_alpha > 0:
        flash_surface = pygame.Surface(screen.get_size())
        flash_surface.fill((255, 255, 255))
        flash_surface.set_alpha(int(self.evidence_capture.flash_alpha))
        screen.blit(flash_surface, (0, 0))
```

### Recording Indicator

```python
def render_recording_indicator(self, screen: pygame.Surface, current_time: float) -> None:
    """Render red recording dot and timer in top-right corner."""
    if not self.evidence_capture.is_recording:
        return

    # Position in top-right corner
    x = screen.get_width() - 100
    y = 20

    # Pulsing red dot
    pulse = (math.sin(current_time * 4) + 1) / 2  # 0 to 1
    red_intensity = int(180 + 75 * pulse)  # 180-255

    # Draw red circle
    pygame.draw.circle(screen, (red_intensity, 0, 0), (x, y), 8)
    pygame.draw.circle(screen, (255, 255, 255), (x, y), 8, 2)  # White border

    # Draw "REC" text
    font = pygame.font.Font(None, 24)
    rec_text = font.render("REC", True, (255, 0, 0))
    screen.blit(rec_text, (x + 15, y - 8))

    # Draw timer
    duration = self.evidence_capture.get_recording_duration(current_time)
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    timer_text = font.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
    screen.blit(timer_text, (x + 50, y - 8))
```

## Input Handling

### Controller Buttons

```python
# In game_engine.py event loop
elif event.type == pygame.JOYBUTTONDOWN:
    # Screenshot - X button (button 2)
    if event.button == 2:
        filename = self.evidence_capture.take_screenshot(self.screen)
        logger.info(f"📸 Screenshot saved: {filename}")

    # Recording toggle - Y button (button 3)
    elif event.button == 3:
        result = self.evidence_capture.toggle_recording(current_time)
        if result:
            logger.info(f"🎬 Recording saved: {result}")
        elif self.evidence_capture.is_recording:
            logger.info("🔴 Recording started...")
```

### Keyboard Keys

```python
# In game_engine.py event loop
elif event.type == pygame.KEYDOWN:
    # Screenshot - F12
    if event.key == pygame.K_F12:
        filename = self.evidence_capture.take_screenshot(self.screen)
        logger.info(f"📸 Screenshot saved: {filename}")

    # Recording toggle - F9
    elif event.key == pygame.K_F9:
        result = self.evidence_capture.toggle_recording(current_time)
        if result:
            logger.info(f"🎬 Recording saved: {result}")
        elif self.evidence_capture.is_recording:
            logger.info("🔴 Recording started...")
```

## Game Loop Integration

```python
# In GameEngine.__init__
from evidence_capture import EvidenceCapture
self.evidence_capture = EvidenceCapture()

# In main game loop (after rendering, before display flip)
def _render_frame(self):
    # ... existing rendering ...

    # Capture frame if recording
    self.evidence_capture.capture_frame(self.screen, self.current_time)

    # Render recording indicator
    self.renderer.render_recording_indicator(self.screen, self.current_time)

    # Render screenshot flash
    self.renderer.render_screenshot_flash(self.screen)

    # Update flash effect
    self.evidence_capture.update_flash(self.delta_time)

    # ... display flip ...
```

## File Structure

```
.kiro/evidence/
├── README.md                    # Explains evidence structure
├── screenshots/
│   ├── ZB_20241128_223045.png
│   ├── ZB_20241128_223112.png
│   └── ...
└── recordings/
    ├── ZB_20241128_223200.gif
    ├── ZB_20241128_223315.gif
    └── ...
```

## Dependencies

### Required
- `pygame` (already installed) - Screen capture
- `Pillow` (PIL) - GIF creation

### Installation
```bash
pip install Pillow
```

Add to `requirements.txt`:
```
Pillow>=10.0.0
```

## Performance Considerations

### Screenshot
- Single frame capture: < 50ms
- PNG compression: handled by pygame
- No frame drop expected

### Recording
- Frame capture every 33ms (30 FPS)
- Memory: ~3MB per second of recording
- 60 seconds max = ~180MB peak memory
- GIF encoding on stop: 1-3 seconds

### Optimization
- Only capture every other game frame (30 FPS recording vs 60 FPS game)
- Scale down frames for smaller GIFs (optional)
- Clear frames immediately after saving

## Error Handling

```python
def take_screenshot(self, screen: pygame.Surface) -> Optional[str]:
    """Capture screenshot with error handling."""
    try:
        filename = self._generate_filename("png")
        filepath = os.path.join(self.SCREENSHOTS_DIR, filename)
        pygame.image.save(screen, filepath)
        self.flash_alpha = 255
        return filename
    except Exception as e:
        logger.error(f"❌ Screenshot failed: {e}")
        return None
```

## Testing Strategy

### Unit Tests
- Filename generation format
- Directory creation
- Flash effect timing
- Recording duration calculation

### Integration Tests
- Screenshot saves valid PNG
- Recording saves valid GIF
- Controller buttons trigger capture
- Keyboard keys trigger capture

### Manual Tests
- Visual flash effect visible
- Recording indicator visible
- Files appear in correct directories
- GIF plays correctly
