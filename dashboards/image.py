from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)

def render(epd, config, flip_screen=False):
    try:
        target_w, target_h = epd.width, epd.height

        cfg = config.get('image', {})
        img_path = cfg.get('path')

        if not img_path or not os.path.exists(img_path):
            logger.error(f"Image dashboard: no valid path '{img_path}'")
            return

        # Open image
        img = Image.open(img_path).convert('1')

        # Maintain aspect ratio
        img_ratio = img.width / img.height
        screen_ratio = target_w / target_h

        if img_ratio > screen_ratio:
            new_w = target_w
            new_h = int(target_w / img_ratio)
        else:
            new_h = target_h
            new_w = int(target_h * img_ratio)

        img = img.resize((new_w, new_h))

        # Center on canvas
        canvas = Image.new('1', (target_w, target_h), 255)
        x_offset = (target_w - new_w) // 2
        y_offset = (target_h - new_h) // 2
        canvas.paste(img, (x_offset, y_offset))

        # Optional 180° flip
        if flip_screen:
            canvas = canvas.rotate(180)

        # **Rotate to match epd buffer expectation**
        canvas = canvas.rotate(90, expand=True)

        # Send to display
        epd.display(epd.getbuffer(canvas))
        logger.info(f"Image dashboard displayed: {img_path}")

    except Exception as e:
        logger.exception(f"Image dashboard failed: {e}")
