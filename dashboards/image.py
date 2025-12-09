from PIL import Image
import os, logging
logger = logging.getLogger(__name__)

def render(epd, config, flip_screen=False):
    cfg = config.get('image', {})
    img_path = cfg.get('path')
    if not img_path or not os.path.exists(img_path):
        logger.error(f"Image dashboard: no valid path {img_path}")
        return

    img = Image.open(img_path).convert('1')
    # optional: resize/fit to screen:
    img = img.resize((epd.width, epd.height))
    if flip_screen:
        img = img.rotate(180)
    epd.display(epd.getbuffer(img))
    logger.info(f"Displayed image dashboard from {img_path}")