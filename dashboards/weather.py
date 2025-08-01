from PIL import Image, ImageDraw, ImageFont
import os
import logging

logger = logging.getLogger(__name__)

def render(epd, config):
    logger.debug("Rendering weather dashboard")

    try:
        # Dimensions
        height, width = epd.height, epd.width

        # Config
        weather_cfg = config.get('weather', {})
        font_path = weather_cfg.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
        font_size = weather_cfg.get('font_size', 24)
        invert = weather_cfg.get('invert_colors', False)

        # Sample data
        temperature = "23°C"
        icon_path = "assets/64x64_Weather_Icons/cloudy.bmp"

        # Load font
        font = ImageFont.truetype(font_path, font_size)

        # Create buffers (match driver expectations: (height, width))
        white = 255 if not invert else 0
        black = 0 if not invert else 255

        black_img = Image.new('1', (height, width), white)
        red_img = Image.new('1', (height, width), 255)  # not used
        draw = ImageDraw.Draw(black_img)

        # Draw text centered
        text_w, text_h = font.getmask(temperature).size
        text_x = (height - text_w) // 2
        text_y = width - text_h - 10
        draw.text((text_x, text_y), temperature, font=font, fill=black)

        # Load and paste icon
        icon = Image.open(icon_path).convert('1')
        icon_x = (height - icon.width) // 2
        icon_y = 10
        black_img.paste(icon, (icon_x, icon_y))

        # Display
        logger.debug("Sending image to display")
        epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))
        logger.debug("Weather dashboard rendered")

    except Exception as e:
        logger.exception(f"Weather rendering failed: {e}")
