from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)

def render(epd, config):
    logger.debug("Rendering clock dashboard")
    
    try:
        logger.debug("Clearing screen")
        epd.Clear()
        logger.debug("Screen cleared")

        width, height = epd.width, epd.height

        # Load config
        clock_cfg = config.get('clock', {})
        font_path = clock_cfg.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
        font_size = clock_cfg.get('font_size', 20)
        use_24hr = clock_cfg.get('use_24hr', False)
        show_date = clock_cfg.get('show_date', False)

        # Time format
        now = datetime.now()
        time_str = now.strftime('%H:%M' if use_24hr else '%I:%M').lstrip('0')
        date_str = now.strftime('%Y-%m-%d') if show_date else None

        logger.debug(f"Time: {time_str}, Date: {date_str if show_date else 'N/A'}")

        # Load font
        font = ImageFont.truetype(font_path, font_size)

        # Dummy image to measure text
        dummy_img = Image.new('1', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)

        # Create display image
        black_img = Image.new('1', (width, height), 255)
        draw_black = ImageDraw.Draw(black_img)

        # Draw time
        time_w, time_h = dummy_draw.textsize(time_str, font=font)
        time_x = (width - time_w) // 2
        time_y = (height // 2 - time_h) if not show_date else (height // 3 - time_h // 2)
        draw_black.text((time_x, time_y), time_str, font=font, fill=0)

        # Draw date if enabled
        if date_str:
            date_w, date_h = dummy_draw.textsize(date_str, font=font)
            date_x = (width - date_w) // 2
            date_y = (2 * height // 3 - date_h // 2)
            draw_black.text((date_x, date_y), date_str, font=font, fill=0)
        
        logger.debug("Image generated, displaying to screen...")
        epd.display(epd.getbuffer(black_img), epd.getbuffer(Image.new('1', (width, height), 255)))
        logger.debug("Image displayed! Setting to sleep")
        epd.sleep()
        logger.debug("Clock dashboard rendered successfully, and screen set to sleep")

    except Exception as e:
        logger.exception(f"Clock rendering failed: {e}")
