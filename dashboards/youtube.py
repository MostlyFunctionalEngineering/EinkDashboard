from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import logging
import requests
import csv
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def render(epd, config):
    logger.debug("Rendering YouTube dashboard")

    try:
        height, width = epd.height, epd.width

        cfg = config.get('youtube', {})
        bg_path = cfg.get('background')
        font_path = cfg.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
        font_size = cfg.get('font_size', 18)
        invert = cfg.get('invert_colors', False)

        white = 255 if not invert else 0
        text_color = 255 if invert else 0

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

        load_dotenv()
        api_key = os.getenv("YOUTUBE_API_KEY")
        channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
        if not api_key or not channel_id:
            raise RuntimeError("Missing YOUTUBE_API_KEY or YOUTUBE_CHANNEL_ID in .env")

        # Fetch current stats
        url = (
            "https://www.googleapis.com/youtube/v3/channels"
            f"?part=snippet,statistics&id={channel_id}&key={api_key}"
        )
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()

        item = data['items'][0]
        sub_count = int(item['statistics']['subscriberCount'])
        logger.debug(f"Subscribers: {sub_count}")

        # Save to CSV
        os.makedirs("data", exist_ok=True)
        with open("data/subscribers.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().isoformat(), sub_count])

        # Prepare text
        sub_str = f"{sub_count:,} Subscribers"
        subs_font = ImageFont.truetype(font_path, font_size)

        text_layer = Image.new('L', (height, width), 255)
        draw_text = ImageDraw.Draw(text_layer)

        bbox = subs_font.getbbox(sub_str)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        x = height - text_w - 7  # 6 px buffer + 1 extra
        y = 6  # Top edge buffer

        draw_text.text((x, y), sub_str, font=subs_font, fill=0)

        # Paste text mask
        mask = text_layer.point(lambda p: 255 if p < 128 else 0, mode='1')
        black_img.paste(Image.new('1', (height, width), text_color), (0, 0), mask)

        rotated_black = black_img.rotate(90, expand=True)
        if invert:
            rotated_black = Image.eval(rotated_black, lambda px: 255 - px)

        epd.display_fast(epd.getbuffer(rotated_black))
        logger.debug("YouTube dashboard rendered")

    except Exception as e:
        logger.exception(f"YouTube rendering failed: {e}")
