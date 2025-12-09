from PIL import Image, ImageOps
import os
import logging

logger = logging.getLogger(__name__)

def render(epd, config, flip_screen=False):
    logger.debug("Rendering image dashboard")

    try:
        height, width = epd.height, epd.width  # 122, 250
        cfg = config.get('image', {})
        img_path = cfg.get('path')

        if not img_path or not os.path.exists(img_path):
            logger.error(f"No valid image path: {img_path}")
            return

        invert = cfg.get('invert_colors', False)
        scale_mode = cfg.get('scale_mode', 'fit')  # 'fit', 'fill', or 'none'

        # Load image
        img = Image.open(img_path).convert('L')
        img_w, img_h = img.size

        if scale_mode in ('fit', 'fill'):
            scale_w = height / img_w
            scale_h = width / img_h
            if scale_mode == 'fit':
                scale = min(scale_w, scale_h)  # scale to fit with bars
            else:
                scale = max(scale_w, scale_h)  # zoom to fill, may crop
            if scale != 1.0:
                img = img.resize((int(img_w * scale), int(img_h * scale)), Image.LANCZOS)
                img_w, img_h = img.size
        elif scale_mode == 'none':
            # Only scale down if image is larger than display
            if img_w > height or img_h > width:
                scale_w = height / img_w
                scale_h = width / img_h
                scale = min(scale_w, scale_h, 1.0)
                img = img.resize((int(img_w * scale), int(img_h * scale)), Image.LANCZOS)
                img_w, img_h = img.size

        if invert:
            img = ImageOps.invert(img)

        # Create canvas
        canvas = Image.new('1', (height, width), 255)

        # Center the image
        x = (height - img_w) // 2
        y = (width - img_h) // 2
        canvas.paste(img.convert('1'), (x, y))

        if flip_screen:
            canvas = canvas.rotate(180)

        epd.display_fast(epd.getbuffer(canvas))
        logger.info(f"Image displayed: {img_path} (scale_mode={scale_mode})")

    except Exception as e:
        logger.exception(f"Image dashboard failed: {e}")
