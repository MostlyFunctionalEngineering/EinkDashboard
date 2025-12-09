from PIL import Image, ImageOps
import os
import logging

logger = logging.getLogger(__name__)

def render(epd, config, flip_screen=False):
    logger.debug("Rendering image dashboard")

    try:
        height, width = epd.height, epd.width  # height=122, width=250
        cfg = config.get('image', {})
        img_path = cfg.get('path')

        if not img_path or not os.path.exists(img_path):
            logger.error(f"No valid image path: {img_path}")
            return

        # Optional invert
        invert = cfg.get('invert_colors', False)

        # Load image
        img = Image.open(img_path).convert('L')
        img_w, img_h = img.size

        if invert:
            img = ImageOps.invert(img)

        # Create display-sized canvas
        black_img = Image.new('1', (height, width), 255)

        # Resize to fill screen if full-screen is desired
        full_screen = cfg.get('full_screen', True)
        if full_screen:
            img = img.resize((height, width))
            black_img.paste(img)
        else:
            # Keep original size and center
            x = (width - img_w) // 2
            y = (height - img_h) // 2
            black_img.paste(img, (x, y))

        # Flip if requested
        if flip_screen:
            black_img = black_img.rotate(180)

        epd.display_fast(epd.getbuffer(black_img))
        logger.info(f"Image displayed: {img_path}")

    except Exception as e:
        logger.exception(f"Image dashboard failed: {e}")
