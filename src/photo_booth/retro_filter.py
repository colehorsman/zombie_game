"""
Retro 8-bit filter effects for photo booth selfies.

Applies pixelation, color reduction, and CRT scanline effects
to create an authentic retro gaming aesthetic while preserving
recognizable features.
"""

import logging
import math

from PIL import Image, ImageDraw, ImageEnhance

# Try to import rembg for background removal
try:
    from rembg import remove as remove_bg

    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    logging.warning("rembg not available - background removal disabled")

logger = logging.getLogger(__name__)


class RetroFilter:
    """Applies retro 8-bit effects to images."""

    # 16-color retro palette (matching game theme)
    RETRO_PALETTE = [
        (0, 0, 0),  # Black
        (255, 255, 255),  # White
        (128, 0, 128),  # Purple (Sonrai)
        (75, 0, 130),  # Indigo
        (138, 43, 226),  # Blue Violet
        (0, 255, 0),  # Green (zombie)
        (0, 128, 0),  # Dark Green
        (255, 165, 0),  # Orange (AWS)
        (255, 69, 0),  # Red Orange
        (255, 0, 0),  # Red
        (255, 192, 203),  # Pink
        (64, 64, 64),  # Dark Gray
        (128, 128, 128),  # Gray
        (192, 192, 192),  # Light Gray
        (0, 0, 255),  # Blue
        (255, 255, 0),  # Yellow
    ]

    # Extended 64-color palette for better photo quality
    EXTENDED_PALETTE = [
        # Skin tones
        (255, 224, 189),  # Light skin
        (255, 205, 148),  # Medium light skin
        (234, 192, 134),  # Medium skin
        (255, 173, 96),  # Tan
        (165, 126, 82),  # Medium dark skin
        (90, 56, 37),  # Dark skin
        (60, 46, 40),  # Very dark skin
        # Hair colors
        (0, 0, 0),  # Black
        (44, 34, 30),  # Dark brown
        (89, 60, 31),  # Brown
        (166, 124, 54),  # Light brown
        (220, 208, 186),  # Blonde
        (255, 245, 225),  # Platinum
        (141, 74, 67),  # Auburn
        (181, 82, 57),  # Red
        (128, 128, 128),  # Gray
        # Eyes
        (66, 133, 244),  # Blue
        (76, 153, 0),  # Green
        (139, 90, 43),  # Brown
        (64, 64, 64),  # Dark
        # Clothing/background common colors
        (255, 255, 255),  # White
        (0, 0, 0),  # Black
        (128, 0, 128),  # Purple (Sonrai)
        (75, 0, 130),  # Indigo
        (138, 43, 226),  # Blue Violet
        (255, 165, 0),  # Orange (AWS)
        (255, 0, 0),  # Red
        (0, 128, 0),  # Green
        (0, 0, 255),  # Blue
        (255, 255, 0),  # Yellow
        (255, 192, 203),  # Pink
        (0, 255, 255),  # Cyan
        (255, 0, 255),  # Magenta
        # Grays
        (32, 32, 32),
        (64, 64, 64),
        (96, 96, 96),
        (128, 128, 128),
        (160, 160, 160),
        (192, 192, 192),
        (224, 224, 224),
        # Additional skin/face tones
        (255, 200, 180),
        (240, 180, 160),
        (220, 160, 140),
        (200, 140, 120),
        (180, 120, 100),
        # Lip colors
        (200, 100, 100),
        (180, 80, 80),
        (220, 120, 120),
        # Background neutrals
        (100, 80, 60),
        (80, 60, 40),
        (60, 40, 20),
        (40, 30, 20),
        (120, 100, 80),
        (140, 120, 100),
        (160, 140, 120),
        (180, 160, 140),
        (200, 180, 160),
        (220, 200, 180),
        (240, 220, 200),
        # Blues for backgrounds
        (100, 150, 200),
        (80, 120, 180),
        (60, 100, 160),
    ]

    # 32-color balanced palette optimized for skin tones + game colors
    # This creates a more authentic video game character look
    VIDEO_GAME_PALETTE = [
        # Skin tones (essential for recognizable faces)
        (255, 224, 189),  # Light skin
        (255, 205, 148),  # Medium light skin
        (234, 192, 134),  # Medium skin
        (200, 160, 130),  # Tan
        (165, 126, 82),  # Medium dark skin
        (90, 56, 37),  # Dark skin
        # Hair colors
        (0, 0, 0),  # Black
        (60, 40, 25),  # Dark brown
        (120, 80, 40),  # Brown
        (180, 140, 80),  # Light brown
        (220, 200, 180),  # Blonde
        # Eyes
        (66, 133, 244),  # Blue
        (76, 153, 0),  # Green
        (100, 70, 40),  # Brown
        # Game theme colors (Sonrai/AWS/Zombie)
        (255, 255, 255),  # White
        (128, 0, 128),  # Purple (Sonrai)
        (75, 0, 130),  # Indigo
        (138, 43, 226),  # Blue Violet
        (40, 20, 60),  # Dark purple (background)
        (255, 165, 0),  # Orange (AWS)
        (255, 0, 0),  # Red
        (0, 200, 0),  # Zombie green
        (0, 128, 0),  # Dark green
        (255, 255, 0),  # Yellow
        (255, 192, 203),  # Pink
        # Grays for depth
        (32, 32, 32),
        (64, 64, 64),
        (96, 96, 96),
        (128, 128, 128),
        (160, 160, 160),
        # Lip/cheek tones
        (200, 120, 120),
        (180, 100, 100),
    ]

    @staticmethod
    def pixelate(image: Image.Image, pixel_size: int = 8) -> Image.Image:
        """
        Pixelate image to retro resolution.

        Args:
            image: PIL Image to pixelate
            pixel_size: Size of pixel blocks (larger = more pixelated)

        Returns:
            Pixelated image at original size
        """
        # Downsample
        small_width = max(1, image.width // pixel_size)
        small_height = max(1, image.height // pixel_size)
        small = image.resize((small_width, small_height), Image.NEAREST)

        # Scale back up with nearest neighbor (blocky pixels)
        return small.resize(image.size, Image.NEAREST)

    @staticmethod
    def soft_pixelate(image: Image.Image, pixel_size: int = 4) -> Image.Image:
        """
        Softer pixelation that preserves more detail.

        Args:
            image: PIL Image to pixelate
            pixel_size: Size of pixel blocks (smaller = more detail)

        Returns:
            Softly pixelated image
        """
        # Downsample with bilinear for smoother result
        small_width = max(1, image.width // pixel_size)
        small_height = max(1, image.height // pixel_size)
        small = image.resize((small_width, small_height), Image.BILINEAR)

        # Scale back up with bilinear for softer pixels
        return small.resize(image.size, Image.NEAREST)

    @staticmethod
    def _color_distance(c1: tuple, c2: tuple) -> float:
        """Calculate Euclidean distance between two RGB colors."""
        return math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2)

    @staticmethod
    def _find_nearest_color(color: tuple, palette: list) -> tuple:
        """Find the nearest color in the palette."""
        min_distance = float("inf")
        nearest = palette[0]

        for palette_color in palette:
            distance = RetroFilter._color_distance(color, palette_color)
            if distance < min_distance:
                min_distance = distance
                nearest = palette_color

        return nearest

    @classmethod
    def reduce_colors(cls, image: Image.Image, palette: list = None) -> Image.Image:
        """
        Reduce image to limited color palette.

        Uses numpy for fast vectorized color matching (100x faster than pixel-by-pixel).

        Args:
            image: PIL Image to reduce
            palette: List of RGB tuples (defaults to RETRO_PALETTE)

        Returns:
            Image with reduced color palette
        """
        if palette is None:
            palette = cls.RETRO_PALETTE

        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Try numpy for fast processing
        try:
            import numpy as np

            # Convert image to numpy array
            img_array = np.array(image, dtype=np.float32)
            palette_array = np.array(palette, dtype=np.float32)

            # Reshape for broadcasting: (H, W, 1, 3) vs (1, 1, P, 3)
            img_reshaped = img_array.reshape(img_array.shape[0], img_array.shape[1], 1, 3)
            palette_reshaped = palette_array.reshape(1, 1, len(palette), 3)

            # Calculate squared distances to all palette colors
            distances = np.sum((img_reshaped - palette_reshaped) ** 2, axis=3)

            # Find index of nearest palette color for each pixel
            nearest_indices = np.argmin(distances, axis=2)

            # Map indices to colors
            result_array = palette_array[nearest_indices].astype(np.uint8)

            return Image.fromarray(result_array, mode="RGB")

        except ImportError:
            # Fallback to slow pixel-by-pixel method
            result = Image.new("RGB", image.size)
            pixels = image.load()
            result_pixels = result.load()

            for y in range(image.height):
                for x in range(image.width):
                    original_color = pixels[x, y]
                    nearest_color = cls._find_nearest_color(original_color, palette)
                    result_pixels[x, y] = nearest_color

            return result

    @classmethod
    def reduce_colors_smooth(cls, image: Image.Image, num_colors: int = 32) -> Image.Image:
        """
        Reduce colors using PIL's quantize for smoother results.

        Args:
            image: PIL Image to reduce
            num_colors: Number of colors to reduce to

        Returns:
            Image with reduced color palette
        """
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Use PIL's built-in quantization for better results
        quantized = image.quantize(colors=num_colors, method=Image.MEDIANCUT)
        return quantized.convert("RGB")

    @staticmethod
    def add_scanlines(image: Image.Image, opacity: int = 40, spacing: int = 3) -> Image.Image:
        """
        Add CRT scanline effect.

        Args:
            image: PIL Image to add scanlines to
            opacity: Opacity of scanlines (0-255)
            spacing: Pixels between scanlines

        Returns:
            Image with scanline overlay
        """
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Create scanline overlay
        scanlines = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(scanlines)

        # Draw horizontal lines
        for y in range(0, image.height, spacing):
            draw.line([(0, y), (image.width, y)], fill=(0, 0, 0, opacity))

        return Image.alpha_composite(image, scanlines)

    @staticmethod
    def add_vignette(image: Image.Image, strength: float = 0.3) -> Image.Image:
        """
        Add subtle vignette effect (darker corners).

        Args:
            image: PIL Image
            strength: Vignette strength (0-1)

        Returns:
            Image with vignette
        """
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Create radial gradient for vignette
        width, height = image.size
        vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vignette)

        center_x, center_y = width // 2, height // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)

        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                # Vignette starts at 60% from center
                if dist > max_dist * 0.6:
                    alpha = int(((dist - max_dist * 0.6) / (max_dist * 0.4)) * 255 * strength)
                    alpha = min(255, alpha)
                    vignette.putpixel((x, y), (0, 0, 0, alpha))

        return Image.alpha_composite(image, vignette)

    @staticmethod
    def enhance_colors(
        image: Image.Image, saturation: float = 1.3, contrast: float = 1.1
    ) -> Image.Image:
        """
        Enhance colors for more vibrant retro look.

        Args:
            image: PIL Image
            saturation: Saturation multiplier (1.0 = no change)
            contrast: Contrast multiplier (1.0 = no change)

        Returns:
            Enhanced image
        """
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Boost saturation
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(saturation)

        # Boost contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)

        return image

    @staticmethod
    def add_purple_tint(image: Image.Image, strength: float = 0.15) -> Image.Image:
        """
        Add subtle purple tint to match Sonrai branding.

        Args:
            image: PIL Image
            strength: Tint strength (0-1)

        Returns:
            Tinted image
        """
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Create purple overlay
        purple = Image.new("RGB", image.size, (138, 43, 226))

        # Blend with original
        return Image.blend(image, purple, strength)

    @classmethod
    def apply_full_retro_effect(
        cls, image: Image.Image, pixel_size: int = 4, add_scanlines: bool = False
    ) -> Image.Image:
        """
        Apply complete 8-bit retro transformation (HEAVY - original behavior).

        Args:
            image: PIL Image to transform
            pixel_size: Size of pixel blocks
            add_scanlines: Whether to add CRT scanlines

        Returns:
            Fully transformed retro image
        """
        # Apply pixelation
        img = cls.pixelate(image, pixel_size=pixel_size)

        # Reduce to retro palette
        img = cls.reduce_colors(img, cls.RETRO_PALETTE)

        # Optionally add scanlines
        if add_scanlines:
            img = cls.add_scanlines(img)

        return img

    @classmethod
    def apply_light_retro_effect(
        cls, image: Image.Image, pixel_size: int = 3, num_colors: int = 64
    ) -> Image.Image:
        """
        Apply lighter retro effect that preserves more detail.
        Good for selfies where you want to recognize the person.

        Args:
            image: PIL Image to transform
            pixel_size: Size of pixel blocks (smaller = more detail)
            num_colors: Number of colors to keep

        Returns:
            Lightly retro-styled image
        """
        # Enhance colors first for vibrant look
        img = cls.enhance_colors(image, saturation=1.2, contrast=1.1)

        # Soft pixelation (preserves more detail)
        img = cls.soft_pixelate(img, pixel_size=pixel_size)

        # Reduce colors but keep more than 16
        img = cls.reduce_colors_smooth(img, num_colors=num_colors)

        # Add subtle purple tint for branding
        img = cls.add_purple_tint(img, strength=0.08)

        return img

    @classmethod
    def apply_medium_retro_effect(
        cls, image: Image.Image, pixel_size: int = 4, num_colors: int = 32
    ) -> Image.Image:
        """
        Apply medium retro effect - balance between retro and recognizable.

        Args:
            image: PIL Image to transform
            pixel_size: Size of pixel blocks
            num_colors: Number of colors to keep

        Returns:
            Medium retro-styled image
        """
        # Enhance colors
        img = cls.enhance_colors(image, saturation=1.3, contrast=1.15)

        # Medium pixelation
        img = cls.pixelate(img, pixel_size=pixel_size)

        # Reduce colors
        img = cls.reduce_colors_smooth(img, num_colors=num_colors)

        # Add purple tint
        img = cls.add_purple_tint(img, strength=0.1)

        return img

    @classmethod
    def apply_arcade_selfie_effect(cls, image: Image.Image) -> Image.Image:
        """
        Apply the recommended effect for arcade photo booth selfies.
        Balances retro aesthetic with recognizable features.

        Args:
            image: PIL Image (selfie from webcam)

        Returns:
            Arcade-styled selfie
        """
        # Use light effect for best balance
        img = cls.apply_light_retro_effect(image, pixel_size=3, num_colors=48)

        # Add very subtle scanlines for CRT feel
        img = cls.add_scanlines(img, opacity=20, spacing=4)

        return img

    @staticmethod
    def remove_background(image: Image.Image) -> Image.Image:
        """
        Remove background from selfie image using AI segmentation.

        Args:
            image: PIL Image (selfie)

        Returns:
            RGBA image with transparent background, or original if rembg unavailable
        """
        if not REMBG_AVAILABLE:
            logger.warning("📸 Background removal not available - rembg not installed")
            return image

        logger.info("📸 Removing selfie background...")
        try:
            # rembg returns RGBA with transparent background
            result = remove_bg(image)
            logger.info("📸 Background removed successfully")
            return result
        except Exception as e:
            logger.error(f"📸 Background removal failed: {e}")
            return image

    @staticmethod
    def add_game_background(image: Image.Image, bg_color: tuple = (40, 20, 60)) -> Image.Image:
        """
        Add solid game-themed background to transparent image.

        Args:
            image: RGBA image with transparent background
            bg_color: RGB tuple for background color (default: dark purple)

        Returns:
            RGB image with solid background
        """
        if image.mode != "RGBA":
            return image

        # Create background
        bg = Image.new("RGBA", image.size, (*bg_color, 255))
        # Composite the person on top
        bg.paste(image, (0, 0), image)
        return bg.convert("RGB")

    @classmethod
    def apply_video_game_character_effect(
        cls, image: Image.Image, pixel_size: int = 5, do_remove_bg: bool = False
    ) -> Image.Image:
        """
        Apply heavy video game character transformation.

        Creates an authentic 8-bit/16-bit video game character look with:
        - Optional background removal (SLOW - disabled by default)
        - Heavy pixelation for blocky retro look
        - Limited 32-color palette optimized for skin tones
        - Game-themed purple background

        Args:
            image: PIL Image (selfie from webcam)
            pixel_size: Pixel block size (5 = chunky retro, 4 = more detail)
            do_remove_bg: Whether to remove background (SLOW - 10+ seconds!)

        Returns:
            Video game character styled image
        """
        logger.info(
            f"📸 Applying video game character effect (pixel_size={pixel_size}, remove_bg={do_remove_bg})"
        )

        if do_remove_bg:
            # Step 1: Remove background (SLOW!)
            img_nobg = cls.remove_background(image)
            # Step 2: Add game-themed purple background
            img_with_bg = cls.add_game_background(img_nobg, bg_color=(40, 20, 60))
        else:
            # Skip background removal - just use original image
            img_with_bg = image

        # Step 3: Apply heavier pixelation for authentic retro look
        img_pixelated = cls.pixelate(img_with_bg, pixel_size=pixel_size)

        # Step 4: Reduce to video game palette (32 colors with good skin tones)
        img_final = cls.reduce_colors(img_pixelated, cls.VIDEO_GAME_PALETTE)

        logger.info("📸 Video game character effect applied")
        return img_final

    @classmethod
    def apply_enhanced_arcade_effect(
        cls, image: Image.Image, do_remove_bg: bool = False
    ) -> Image.Image:
        """
        Apply enhanced arcade photo booth effect.

        This is the RECOMMENDED effect for the photo booth - creates an
        authentic video game character look while keeping the person recognizable.

        Args:
            image: PIL Image (selfie from webcam)
            do_remove_bg: Whether to remove background (SLOW - disabled by default)

        Returns:
            Arcade-styled selfie that looks like a video game character
        """
        # Apply the full video game character transformation
        # Background removal is disabled by default for speed
        img = cls.apply_video_game_character_effect(image, pixel_size=5, do_remove_bg=do_remove_bg)

        # Add subtle scanlines for CRT arcade feel
        img = cls.add_scanlines(img, opacity=25, spacing=4)

        return img
