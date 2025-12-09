from PIL import Image, ImageOps
import os
import logging

logger = logging.getLogger(__name__)

def render(epd, config, flip_screen=False):
    logger.debug("Rendering image dashboard")

    try:
        height, width = epd.height, epd.width  # e.g., height=122, width=250
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

        # Resize if larger than display
        scale_w = width / img_w
        scale_h = height / img_h
        scale = min(scale_w, scale_h, 1.0)  # never scale up
        if scale < 1.0:
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            img_w, img_h = img.size

        if invert:
            img = ImageOps.invert(img)

        # Create display canvas and paste image centered
        canvas = Image.new('1', (width, height), 255)  # white background
        x = (width - img_w) // 2
        y = (height - img_h) // 2
        canvas.paste(img.convert('1'), (x, y))

        # Flip if requested
        if flip_screen:
            canvas = canvas.rotate(180)

        epd.display_fast(epd.getbuffer(canvas))
        logger.info(f"Image displayed: {img_path}")

    except Exception as e:
        logger.exception(f"Image dashboard failed: {e}")
