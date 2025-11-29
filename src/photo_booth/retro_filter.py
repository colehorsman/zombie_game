"""
Retro 8-bit filter effects for photo booth selfies.

Applies pixelation, color reduction, and CRT scanline effects
to create an authentic retro gaming aesthetic.
"""

import math

from PIL import Image, ImageDraw


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

        # Create new image with reduced colors
        result = Image.new("RGB", image.size)
        pixels = image.load()
        result_pixels = result.load()

        for y in range(image.height):
            for x in range(image.width):
                original_color = pixels[x, y]
                nearest_color = cls._find_nearest_color(original_color, palette)
                result_pixels[x, y] = nearest_color

        return result

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

    @classmethod
    def apply_full_retro_effect(
        cls, image: Image.Image, pixel_size: int = 4, add_scanlines: bool = False
    ) -> Image.Image:
        """
        Apply complete 8-bit retro transformation.

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
