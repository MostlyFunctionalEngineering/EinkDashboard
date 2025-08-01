# dashboards/clock.py

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def render(epd, config):
    epd.Clear()

    # Get display dimensions
    width, height = epd.width, epd.height

    # Load clock-specific settings
    clock_cfg = config.get('clock', {})
    font_path = clock_cfg.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
    font_size = clock_cfg.get('font_size', 20)
    use_24hr = clock_cfg.get('use_24hr', False)
    show_date = clock_cfg.get('show_date', False)

    # Format time string
    now = datetime.now()
    time_str = now.strftime('%H:%M' if use_24hr else '%I:%M').lstrip('0')  # remove leading 0 in 12-hr
    date_str = now.strftime('%Y-%m-%d') if show_date else None

    # Load font
    font = ImageFont.truetype(font_path, font_size)

    # Draw black image only
    black_img = Image.new('1', (width, height), 255)
    draw_black = ImageDraw.Draw(black_img)

    # Center time text
    time_w, time_h = draw_black.textsize(time_str, font=font)
    time_x = (width - time_w) // 2
    time_y = (height // 2 - time_h) if not show_date else (height // 3 - time_h // 2)
    draw_black.text((time_x, time_y), time_str, font=font, fill=0)

    # Optional date
    if date_str:
        date_w, date_h = draw_black.textsize(date_str, font=font)
        date_x = (width - date_w) // 2
        date_y = (2 * height // 3 - date_h // 2)
        draw_black.text((date_x, date_y), date_str, font=font, fill=0)


    epd.display(epd.getbuffer(black_img), epd.getbuffer(Image.new('1', (width, height), 255)))
    epd.sleep()
