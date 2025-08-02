from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import logging

logger = logging.getLogger(__name__)

def render(epd, config):
    logger.debug("Rendering clock dashboard")

    try:
        height, width = epd.height, epd.width

        clock_cfg = config.get('clock', {})
        bg_path = clock_cfg.get('background')  # e.g. assets/Borders_and_Logos/250x122_*.bmp
        font_path = clock_cfg.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
        time_font_size = clock_cfg.get('font_size', 40)
        date_font_size = clock_cfg.get('date_font_size', 20)
        use_24hr = clock_cfg.get('use_24hr', False)
        show_date = clock_cfg.get('show_date', False)
        date_format = clock_cfg.get('date_format', '%Y-%m-%d')
        spacing = clock_cfg.get('vertical_spacing', 5)
        invert = clock_cfg.get('invert_colors', False)

        now = datetime.now()
        time_str = now.strftime('%H:%M' if use_24hr else '%I:%M').lstrip('0')
        date_str = now.strftime(date_format) if show_date else None

        logger.debug(f"Time: {time_str}, Date: {date_str if show_date else 'N/A'}")

        time_font = ImageFont.truetype(font_path, time_font_size)
        date_font = ImageFont.truetype(font_path, date_font_size) if show_date else None

        background_color = 0 if invert else 255
        text_color = 255 if invert else 0

        black_img = Image.new('1', (height, width), background_color)
        red_img = Image.new('1', (height, width), 255)

        # Paste background image if present
        if bg_path and os.path.exists(bg_path):
            try:
                background = Image.open(bg_path).convert('L').resize((height, width))
                if invert:
                    background = ImageOps.invert(background)
                background = background.convert('1')
                black_img.paste(background)
                logger.debug(f"Pasted background from {bg_path}")
            except Exception as e:
                logger.warning(f"Failed to load background {bg_path}: {e}")

        # Draw text onto grayscale layer for masking
        text_layer = Image.new('L', (height, width), 255)  # white background
        draw_text = ImageDraw.Draw(text_layer)

        time_w, time_h = time_font.getmask(time_str).size

        if show_date:
            date_w, date_h = date_font.getmask(date_str).size
            total_height = time_h + spacing + date_h
            top_margin = (width - total_height) // 2

            time_x = (height - time_w) // 2
            time_y = top_margin

            date_x = (height - date_w) // 2
            date_y = top_margin + time_h + spacing

            draw_text.text((time_x, time_y), time_str, font=time_font, fill=0)
            draw_text.text((date_x, date_y), date_str, font=date_font, fill=0)
        else:
            time_x = (height - time_w) // 2
            time_y = (width - time_h) // 2
            draw_text.text((time_x, time_y), time_str, font=time_font, fill=0)

        # Convert grayscale to binary mask: black text becomes white mask
        mask = text_layer.point(lambda p: 255 if p < 128 else 0, mode='1')

        # Always paste black text for visibility, regardless of inversion
        text_color = 255 if invert else 0
        black_img.paste(Image.new('1', (height, width), text_color), (0, 0), mask)

        logger.debug("Sending image to display")
        epd.display_fast(epd.getbuffer(black_img))
        logger.debug("Clock dashboard rendered")

    except Exception as e:
        logger.exception(f"Clock rendering failed: {e}")
