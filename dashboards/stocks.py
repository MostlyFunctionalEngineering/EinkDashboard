from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

YAHOO_FINANCE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"

def fetch_stock_data(symbols):
    try:
        query = ",".join(symbols)
        resp = requests.get(YAHOO_FINANCE_URL, params={"symbols": query})
        resp.raise_for_status()
        data = resp.json()
        quotes = data.get("quoteResponse", {}).get("result", [])
        result = []
        for quote in quotes:
            symbol = quote.get("symbol")
            price = quote.get("regularMarketPrice")
            change = quote.get("regularMarketChangePercent")
            if symbol and price is not None and change is not None:
                result.append((symbol, price, change))
        return result
    except Exception as e:
        logger.exception("Failed to fetch stock data")
        return []

def render(epd, config):
    logger.debug("Rendering stocks dashboard")
    try:
        height, width = epd.height, epd.width

        cfg = config.get('stocks', {})
        bg_path = cfg.get('background')
        font_path = cfg.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
        font_size = cfg.get('font_size', 20)
        invert = cfg.get('invert_colors', False)
        symbols = cfg.get('symbols', [])

        white = 255 if not invert else 0
        text_color = 255 if invert else 0
        max_rows = 4
        padding = 6

        font = ImageFont.truetype(font_path, font_size)
        black_img = Image.new('1', (height, width), white)

        if bg_path and os.path.exists(bg_path):
            try:
                background = Image.open(bg_path).convert('L').resize((height, width))
                if invert:
                    background = ImageOps.invert(background)
                background = background.convert('1')
                black_img.paste(background)
                logger.debug(f"Applied background: {bg_path}")
            except Exception as e:
                logger.warning(f"Failed to load background image: {e}")

        draw_layer = Image.new('L', (height, width), 255)
        draw = ImageDraw.Draw(draw_layer)

        stock_data = fetch_stock_data(symbols[:max_rows])
        row_height = font_size + 4
        total_height = row_height * len(stock_data)
        top_margin = (width - total_height) // 2

        for idx, (symbol, price, change) in enumerate(stock_data):
            y = top_margin + idx * row_height
            arrow = "↑" if change > 0 else ("↓" if change < 0 else "")
            percent = f"{arrow} {abs(change):.2f}%"
            price_str = f"{price:.2f}"

            # Column layout: [Symbol | Price | % Change]
            draw.text((padding, y), symbol, font=font, fill=0)
            price_w = font.getbbox(price_str)[2]
            draw.text(((height - price_w) // 2, y), price_str, font=font, fill=0)
            change_w = font.getbbox(percent)[2]
            draw.text((height - change_w - padding, y), percent, font=font, fill=0)

        mask = draw_layer.point(lambda p: 255 if p < 128 else 0, mode='1')
        black_img.paste(Image.new('1', (height, width), text_color), (0, 0), mask)

        logger.debug("Sending image to display")
        epd.display_fast(epd.getbuffer(black_img))
        logger.debug("Stocks dashboard rendered")

    except Exception as e:
        logger.exception(f"Stocks rendering failed: {e}")