#!/usr/bin/env python3
"""Capture a live selfie with countdown and background removal."""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    import cv2
except ImportError:
    print("❌ OpenCV not available. Install with: pip install opencv-python")
    sys.exit(1)

from PIL import Image, ImageDraw

from photo_booth.compositor import PhotoBoothCompositor
from photo_booth.config import PhotoBoothConfig
from photo_booth.retro_filter import RetroFilter

# Try to import rembg for background removal
try:
    from rembg import remove as remove_bg

    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("⚠️ rembg not available - background removal disabled")


def capture_webcam_with_countdown(camera_index=0, countdown_seconds=5):
    """Capture with countdown so you can get in frame."""
    print(f"📷 Opening webcam (index {camera_index})...")
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("❌ Could not open webcam")
        return None

    print(f"\n🎬 GET READY! Capturing in {countdown_seconds} seconds...")
    print("   Position yourself in the frame!\n")

    # Countdown with camera warmup
    for i in range(countdown_seconds, 0, -1):
        print(f"   {i}...")
        cap.read()  # Keep reading to warm up
        time.sleep(1)

    print("   📸 CHEESE!")
    time.sleep(0.3)  # Brief pause

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        print("❌ Failed to capture image")
        return None

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame_rgb)


def remove_background(image):
    """Remove background from image, keeping only the person."""
    if not REMBG_AVAILABLE:
        print("⚠️ Background removal not available")
        return image

    print("🔄 Removing background...")
    # rembg returns RGBA with transparent background
    result = remove_bg(image)
    return result


def add_purple_background(image):
    """Add purple game-themed background to transparent image."""
    if image.mode != "RGBA":
        return image

    # Create purple background matching game theme
    bg = Image.new("RGBA", image.size, (40, 20, 60, 255))
    # Composite the person on top
    bg.paste(image, (0, 0), image)
    return bg.convert("RGB")


def create_sample_gameplay_image():
    """Create a mock gameplay screenshot."""
    img = Image.new("RGB", (1280, 720), (40, 20, 60))
    draw = ImageDraw.Draw(img)

    for i in range(8):
        x = 100 + i * 140
        y = 400
        draw.rectangle([(x, y), (x + 40, y + 60)], fill=(0, 180, 0))
        draw.ellipse([(x + 5, y - 20), (x + 35, y + 10)], fill=(0, 200, 0))
        draw.ellipse([(x + 10, y - 10), (x + 18, y - 2)], fill=(255, 0, 0))
        draw.ellipse([(x + 22, y - 10), (x + 30, y - 2)], fill=(255, 0, 0))

    px, py = 600, 380
    draw.rectangle([(px, py), (px + 50, py + 80)], fill=(138, 43, 226))
    draw.ellipse([(px + 10, py - 30), (px + 40, py)], fill=(255, 200, 150))
    draw.rectangle([(px + 45, py + 30), (px + 70, py + 45)], fill=(255, 165, 0))
    draw.line([(px + 70, py + 37), (px + 200, py + 37)], fill=(255, 255, 0), width=6)
    draw.rectangle([(0, 500), (1280, 720)], fill=(60, 40, 80))
    draw.text((20, 20), "ARCADE MODE", fill=(255, 215, 0))
    draw.text((20, 50), "TIME: 0:47", fill=(255, 255, 255))
    draw.text((1100, 20), "COMBO: x5", fill=(255, 100, 100))

    return img


# 32-color balanced palette for skin tones + game colors
BALANCED_PALETTE = [
    # Skin tones
    (255, 224, 189),
    (255, 205, 148),
    (234, 192, 134),
    (200, 160, 130),
    (165, 126, 82),
    (90, 56, 37),
    # Hair
    (0, 0, 0),
    (60, 40, 25),
    (120, 80, 40),
    (180, 140, 80),
    (220, 200, 180),
    # Eyes
    (66, 133, 244),
    (76, 153, 0),
    (100, 70, 40),
    # Game theme
    (255, 255, 255),
    (128, 0, 128),
    (75, 0, 130),
    (138, 43, 226),
    (255, 165, 0),
    (255, 0, 0),
    (0, 200, 0),
    (0, 128, 0),
    (255, 255, 0),
    (255, 192, 203),
    # Grays
    (32, 32, 32),
    (64, 64, 64),
    (96, 96, 96),
    (128, 128, 128),
    (160, 160, 160),
    (192, 192, 192),
    # Lip/cheek
    (200, 120, 120),
    (180, 100, 100),
]


def main():
    print("🎮 Photo Booth - Live Capture with Background Removal")
    print("=" * 55)

    output_dir = ".kiro/evidence/booth_photos"
    os.makedirs(output_dir, exist_ok=True)

    # Capture with countdown
    selfie = capture_webcam_with_countdown(countdown_seconds=5)
    if selfie is None:
        print("❌ Could not capture selfie. Exiting.")
        return

    print(f"✅ Captured selfie: {selfie.size}")

    # Save original
    path_orig = os.path.join(output_dir, "LIVE_1_original.png")
    selfie.save(path_orig)
    print(f"✅ Original: {path_orig}")

    # Remove background
    selfie_nobg = remove_background(selfie)

    # Save with transparent background
    path_nobg = os.path.join(output_dir, "LIVE_2_no_background.png")
    selfie_nobg.save(path_nobg)
    print(f"✅ No background: {path_nobg}")

    # Add purple background
    selfie_purple = add_purple_background(selfie_nobg)
    path_purple = os.path.join(output_dir, "LIVE_3_purple_bg.png")
    selfie_purple.save(path_purple)
    print(f"✅ Purple background: {path_purple}")

    compositor = PhotoBoothCompositor()
    config = PhotoBoothConfig()
    gameplay = create_sample_gameplay_image()

    print("\n📸 Testing retro filter combinations...")

    # Option A: pixel=5, 32 colors
    opt_a = RetroFilter.pixelate(selfie_purple, pixel_size=5)
    opt_a = RetroFilter.reduce_colors(opt_a, BALANCED_PALETTE)
    path_a = os.path.join(output_dir, "TEST_A_px5_32col.png")
    opt_a.save(path_a)
    print(f"✅ A: pixel=5, 32 colors")

    # Option B: pixel=4, 32 colors
    opt_b = RetroFilter.pixelate(selfie_purple, pixel_size=4)
    opt_b = RetroFilter.reduce_colors(opt_b, BALANCED_PALETTE)
    path_b = os.path.join(output_dir, "TEST_B_px4_32col.png")
    opt_b.save(path_b)
    print(f"✅ B: pixel=4, 32 colors")

    # Option C: pixel=5, 64 colors
    opt_c = RetroFilter.pixelate(selfie_purple, pixel_size=5)
    opt_c = RetroFilter.reduce_colors(opt_c, RetroFilter.EXTENDED_PALETTE)
    path_c = os.path.join(output_dir, "TEST_C_px5_64col.png")
    opt_c.save(path_c)
    print(f"✅ C: pixel=5, 64 colors")

    # Option D: soft pixel=5, 32 colors
    opt_d = RetroFilter.soft_pixelate(selfie_purple, pixel_size=5)
    opt_d = RetroFilter.reduce_colors(opt_d, BALANCED_PALETTE)
    path_d = os.path.join(output_dir, "TEST_D_soft5_32col.png")
    opt_d.save(path_d)
    print(f"✅ D: soft pixel=5, 32 colors")

    print("\n📸 Generating composites...")

    for name, opt in [("A", opt_a), ("B", opt_b), ("C", opt_c), ("D", opt_d)]:
        comp = compositor.generate(selfie=opt, gameplay=gameplay, zombie_count=42, config=config)
        path = os.path.join(output_dir, f"COMP_{name}.png")
        comp.save(path)
        print(f"✅ Composite {name}: {path}")

    print(f"\n🎉 Done! Check {output_dir}/")
    print("\n📋 Options:")
    print("  A: pixel=5, 32 colors - Chunky 8-bit, good skin tones")
    print("  B: pixel=4, 32 colors - Slightly more detail")
    print("  C: pixel=5, 64 colors - Chunky, more color nuance")
    print("  D: soft=5, 32 colors - Softer edges")


if __name__ == "__main__":
    main()
