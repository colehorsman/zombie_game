#!/usr/bin/env python3
"""Generate final photo booth composite using LIVE_3_purple with more 8-bit pixelation."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from PIL import Image, ImageDraw

from photo_booth.compositor import PhotoBoothCompositor
from photo_booth.config import PhotoBoothConfig
from photo_booth.retro_filter import RetroFilter


def create_gameplay_screenshot():
    """Create a mock gameplay screenshot."""
    img = Image.new("RGB", (1280, 720), (40, 20, 60))  # Purple background
    draw = ImageDraw.Draw(img)

    # Draw some "zombies" (green rectangles with more detail)
    for i in range(8):
        x = 100 + i * 140
        y = 400
        # Body
        draw.rectangle([(x, y), (x + 40, y + 60)], fill=(0, 180, 0))
        # Head
        draw.ellipse([(x + 5, y - 20), (x + 35, y + 10)], fill=(0, 200, 0))
        # Eyes
        draw.ellipse([(x + 10, y - 10), (x + 18, y - 2)], fill=(255, 0, 0))
        draw.ellipse([(x + 22, y - 10), (x + 30, y - 2)], fill=(255, 0, 0))
        # Arms
        draw.rectangle([(x - 8, y + 10), (x, y + 40)], fill=(0, 160, 0))
        draw.rectangle([(x + 40, y + 10), (x + 48, y + 40)], fill=(0, 160, 0))

    # Draw player (more detailed)
    px, py = 600, 380
    # Body
    draw.rectangle([(px, py), (px + 50, py + 80)], fill=(138, 43, 226))
    # Head
    draw.ellipse([(px + 10, py - 30), (px + 40, py)], fill=(255, 200, 150))
    # Raygun
    draw.rectangle([(px + 45, py + 30), (px + 70, py + 45)], fill=(255, 165, 0))

    # Draw raygun beam
    draw.line([(px + 70, py + 37), (px + 200, py + 37)], fill=(255, 255, 0), width=6)

    # Draw ground with texture
    draw.rectangle([(0, 500), (1280, 720)], fill=(60, 40, 80))
    for i in range(0, 1280, 40):
        draw.line([(i, 500), (i, 720)], fill=(70, 50, 90), width=1)

    # Draw HUD elements
    draw.text((20, 20), "ARCADE MODE", fill=(255, 215, 0))
    draw.text((20, 50), "TIME: 0:47", fill=(255, 255, 255))
    draw.text((1100, 20), "COMBO: x5", fill=(255, 100, 100))
    draw.text((1100, 50), "SCORE: 4700", fill=(255, 215, 0))

    return img


def apply_heavy_8bit_effect(img: Image.Image) -> Image.Image:
    """Apply heavier 8-bit pixelation effect while keeping recognizable."""
    # More aggressive pixelation (pixel_size=6 for chunky 8-bit look)
    pixel_size = 6
    small = img.resize((img.width // pixel_size, img.height // pixel_size), Image.NEAREST)
    pixelated = small.resize(img.size, Image.NEAREST)

    # Reduce to 24 colors for more retro feel (but not too few)
    num_colors = 24
    quantized = pixelated.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
    result = quantized.convert("RGB")

    return result


def main():
    print("🎮 Generating FINAL photo booth composite with zombie icons...")

    output_dir = ".kiro/evidence/booth_photos"
    os.makedirs(output_dir, exist_ok=True)

    # Check if LIVE_3_purple exists
    live3_path = os.path.join(output_dir, "LIVE_3_purple_bg.png")

    if os.path.exists(live3_path):
        print(f"✅ Found LIVE_3_purple_bg.png")
        selfie = Image.open(live3_path)

        # Apply heavier 8-bit pixelation
        print("📸 Applying heavy 8-bit pixelation...")
        selfie_8bit = apply_heavy_8bit_effect(selfie)

        # Save the 8-bit version
        path_8bit = os.path.join(output_dir, "LIVE_4_8bit_heavy.png")
        selfie_8bit.save(path_8bit)
        print(f"✅ Saved 8-bit version: {path_8bit}")
    else:
        print(f"⚠️ LIVE_3_purple_bg.png not found at {live3_path}")
        print("   Using generated selfie instead...")
        selfie_8bit = None

    # Create gameplay screenshot
    gameplay = create_gameplay_screenshot()

    # Create compositor and config
    compositor = PhotoBoothCompositor()
    config = PhotoBoothConfig()

    # Generate composite with zombie icons
    print("\n📸 Generating final composite with zombie icons...")

    if selfie_8bit:
        # Use the 8-bit selfie directly, skip compositor's retro filter
        composite = compositor.generate(
            selfie=selfie_8bit,
            gameplay=gameplay,
            zombie_count=42,
            config=config,
            skip_selfie_retro=True,  # Already processed!
        )
    else:
        composite = compositor.generate(
            selfie=None, gameplay=gameplay, zombie_count=42, config=config
        )

    # Save final composite
    path_final = os.path.join(output_dir, "FINAL_composite.png")
    composite.save(path_final)
    print(f"✅ Saved FINAL composite: {path_final}")

    # Also generate variations
    print("\n📸 Generating additional variations...")

    # Variation with different zombie counts
    for count in [13, 42, 99]:
        composite_var = compositor.generate(
            selfie=selfie_8bit if selfie_8bit else None,
            gameplay=gameplay,
            zombie_count=count,
            config=config,
            skip_selfie_retro=True if selfie_8bit else False,
        )
        path_var = os.path.join(output_dir, f"FINAL_{count}_zombies.png")
        composite_var.save(path_var)
        print(f"✅ Saved: {path_var}")

    print(f"\n🎉 Done! Check {output_dir}/ for final composites.")
    print("\n📋 Generated files:")
    print("  - LIVE_4_8bit_heavy.png - Your selfie with heavy 8-bit effect")
    print("  - FINAL_composite.png - Complete booth photo with zombie icons")
    print("  - FINAL_13_zombies.png - Variation with 13 zombies")
    print("  - FINAL_42_zombies.png - Variation with 42 zombies")
    print("  - FINAL_99_zombies.png - Variation with 99 zombies")


if __name__ == "__main__":
    main()
