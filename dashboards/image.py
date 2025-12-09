from PIL import Image, ImageOps
import os
import logging

logger = logging.getLogger(__name__)

def render(epd, config, flip_screen=False):
    logger.debug("Rendering image dashboard")

    try:
        height, width = epd.height, epd.width  # same as clock.py
        cfg = config.get('image', {})
        img_path = cfg.get('path')

        if not img_path or not os.path.exists(img_path):
            logger.error(f"No valid image path: {img_path}")
            return

        # Optional invert
        invert = cfg.get('invert_colors', False)
        full_screen = cfg.get('full_screen', True)

        # Load image
        img = Image.open(img_path).convert('L')
        img_w, img_h = img.size

        if full_screen:
            # Scale to fit display (maintain aspect ratio)
            scale_w = height / img_w
            scale_h = width / img_h
            scale = min(scale_w, scale_h, 1.0)
            if scale != 1.0:
                img = img.resize((int(img_w * scale), int(img_h * scale)), Image.LANCZOS)
                img_w, img_h = img.size
        else:
            # If not full_screen, limit to display size
            if img_w > height or img_h > width:
                scale_w = height / img_w
                scale_h = width / img_h
                scale = min(scale_w, scale_h, 1.0)
                img = img.resize((int(img_w * scale), int(img_h * scale)), Image.LANCZOS)
                img_w, img_h = img.size

        if invert:
            img = ImageOps.invert(img)

        # Create display-sized canvas (height x width)
        canvas = Image.new('1', (height, width), 255)  # white background

        # Paste image centered (swap width/height for coordinates)
        x = (height - img_w) // 2
        y = (width - img_h) // 2
        canvas.paste(img.convert('1'), (x, y))

        # Flip if requested
        if flip_screen:
            canvas = canvas.rotate(180)

        epd.display_fast(epd.getbuffer(canvas))
        logger.info(f"Image displayed: {img_path} (full_screen={full_screen})")

    except Exception as e:
        logger.exception(f"Image dashboard failed: {e}")
