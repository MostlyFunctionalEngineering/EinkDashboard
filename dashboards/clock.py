from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)

def render(epd, config):
    logger.debug("Rendering clock dashboard")

    try:
        height, width = epd.height, epd.width  # 250 x 122 for 2.13" v4

        clock_cfg = config.get('clock', {})
        font_path = clock_cfg.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
        font_size = clock_cfg.get('font_size', 20)
        use_24hr = clock_cfg.get('use_24hr', False)
        show_date = clock_cfg.get('show_date', False)

        now = datetime.now()
        time_str = now.strftime('%H:%M' if use_24hr else '%I:%M').lstrip('0')
        date_str = now.strftime('%Y-%m-%d') if show_date else None

        logger.debug(f"Time: {time_str}, Date: {date_str if show_date else 'N/A'}")

        font = ImageFont.truetype(font_path, font_size)

        # Match demo dimensions: black and red image as (epd.height, epd.width)
        black_img = Image.new('1', (height, width), 255)
        red_img = Image.new('1', (height, width), 255)  # Not used, but required by API

        draw_black = ImageDraw.Draw(black_img)

        # Draw text at fixed position for now
        draw_black.text((10, 20), time_str, font=font, fill=0)
        if date_str:
            draw_black.text((10, 60), date_str, font=font, fill=0)

        logger.debug("Image generated, sending to display...")

        epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))

        logger.debug("Clock dashboard rendered")

    except Exception as e:
        logger.exception(f"Clock rendering failed: {e}")
