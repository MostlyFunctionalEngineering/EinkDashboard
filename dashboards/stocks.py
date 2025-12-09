from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import logging
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def render(epd, config, flip_screen=false):
    try:
        logger.debug("Rendering stocks dashboard")
        height, width = epd.height, epd.width

        stock_cfg = config.get('stocks', {})
        bg_path = stock_cfg.get('background')
        font_path = stock_cfg.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
        font_size = stock_cfg.get('font_size', 18)
        invert = stock_cfg.get('invert_colors', False)
        symbols = stock_cfg.get('symbols', [])[:8]

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
        api_key = os.getenv("FINNHUB_API_KEY")
        results = []
        for sym in symbols:
            try:
                url = f"https://finnhub.io/api/v1/quote?symbol={sym}&token={api_key}"
                resp = requests.get(url)
                resp.raise_for_status()
                data = resp.json()
                price = data.get('c')
                prev = data.get('pc')
                if price and prev:
                    change_pct = ((price - prev) / prev) * 100
                    results.append((sym, price, change_pct))
            except Exception as e:
                logger.warning(f"Failed to fetch {sym}: {e}")

        top_margin = 6
        row_height = font_size + 4
        total_height = len(results) * row_height
        start_y = (width - total_height) // 2

        # Column x-positions: left, center (shifted), right
        col_x = {
            "symbol": 6,
            "price_center": (height // 2) - 6,
            "pct_right": height - 6
        }

        for i, (sym, price, pct) in enumerate(results):
            y = start_y + i * row_height
            price_str = f"{price:7.2f}"
            pct_str = f"{abs(pct):.2f}%"
            arrow = "↑" if pct > 0 else "↓"

            # Left-aligned ticker
            draw.text((col_x["symbol"], y), sym, font=font, fill=text_color)

            # Center-aligned price (decimal-point approximation)
            price_w = font.getlength(price_str)
            draw.text((col_x["price_center"] - price_w / 2, y), price_str, font=font, fill=text_color)

            # Right-aligned arrow + percent (tightened spacing)
            arrow_w = font.getlength(arrow)
            pct_w = font.getlength(pct_str)
            total_w = arrow_w + 2 + pct_w
            draw.text((col_x["pct_right"] - total_w, y), arrow, font=font, fill=text_color)
            draw.text((col_x["pct_right"] - pct_w, y), pct_str, font=font, fill=text_color)

        rotated_black = black_img.rotate(90, expand=True)
        rotated_red = red_img.rotate(90, expand=True)
        if invert:
            rotated_black = Image.eval(rotated_black, lambda px: 255 - px)
        if flip_screen:
            image = image.rotate(180)  # flip upside-down
        epd.display_fast(epd.getbuffer(rotated_black))
        logger.debug("Stocks dashboard rendered")

    except Exception as e:
        logger.exception(f"Stocks rendering failed: {e}")
