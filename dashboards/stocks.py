import os
import requests
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
FINNHUB_URL = "https://finnhub.io/api/v1/quote"

MARGIN = 6  # buffer around the edges

def fetch_stock_data(symbols):
    data = {}
    for symbol in symbols:
        try:
            resp = requests.get(
                FINNHUB_URL,
                params={"symbol": symbol, "token": FINNHUB_API_KEY},
                timeout=5
            )
            resp.raise_for_status()
            quote = resp.json()
            price = quote.get("c")
            prev_close = quote.get("pc")
            if price is not None and prev_close:
                change_pct = 100 * (price - prev_close) / prev_close
                data[symbol] = (price, change_pct)
        except Exception as e:
            logger.warning(f"Failed to fetch {symbol}: {e}")
    return data

def render(epd, config):
    try:
        logger.debug("Rendering stocks dashboard")

        height, width = epd.height, epd.width
        cfg = config.get("stocks", {})
        bg_path = cfg.get("background")
        font_path = cfg.get("font_path", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
        font_size = cfg.get("font_size", 18)
        invert = cfg.get("invert_colors", False)
        symbols = cfg.get("symbols", [])[:4]

        white = 255 if not invert else 0
        text_color = 255 if invert else 0

        font = ImageFont.truetype(font_path, font_size)
        line_height = font.getbbox("Hg")[3] - font.getbbox("Hg")[1] + 4

        black_img = Image.new("1", (height, width), white)

        if bg_path and os.path.exists(bg_path):
            try:
                background = Image.open(bg_path).convert("L").resize((height, width))
                if invert:
                    background = ImageOps.invert(background)
                background = background.convert("1")
                black_img.paste(background)
                logger.debug(f"Applied background image: {bg_path}")
            except Exception as e:
                logger.warning(f"Failed to load background {bg_path}: {e}")

        text_layer = Image.new("L", (height, width), 255)
        draw = ImageDraw.Draw(text_layer)

        data = fetch_stock_data(symbols)
        start_y = (width - (len(data) * line_height)) // 2

        for i, symbol in enumerate(symbols):
            if symbol not in data:
                continue
            price, pct = data[symbol]
            y = start_y + i * line_height

            arrow = "↑" if pct > 0 else "↓" if pct < 0 else "→"
            pct_str = f"{arrow} {abs(pct):.2f}%"

            draw.text((MARGIN, y), symbol, font=font, fill=0)
            price_text = f"{price:.2f}"
            price_w = font.getlength(price_text)
            draw.text(((height - price_w) // 2, y), price_text, font=font, fill=0)
            pct_w = font.getlength(pct_str)
            draw.text((height - MARGIN - pct_w, y), pct_str, font=font, fill=0)

        mask = text_layer.point(lambda p: 255 if p < 128 else 0, mode="1")
        black_img.paste(Image.new("1", (height, width), text_color), (0, 0), mask)

        logger.debug("Sending image to display")
        epd.display_fast(epd.getbuffer(black_img))
        logger.debug("Stocks dashboard rendered")

    except Exception as e:
        logger.exception(f"Stock rendering failed: {e}")
