"""
Photo Booth Compositor.

Generates the final composite image with selfie, gameplay screenshot,
score, branding, and retro arcade frame.
"""

import os
from datetime import datetime
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from .config import PhotoBoothConfig
from .retro_filter import RetroFilter


class PhotoBoothCompositor:
    """Generates the final photo booth composite image."""

    # Output dimensions (1080p for social sharing)
    OUTPUT_WIDTH = 1920
    OUTPUT_HEIGHT = 1080

    # Layout constants
    FRAME_BORDER = 40
    PHOTO_GAP = 20
    SCORE_HEIGHT = 120
    FOOTER_HEIGHT = 100

    # Colors
    BG_COLOR = (20, 10, 30)  # Dark purple
    PANEL_BG = (40, 20, 60)  # Lighter purple
    SCORE_COLOR = (255, 215, 0)  # Gold
    TEXT_COLOR = (255, 255, 255)  # White
    ACCENT_COLOR = (138, 43, 226)  # Purple

    def __init__(self):
        self.frame_overlay = self._load_frame_overlay()
        self.sonrai_logo = self._load_sonrai_logo()
        self.qr_code = self._load_qr_code()
        self.pixel_font_large = self._load_font(48)
        self.pixel_font_medium = self._load_font(32)
        self.pixel_font_small = self._load_font(20)

    def generate(
        self,
        selfie: Optional[Image.Image],
        gameplay: Image.Image,
        zombie_count: int,
        config: PhotoBoothConfig,
        skip_selfie_retro: bool = False,
    ) -> Image.Image:
        """
        Generate complete photo booth composite.

        Args:
            selfie: Pixelated selfie image (or None if not opted in)
            gameplay: Gameplay screenshot
            zombie_count: Number of zombies eliminated
            config: Photo booth configuration
            skip_selfie_retro: If True, skip applying retro filter to selfie (already processed)

        Returns:
            Complete composite image (1920x1080)
        """
        # Create base canvas
        canvas = Image.new("RGB", (self.OUTPUT_WIDTH, self.OUTPUT_HEIGHT), self.BG_COLOR)

        # Calculate content area
        content_top = self.FRAME_BORDER + self.SCORE_HEIGHT
        content_bottom = self.OUTPUT_HEIGHT - self.FRAME_BORDER - self.FOOTER_HEIGHT
        content_height = content_bottom - content_top

        # Create and place panels
        if selfie:
            # Two-panel layout
            panel_width = (self.OUTPUT_WIDTH - self.FRAME_BORDER * 2 - self.PHOTO_GAP) // 2

            selfie_panel = self._create_selfie_panel(
                selfie, panel_width, content_height, skip_selfie_retro
            )
            gameplay_panel = self._create_gameplay_panel(gameplay, panel_width, content_height)

            canvas.paste(selfie_panel, (self.FRAME_BORDER, content_top))
            canvas.paste(
                gameplay_panel, (self.FRAME_BORDER + panel_width + self.PHOTO_GAP, content_top)
            )
        else:
            # Single panel - gameplay fills center
            panel_width = self.OUTPUT_WIDTH - self.FRAME_BORDER * 2
            gameplay_panel = self._create_gameplay_panel(gameplay, panel_width, content_height)
            canvas.paste(gameplay_panel, (self.FRAME_BORDER, content_top))

        # Draw score header
        self._draw_score_header(canvas, zombie_count)

        # Draw footer with branding
        self._draw_footer(canvas, config)

        # Draw decorative border
        self._draw_arcade_border(canvas)

        # Apply frame overlay if available
        if self.frame_overlay:
            canvas = self._apply_overlay(canvas, self.frame_overlay)

        # Apply subtle scanlines to entire image
        canvas = RetroFilter.add_scanlines(canvas, opacity=25, spacing=4)

        return canvas.convert("RGB")

    def save(self, composite: Image.Image, config: PhotoBoothConfig) -> str:
        """
        Save composite to file.

        Args:
            composite: Composite image to save
            config: Configuration with output directory

        Returns:
            Path to saved file
        """
        # Ensure output directory exists
        os.makedirs(config.output_dir, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"BOOTH_{timestamp}.png"
        filepath = os.path.join(config.output_dir, filename)

        # Save as PNG
        composite.save(filepath, "PNG")

        return filepath

    def _create_selfie_panel(
        self, selfie: Image.Image, panel_width: int, panel_height: int, skip_retro: bool = False
    ) -> Image.Image:
        """Create the pixelated selfie panel."""
        # Apply arcade selfie effect unless already processed
        if skip_retro:
            retro_selfie = selfie
        else:
            retro_selfie = RetroFilter.apply_arcade_selfie_effect(selfie)

        # Create panel background
        panel = Image.new("RGB", (panel_width, panel_height), self.PANEL_BG)

        # Resize selfie to fit panel while maintaining aspect ratio
        selfie_ratio = retro_selfie.width / retro_selfie.height
        panel_ratio = panel_width / panel_height

        if selfie_ratio > panel_ratio:
            # Selfie is wider - fit to width
            new_width = panel_width - 20
            new_height = int(new_width / selfie_ratio)
        else:
            # Selfie is taller - fit to height
            new_height = panel_height - 20
            new_width = int(new_height * selfie_ratio)

        retro_selfie = retro_selfie.resize((new_width, new_height), Image.NEAREST)

        # Center in panel
        x_offset = (panel_width - new_width) // 2
        y_offset = (panel_height - new_height) // 2
        panel.paste(retro_selfie, (x_offset, y_offset))

        # Add border
        self._draw_panel_border(panel)

        return panel

    def _create_gameplay_panel(
        self, gameplay: Image.Image, panel_width: int, panel_height: int
    ) -> Image.Image:
        """Create the gameplay screenshot panel."""
        # Create panel background
        panel = Image.new("RGB", (panel_width, panel_height), self.PANEL_BG)

        # Resize gameplay to fit panel while maintaining aspect ratio
        gameplay_ratio = gameplay.width / gameplay.height
        panel_ratio = panel_width / panel_height

        if gameplay_ratio > panel_ratio:
            new_width = panel_width - 20
            new_height = int(new_width / gameplay_ratio)
        else:
            new_height = panel_height - 20
            new_width = int(new_height * gameplay_ratio)

        gameplay_resized = gameplay.resize((new_width, new_height), Image.LANCZOS)

        # Center in panel
        x_offset = (panel_width - new_width) // 2
        y_offset = (panel_height - new_height) // 2
        panel.paste(gameplay_resized, (x_offset, y_offset))

        # Add border
        self._draw_panel_border(panel)

        return panel

    def _draw_panel_border(self, panel: Image.Image) -> None:
        """Draw decorative border around panel."""
        draw = ImageDraw.Draw(panel)
        # Outer border
        draw.rectangle(
            [(0, 0), (panel.width - 1, panel.height - 1)], outline=self.ACCENT_COLOR, width=3
        )
        # Inner highlight
        draw.rectangle(
            [(4, 4), (panel.width - 5, panel.height - 5)], outline=(80, 40, 100), width=1
        )

    def _draw_score_header(self, canvas: Image.Image, zombie_count: int) -> None:
        """Draw the score header with zombie icons and zombie count."""
        draw = ImageDraw.Draw(canvas)

        # Score text (without stars - we'll add zombie icons)
        score_text = f"{zombie_count} ZOMBIES ELIMINATED"
        subtitle = "60 SECOND CHALLENGE"

        # Calculate text dimensions
        score_bbox = draw.textbbox((0, 0), score_text, font=self.pixel_font_large)
        score_width = score_bbox[2] - score_bbox[0]
        score_height = score_bbox[3] - score_bbox[1]

        # Zombie icon size (match text height)
        icon_size = 40
        icon_spacing = 15
        num_icons = 3  # 3 zombies on each side

        # Total width including icons
        icons_width = (num_icons * icon_size + (num_icons - 1) * 5) * 2  # Both sides
        total_width = icons_width + score_width + icon_spacing * 2

        # Starting X position to center everything
        start_x = (self.OUTPUT_WIDTH - total_width) // 2
        text_y = self.FRAME_BORDER + 15
        icon_y = text_y + (score_height - icon_size) // 2 + 5

        # Draw left zombie icons
        x = start_x
        for i in range(num_icons):
            self._draw_zombie_icon(canvas, x, icon_y, icon_size)
            x += icon_size + 5

        # Draw score text (gold color)
        text_x = x + icon_spacing
        draw.text(
            (text_x, text_y),
            score_text,
            fill=self.SCORE_COLOR,
            font=self.pixel_font_large,
        )

        # Draw right zombie icons
        x = text_x + score_width + icon_spacing
        for i in range(num_icons):
            self._draw_zombie_icon(canvas, x, icon_y, icon_size)
            x += icon_size + 5

        # Draw subtitle (white)
        sub_bbox = draw.textbbox((0, 0), subtitle, font=self.pixel_font_medium)
        sub_width = sub_bbox[2] - sub_bbox[0]
        x = (self.OUTPUT_WIDTH - sub_width) // 2
        draw.text(
            (x, self.FRAME_BORDER + 70), subtitle, fill=self.TEXT_COLOR, font=self.pixel_font_medium
        )

    def _draw_zombie_icon(self, canvas: Image.Image, x: int, y: int, size: int) -> None:
        """Draw a pixel art zombie icon."""
        draw = ImageDraw.Draw(canvas)

        # Scale factor for the icon
        s = size // 10  # Base unit

        # Zombie colors
        body_color = (0, 180, 0)  # Green body
        head_color = (0, 200, 0)  # Lighter green head
        eye_color = (255, 0, 0)  # Red eyes
        dark_green = (0, 140, 0)  # Darker green for details

        # Head (top portion)
        head_x = x + s * 2
        head_y = y
        head_w = s * 6
        head_h = s * 4
        draw.rectangle([(head_x, head_y), (head_x + head_w, head_y + head_h)], fill=head_color)

        # Eyes (red, menacing)
        eye_size = s * 2
        # Left eye
        draw.rectangle(
            [(head_x + s, head_y + s), (head_x + s + eye_size, head_y + s + eye_size)],
            fill=eye_color,
        )
        # Right eye
        draw.rectangle(
            [
                (head_x + head_w - s - eye_size, head_y + s),
                (head_x + head_w - s, head_y + s + eye_size),
            ],
            fill=eye_color,
        )

        # Body (middle portion)
        body_x = x + s * 2
        body_y = y + s * 4
        body_w = s * 6
        body_h = s * 4
        draw.rectangle([(body_x, body_y), (body_x + body_w, body_y + body_h)], fill=body_color)

        # Arms (reaching out - zombie style)
        arm_h = s * 2
        # Left arm (extended)
        draw.rectangle([(x, body_y + s), (body_x, body_y + s + arm_h)], fill=dark_green)
        # Right arm (extended)
        draw.rectangle(
            [(body_x + body_w, body_y + s), (x + size, body_y + s + arm_h)], fill=dark_green
        )

        # Legs
        leg_y = body_y + body_h
        leg_w = s * 2
        leg_h = s * 2
        # Left leg
        draw.rectangle([(body_x + s, leg_y), (body_x + s + leg_w, leg_y + leg_h)], fill=dark_green)
        # Right leg
        draw.rectangle(
            [(body_x + body_w - s - leg_w, leg_y), (body_x + body_w - s, leg_y + leg_h)],
            fill=dark_green,
        )

    def _draw_footer(self, canvas: Image.Image, config: PhotoBoothConfig) -> None:
        """Draw footer with branding and event info."""
        draw = ImageDraw.Draw(canvas)

        footer_y = self.OUTPUT_HEIGHT - self.FOOTER_HEIGHT - self.FRAME_BORDER + 10

        # Left side: Sonrai logo
        if self.sonrai_logo:
            logo_height = self.FOOTER_HEIGHT - 30
            logo_ratio = self.sonrai_logo.width / self.sonrai_logo.height
            logo_width = int(logo_height * logo_ratio)
            logo_resized = self.sonrai_logo.resize((logo_width, logo_height), Image.LANCZOS)

            # Handle transparency
            if logo_resized.mode == "RGBA":
                canvas.paste(logo_resized, (self.FRAME_BORDER + 10, footer_y + 5), logo_resized)
            else:
                canvas.paste(logo_resized, (self.FRAME_BORDER + 10, footer_y + 5))

        # Center: Event info and hashtag
        event_text = f"{config.event_name}  |  Booth #{config.booth_number}"
        hashtag_text = config.hashtag

        event_bbox = draw.textbbox((0, 0), event_text, font=self.pixel_font_small)
        event_width = event_bbox[2] - event_bbox[0]
        x = (self.OUTPUT_WIDTH - event_width) // 2
        draw.text((x, footer_y + 15), event_text, fill=(200, 200, 200), font=self.pixel_font_small)

        hashtag_bbox = draw.textbbox((0, 0), hashtag_text, font=self.pixel_font_small)
        hashtag_width = hashtag_bbox[2] - hashtag_bbox[0]
        x = (self.OUTPUT_WIDTH - hashtag_width) // 2
        draw.text(
            (x, footer_y + 45), hashtag_text, fill=self.ACCENT_COLOR, font=self.pixel_font_small
        )

        # Right side: QR code
        qr_size = self.FOOTER_HEIGHT - 30
        qr_x = self.OUTPUT_WIDTH - self.FRAME_BORDER - qr_size - 10

        if self.qr_code:
            # Use actual QR code image
            qr_resized = self.qr_code.resize((qr_size, qr_size), Image.LANCZOS)
            # Handle transparency if present
            if qr_resized.mode == "RGBA":
                canvas.paste(qr_resized, (qr_x, footer_y + 5), qr_resized)
            else:
                canvas.paste(qr_resized, (qr_x, footer_y + 5))
        else:
            # Fallback: white placeholder with text
            draw.rectangle(
                [(qr_x, footer_y + 5), (qr_x + qr_size, footer_y + 5 + qr_size)],
                fill=(255, 255, 255),
            )
            draw.text(
                (qr_x + 15, footer_y + qr_size // 2),
                "QR",
                fill=(0, 0, 0),
                font=self.pixel_font_small,
            )

    def _draw_arcade_border(self, canvas: Image.Image) -> None:
        """Draw decorative arcade cabinet border."""
        draw = ImageDraw.Draw(canvas)

        # Outer border
        draw.rectangle(
            [(10, 10), (self.OUTPUT_WIDTH - 11, self.OUTPUT_HEIGHT - 11)],
            outline=self.ACCENT_COLOR,
            width=4,
        )

        # Corner decorations (pixel art style)
        corner_size = 20
        for x, y in [
            (15, 15),
            (self.OUTPUT_WIDTH - 35, 15),
            (15, self.OUTPUT_HEIGHT - 35),
            (self.OUTPUT_WIDTH - 35, self.OUTPUT_HEIGHT - 35),
        ]:
            draw.rectangle([(x, y), (x + corner_size, y + corner_size)], fill=self.ACCENT_COLOR)

        # "INSERT COIN" text at bottom
        insert_coin = "INSERT COIN TO CONTINUE"
        coin_bbox = draw.textbbox((0, 0), insert_coin, font=self.pixel_font_small)
        coin_width = coin_bbox[2] - coin_bbox[0]
        x = (self.OUTPUT_WIDTH - coin_width) // 2
        draw.text(
            (x, self.OUTPUT_HEIGHT - 35),
            insert_coin,
            fill=(100, 100, 100),
            font=self.pixel_font_small,
        )

    def _apply_overlay(self, canvas: Image.Image, overlay: Image.Image) -> Image.Image:
        """Apply transparent overlay to canvas."""
        if canvas.mode != "RGBA":
            canvas = canvas.convert("RGBA")

        # Resize overlay to match canvas if needed
        if overlay.size != canvas.size:
            overlay = overlay.resize(canvas.size, Image.LANCZOS)

        return Image.alpha_composite(canvas, overlay)

    def _load_frame_overlay(self) -> Optional[Image.Image]:
        """Load the arcade frame overlay asset."""
        try:
            return Image.open("assets/photo_booth_frame.png").convert("RGBA")
        except FileNotFoundError:
            return None
        except Exception:
            return None

    def _load_sonrai_logo(self) -> Optional[Image.Image]:
        """Load the Sonrai logo."""
        # Try stacked logo first
        try:
            return Image.open("assets/Sonrai logo_stacked_purple-black.png").convert("RGBA")
        except FileNotFoundError:
            pass
        except Exception:
            pass

        # Fallback to regular logo
        try:
            return Image.open("assets/sonrai_logo.png").convert("RGBA")
        except FileNotFoundError:
            return None
        except Exception:
            return None

    def _load_qr_code(self) -> Optional[Image.Image]:
        """Load the QR code image."""
        try:
            return Image.open("assets/qr.png").convert("RGBA")
        except FileNotFoundError:
            return None
        except Exception:
            return None

    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Load pixel font or fallback to default."""
        # Try pixel font first
        font_paths = [
            "assets/fonts/pixel.ttf",
            "assets/fonts/PressStart2P.ttf",
            "/System/Library/Fonts/Monaco.ttf",  # macOS monospace
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
        ]

        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except (FileNotFoundError, OSError):
                continue

        # Fallback to default
        try:
            return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()
