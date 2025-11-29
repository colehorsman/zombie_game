#!/usr/bin/env python3
"""Generate sample photo booth composites with different retro filter levels."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from PIL import Image, ImageDraw, ImageFilter

from photo_booth.compositor import PhotoBoothCompositor
from photo_booth.config import PhotoBoothConfig
from photo_booth.retro_filter import RetroFilter


def create_sample_gameplay_image():
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


def create_realistic_selfie():
    """Create a more realistic mock selfie with proper features."""
    img = Image.new("RGB", (640, 480), (80, 70, 65))  # Neutral background
    draw = ImageDraw.Draw(img)

    # Background gradient (office/room)
    for y in range(480):
        shade = int(60 + (y / 480) * 40)
        draw.line([(0, y), (640, y)], fill=(shade, shade - 10, shade - 5))

    # Shoulders/body (t-shirt)
    draw.ellipse([(180, 380), (460, 550)], fill=(50, 50, 120))  # Blue shirt

    # Neck
    draw.rectangle([(280, 320), (360, 400)], fill=(235, 190, 160))

    # Head shape (oval)
    draw.ellipse([(230, 80), (410, 340)], fill=(245, 200, 170))

    # Hair (on top)
    draw.ellipse([(225, 60), (415, 180)], fill=(60, 40, 25))  # Dark brown hair
    # Hair sides
    draw.ellipse([(220, 80), (260, 200)], fill=(60, 40, 25))
    draw.ellipse([(380, 80), (420, 200)], fill=(60, 40, 25))

    # Ears
    draw.ellipse([(218, 160), (245, 220)], fill=(235, 185, 155))
    draw.ellipse([(395, 160), (422, 220)], fill=(235, 185, 155))

    # Eyebrows
    draw.arc([(265, 155), (310, 180)], 180, 360, fill=(50, 35, 20), width=3)
    draw.arc([(330, 155), (375, 180)], 180, 360, fill=(50, 35, 20), width=3)

    # Eyes (white)
    draw.ellipse([(270, 175), (315, 210)], fill=(255, 255, 255))
    draw.ellipse([(325, 175), (370, 210)], fill=(255, 255, 255))

    # Iris (brown)
    draw.ellipse([(282, 182), (308, 208)], fill=(100, 70, 40))
    draw.ellipse([(337, 182), (363, 208)], fill=(100, 70, 40))

    # Pupils
    draw.ellipse([(290, 188), (302, 200)], fill=(20, 20, 20))
    draw.ellipse([(345, 188), (357, 200)], fill=(20, 20, 20))

    # Eye highlights
    draw.ellipse([(293, 190), (298, 195)], fill=(255, 255, 255))
    draw.ellipse([(348, 190), (353, 195)], fill=(255, 255, 255))

    # Nose
    draw.polygon([(320, 200), (305, 260), (320, 265), (335, 260)], fill=(235, 185, 155))
    draw.arc([(300, 250), (340, 275)], 0, 180, fill=(200, 160, 140), width=2)

    # Mouth/smile
    draw.arc([(285, 275), (355, 320)], 0, 180, fill=(180, 100, 100), width=3)
    # Lips
    draw.ellipse([(295, 285), (345, 310)], fill=(200, 120, 120))

    # Subtle cheek color
    draw.ellipse([(245, 220), (285, 260)], fill=(250, 195, 175))
    draw.ellipse([(355, 220), (395, 260)], fill=(250, 195, 175))

    # Slight blur for more realistic look
    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    return img


def main():
    print("🎮 Generating sample photo booth composites with different filter levels...")

    compositor = PhotoBoothCompositor()
    config = PhotoBoothConfig()

    # Create sample images
    gameplay = create_sample_gameplay_image()
    selfie = create_realistic_selfie()

    output_dir = ".kiro/evidence/booth_photos"
    os.makedirs(output_dir, exist_ok=True)

    # Save original selfie for comparison
    path_orig = os.path.join(output_dir, "SAMPLE_1_original_selfie.png")
    selfie.save(path_orig)
    print(f"✅ Saved original: {path_orig}")

    # 1. HEAVY retro (original 16-color, high pixelation)
    print("\n📸 1. Heavy retro effect (16 colors, pixel_size=6)...")
    heavy_selfie = RetroFilter.apply_full_retro_effect(selfie, pixel_size=6)
    path_heavy = os.path.join(output_dir, "SAMPLE_2_heavy_retro_selfie.png")
    heavy_selfie.save(path_heavy)
    print(f"✅ Saved: {path_heavy}")

    # 2. MEDIUM retro (32 colors, medium pixelation)
    print("\n📸 2. Medium retro effect (32 colors, pixel_size=4)...")
    medium_selfie = RetroFilter.apply_medium_retro_effect(selfie, pixel_size=4, num_colors=32)
    path_medium = os.path.join(output_dir, "SAMPLE_3_medium_retro_selfie.png")
    medium_selfie.save(path_medium)
    print(f"✅ Saved: {path_medium}")

    # 3. LIGHT retro (64 colors, light pixelation) - RECOMMENDED
    print("\n📸 3. Light retro effect (48 colors, pixel_size=3) - RECOMMENDED...")
    light_selfie = RetroFilter.apply_light_retro_effect(selfie, pixel_size=3, num_colors=48)
    path_light = os.path.join(output_dir, "SAMPLE_4_light_retro_selfie.png")
    light_selfie.save(path_light)
    print(f"✅ Saved: {path_light}")

    # 4. ARCADE selfie effect (the default for photo booth)
    print("\n📸 4. Arcade selfie effect (balanced for booth)...")
    arcade_selfie = RetroFilter.apply_arcade_selfie_effect(selfie)
    path_arcade = os.path.join(output_dir, "SAMPLE_5_arcade_selfie.png")
    arcade_selfie.save(path_arcade)
    print(f"✅ Saved: {path_arcade}")

    # Generate full composites with different selfie styles
    print("\n📸 Generating full composites...")

    # Composite with arcade selfie (new default)
    composite_arcade = compositor.generate(
        selfie=selfie,  # Compositor now applies arcade effect internally
        gameplay=gameplay,
        zombie_count=47,
        config=config,
    )
    path_comp_arcade = os.path.join(output_dir, "SAMPLE_6_composite_arcade.png")
    composite_arcade.save(path_comp_arcade)
    print(f"✅ Saved composite (arcade): {path_comp_arcade}")

    # Composite without selfie
    composite_no_selfie = compositor.generate(
        selfie=None, gameplay=gameplay, zombie_count=123, config=config
    )
    path_comp_no = os.path.join(output_dir, "SAMPLE_7_composite_no_selfie.png")
    composite_no_selfie.save(path_comp_no)
    print(f"✅ Saved composite (no selfie): {path_comp_no}")

    print(f"\n🎉 Done! Check {output_dir}/ for all sample images.")
    print("\n📋 Summary of filter levels:")
    print("  1. Original - No filter (for comparison)")
    print("  2. Heavy - 16 colors, high pixelation (very retro, loses detail)")
    print("  3. Medium - 32 colors, medium pixelation (balanced)")
    print("  4. Light - 48 colors, light pixelation (preserves features)")
    print("  5. Arcade - Optimized for photo booth (recommended)")
    print("  6. Full composite with arcade selfie")
    print("  7. Full composite without selfie")


if __name__ == "__main__":
    main()
