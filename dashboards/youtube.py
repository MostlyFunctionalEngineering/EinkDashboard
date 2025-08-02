from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import logging
import csv
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def render(epd, config):
    logger.debug("Rendering YouTube dashboard")

    try:
        height, width = epd.height, epd.width

        yt_cfg = config.get('youtube', {})
        bg_path = yt_cfg.get('background')
        font_path = yt_cfg.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
        font_size = yt_cfg.get('font_size', 20)
        invert = yt_cfg.get('invert_colors', False)
        logo_path = 'assets/Borders_and_Logos/YouTube_Logo_68x48.bmp'
        data_path = 'data/subscribers.csv'

        white = 255 if not invert else 0
        text_color = 255 if invert else 0

        font = ImageFont.truetype(font_path, font_size)
        black_img = Image.new('1', (height, width), white)
        red_img = Image.new('1', (height, width), 255)

        if bg_path and os.path.exists(bg_path):
            try:
                bg = Image.open(bg_path).convert('L').resize((height, width))
                if invert:
                    bg = ImageOps.invert(bg)
                black_img.paste(bg.convert('1'))
                logger.debug(f"Applied background image: {bg_path}")
            except Exception as e:
                logger.warning(f"Failed to load background: {bg_path}, error: {e}")

        draw = ImageDraw.Draw(black_img)

        load_dotenv()
        api_key = os.getenv("YOUTUBE_API_KEY")
        channel_id = os.getenv("YOUTUBE_CHANNEL_ID")

        url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={api_key}"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()

        channel = data['items'][0]
        name = channel['snippet']['title']
        subs = int(channel['statistics']['subscriberCount'])

        # Save to CSV
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        now = datetime.now().isoformat()
        if not os.path.exists(data_path):
            with open(data_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'subscribers'])
        with open(data_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([now, subs])

        # Text for display
        name_str = name
        subs_str = f"{subs:,} Subscribers"

        # Logo
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert('1')
            black_img.paste(logo, (6, 6))
            logger.debug("Pasted YouTube logo")

        # Draw text on separate mask layer
        text_layer = Image.new('L', (height, width), 255)
        draw_text = ImageDraw.Draw(text_layer)

        name_w = font.getlength(name_str)
        subs_w = font.getlength(subs_str)

        draw_text.text((height - name_w - 6, 6), name_str, font=font, fill=0)
        draw_text.text((height - subs_w - 6, 6 + font_size + 4), subs_str, font=font, fill=0)

        mask = text_layer.point(lambda p: 255 if p < 128 else 0, mode='1')
        black_img.paste(Image.new('1', (height, width), text_color), (0, 0), mask)

        rotated_black = black_img.rotate(90, expand=True)
        rotated_red = red_img.rotate(90, expand=True)
        if invert:
            rotated_black = Image.eval(rotated_black, lambda px: 255 - px)

        epd.display_fast(epd.getbuffer(rotated_black))
        logger.debug("YouTube dashboard rendered")

    except Exception as e:
        logger.exception(f"YouTube rendering failed: {e}")
