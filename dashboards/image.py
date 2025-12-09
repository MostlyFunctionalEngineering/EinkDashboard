from PIL import Image, ImageOps
import os
import logging

logger = logging.getLogger(__name__)

def render(epd, config, flip_screen=False):
    logger.debug("Rendering image dashboard")

    try:
        width, height = epd.width, epd.height  # width=250, height=122
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

        # Create canvas in display orientation (width × height)
        canvas = Image.new('1', (width, height), 255)  # white background

        if full_screen:
            # Stretch to fill display exactly
            img_resized = img.resize((width, height))
            canvas.paste(img_resized.convert('1'), (0, 0))
        else:
            # Center without scaling
            img_w, img_h = img.size
            x = (width - img_w) // 2
            y = (height - img_h) // 2
            canvas.paste(img.convert('1'), (x, y))

        # Rotate 90° clockwise to match display orientation
        canvas = canvas.rotate(-90, expand=True)

        # Flip upside-down if requested
        if flip_screen:
            canvas = canvas.rotate(180)

        epd.display_fast(epd.getbuffer(canvas))
        logger.info(f"Image displayed: {img_path}")

    except Exception as e:
        logger.exception(f"Image dashboard failed: {e}")
