from PIL import Image, ImageOps
import os
import logging

logger = logging.getLogger(__name__)

def render(epd, config, flip_screen=False):
    logger.debug("Rendering image dashboard")

    try:
        width, height = epd.width, epd.height  # note: PIL uses (width, height)
        cfg = config.get('image', {})
        img_path = cfg.get('path')

        if not img_path or not os.path.exists(img_path):
            logger.error(f"No valid image path: {img_path}")
            return

        invert = cfg.get('invert_colors', False)
        full_screen = cfg.get('full_screen', True)

        # Load image
        img = Image.open(img_path).convert('L')
        if invert:
            img = ImageOps.invert(img)

        # Create canvas
        black_img = Image.new('1', (width, height), 255)  # white background

        if full_screen:
            # Resize to fill display exactly
            img_resized = img.resize((width, height))
            black_img.paste(img_resized.convert('1'), (0, 0))
        else:
            # Keep original size, center
            img_w, img_h = img.size
            x = (width - img_w) // 2
            y = (height - img_h) // 2
            black_img.paste(img.convert('1'), (x, y))

        if flip_screen:
            black_img = black_img.rotate(180)

        epd.display_fast(epd.getbuffer(black_img))
        logger.info(f"Image displayed: {img_path}")

    except Exception as e:
        logger.exception(f"Image dashboard failed: {e}")
