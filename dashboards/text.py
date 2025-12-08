from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import logging

logger = logging.getLogger(__name__)

def render(epd, config):
    logger.debug("Rendering text dashboard")

    try:
        height, width = epd.height, epd.width

        # Load config block
        text_cfg = config.get('text', {})
        if not text_cfg.get('enabled', False):
            logger.debug("Text dashboard disabled — skipping render")
            return

        message = text_cfg.get('text', "")
        font_path = text_cfg.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
        font_size = text_cfg.get('font_size', 40)
        spacing = text_cfg.get('vertical_spacing', 10)
        invert = text_cfg.get('invert_colors', False)
        bg_path = text_cfg.get('background')

        # Colors
        background_color = 0 if invert else 255
        text_color = 255 if invert else 0

        # Base layers
        black_img = Image.new('1', (height, width), background_color)
        red_img = Image.new('1', (height, width), 255)

        # Optional background image
        if bg_path and os.path.exists(bg_path):
            try:
                background = Image.open(bg_path).convert('L').resize((height, width))
                if invert:
                    background = ImageOps.invert(background)
                background = background.convert('1')
                black_img.paste(background)
                logger.debug(f"Pasted background: {bg_path}")
            except Exception as e:
                logger.warning(f"Failed to load background {bg_path}: {e}")

        # Load font
        font = ImageFont.truetype(font_path, font_size)

        # Render text to layer
        text_layer = Image.new('L', (height, width), 255)
        draw = ImageDraw.Draw(text_layer)

        # Measure text
        text_w, text_h = font.getmask(message).size
        text_x = (height - text_w) // 2
        text_y = (width - text_h) // 2

        # Draw text
        draw.text((text_x, text_y), message, font=font, fill=0)

        # Convert grayscale to mask
        mask = text_layer.point(lambda p: 255 if p < 128 else 0, mode='1')

        # Apply mask to base image
        black_img.paste(Image.new('1', (height, width), text_color), (0, 0), mask)

        logger.debug("Sending text dashboard to display")
        epd.display_fast(epd.getbuffer(black_img))
        logger.debug("Text dashboard rendered")

    except Exception as e:
        logger.exception(f"Text dashboard failed: {e}")