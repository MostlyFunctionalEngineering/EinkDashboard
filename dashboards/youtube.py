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

        # Query YouTube API
        url = (
            "https://www.googleapis.com/youtube/v3/channels"
            f"?part=snippet,statistics&id={channel_id}&key={api_key}"
        )
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()

        item = data['items'][0]
        channel_name = item['snippet']['title']
        sub_count = int(item['statistics']['subscriberCount'])

        logger.debug(f"Fetched channel: {channel_name}, subscribers: {sub_count}")

        # Write to CSV
        os.makedirs("data", exist_ok=True)
        with open("data/subscribers.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().isoformat(), sub_count])

        # Fonts
        channel_font = ImageFont.truetype(font_path, font_size)
        subs_font = ImageFont.truetype(font_path, int(font_size * 0.9))

        text_layer = Image.new('L', (height, width), 255)
        draw_text = ImageDraw.Draw(text_layer)

        # Right-aligned text block with wrapping logic
        sub_str = f"{sub_count:,} Subscribers"
        channel_bbox = channel_font.getbbox(channel_name)
        channel_w = channel_bbox[2] - channel_bbox[0]
        channel_h = channel_bbox[3] - channel_bbox[1]

        subs_bbox = subs_font.getbbox(sub_str)
        subs_w = subs_bbox[2] - subs_bbox[0]
        subs_h = subs_bbox[3] - subs_bbox[1]

        if channel_w > height - 12:
            # Name too long: wrap to two lines
            line1_y = 6
            line2_y = line1_y + channel_h + 2
            draw_text.text((height - channel_w - 6, line1_y), channel_name, font=channel_font, fill=0)
            draw_text.text((height - subs_w - 6, line2_y), sub_str, font=subs_font, fill=0)
        else:
            # Vertically center both lines
            block_height = channel_h + subs_h + 2
            start_y = (width - block_height) // 2
            draw_text.text((height - channel_w - 6, start_y), channel_name, font=channel_font, fill=0)
            draw_text.text((height - subs_w - 6, start_y + channel_h + 2), sub_str, font=subs_font, fill=0)

        # Convert mask and paste text
        mask = text_layer.point(lambda p: 255 if p < 128 else 0, mode='1')
        black_img.paste(Image.new('1', (height, width), text_color), (0, 0), mask)

        # Rotate and display
        rotated_black = black_img.rotate(90, expand=True)
        if invert:
            rotated_black = Image.eval(rotated_black, lambda px: 255 - px)

        epd.display_fast(epd.getbuffer(rotated_black))
        logger.debug("YouTube dashboard rendered")

    except Exception as e:
        logger.exception(f"YouTube rendering failed: {e}")
