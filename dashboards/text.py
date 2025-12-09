from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import logging

logger = logging.getLogger(__name__)

def render(epd, config, flip_screen=false):
    logger.debug("Rendering text dashboard")

    try:
        height, width = epd.height, epd.width

        # Load config
        text_cfg = config.get('text', {})
        message = text_cfg.get('text', "")
        font_path = text_cfg.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
        font_size = text_cfg.get('font_size', 40)
        spacing = text_cfg.get('vertical_spacing', 10)
        invert = text_cfg.get('invert_colors', False)
        bg_path = text_cfg.get('background')
        align = text_cfg.get('align', 'center').lower()  # default center

        if align not in ['left', 'center', 'right']:
            logger.warning(f"Invalid align value '{align}', defaulting to 'center'")
            align = 'center'

        # Colors
        background_color = 0 if invert else 255
        text_color = 255 if invert else 0

        # Base layers
        black_img = Image.new('1', (height, width), background_color)

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

        # Render multi-line text
        lines = message.splitlines() or [""]  # fallback to one empty line
        line_sizes = [font.getmask(line).size for line in lines]
        total_height = sum(h for _, h in line_sizes) + spacing * (len(lines) - 1)
        top_y = (width - total_height) // 2

        text_layer = Image.new('L', (height, width), 255)
        draw = ImageDraw.Draw(text_layer)

        current_y = top_y
        for (line, (line_w, line_h)) in zip(lines, line_sizes):
            if align == 'left':
                x = 0
            elif align == 'right':
                x = height - line_w
            else:  # center
                x = (height - line_w) // 2

            draw.text((x, current_y), line, font=font, fill=0)
            current_y += line_h + spacing

        # Convert grayscale to mask
        mask = text_layer.point(lambda p: 255 if p < 128 else 0, mode='1')

        # Apply mask to base image
        black_img.paste(Image.new('1', (height, width), text_color), (0, 0), mask)

        if invert:
            blac_img = Image.eval(black_img, lambda px: 255 - px)

        logger.debug("Sending text dashboard to display")
        if flip_screen:
            image = image.rotate(180)  # flip upside-down
        epd.display_fast(epd.getbuffer(black_img))
        logger.debug("Text dashboard rendered")

    except Exception as e:
        logger.exception(f"Text dashboard failed: {e}")