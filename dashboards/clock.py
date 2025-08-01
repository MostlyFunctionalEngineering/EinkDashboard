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
        bg_path = clock_cfg.get('background')  # None means no background
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

        # Paste background if provided
        if bg_path and os.path.exists(bg_path):
            background = Image.open(bg_path).convert('1').resize((height, width))
            black_img.paste(background, (0, 0))

        draw_black = ImageDraw.Draw(black_img)

        time_w, time_h = time_font.getmask(time_str).size

        if show_date:
            date_w, date_h = date_font.getmask(date_str).size
            total_height = time_h + spacing + date_h
            top_margin = (width - total_height) // 2

            time_x = (height - time_w) // 2
            time_y = top_margin

            date_x = (height - date_w) // 2
            date_y = top_margin + time_h + spacing

            draw_black.text((time_x, time_y), time_str, font=time_font, fill=text_color)
            draw_black.text((date_x, date_y), date_str, font=date_font, fill=text_color)
        else:
            time_x = (height - time_w) // 2
            time_y = (width - time_h) // 2
            draw_black.text((time_x, time_y), time_str, font=time_font, fill=text_color)

        logger.debug("Sending image to display")
        epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))
        logger.debug("Clock dashboard rendered")

    except Exception as e:
        logger.exception(f"Clock rendering failed: {e}")
