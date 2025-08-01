from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import logging

logger = logging.getLogger(__name__)

def render(epd, config):
    logger.debug("Rendering clock dashboard")

    try:
        width, height = epd.width, epd.height  # Should be 250x122

        clock_cfg = config.get('clock', {})
        bg_path = clock_cfg.get('background')  # e.g., 'assets/Borders_and_Logos/250x122_*.bmp'
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

        white = 255 if not invert else 0
        black = 0 if not invert else 255

        # Create blank canvas
        black_img = Image.new('1', (width, height), white)
        red_img = Image.new('1', (width, height), 255)

        # Paste background if available
        if bg_path and os.path.exists(bg_path):
            try:
                background = Image.open(bg_path).convert('1').resize((width, height))
                black_img.paste(background)
                logger.debug(f"Pasted background: {bg_path}")
            except Exception as e:
                logger.warning(f"Failed to load background: {e}")

        draw = ImageDraw.Draw(black_img)

        # Calculate positions
        time_w, time_h = time_font.getmask(time_str).size
        if show_date:
            date_w, date_h = date_font.getmask(date_str).size
            total_height = time_h + spacing + date_h
            top = (height - total_height) // 2

            time_x = (width - time_w) // 2
            time_y = top

            date_x = (width - date_w) // 2
            date_y = top + time_h + spacing

            draw.text((time_x, time_y), time_str, font=time_font, fill=black)
            draw.text((date_x, date_y), date_str, font=date_font, fill=black)
        else:
            time_x = (width - time_w) // 2
            time_y = (height - time_h) // 2
            draw.text((time_x, time_y), time_str, font=time_font, fill=black)

        logger.debug("Sending image to display")
        epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))
        logger.debug("Clock dashboard rendered")

    except Exception as e:
        logger.exception(f"Clock rendering failed: {e}")
