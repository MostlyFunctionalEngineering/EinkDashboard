from PIL import Image, ImageDraw, ImageFont
import os
import logging
import requests
from datetime import datetime
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)

# Direct match to provided bitmap names (no inference logic needed)
WEATHER_CODE_ICON_MAP = {
    "cloudy": "cloudy.bmp",
    "day_clear": "day_clear.bmp",
    "day_partial_cloudy": "day_partial_cloudy.bmp",
    "day_rain_thunder": "day_rain_thunder.bmp",
    "day_rain": "day_rain.bmp",
    "day_sleet": "day_sleet.bmp",
    "day_snow_thunder": "day_snow_thunder.bmp",
    "day_snow": "day_snow.bmp",
    "fog": "fog.bmp",
    "mist": "mist.bmp",
    "night_clear": "night_clear.bmp",
    "night_partial_cloud": "night_partial_cloud.bmp",
    "night_rain": "night_rain.bmp",
    "night_sleet": "night_sleet.bmp",
    "night_snow_thunder": "night_snow_thunder.bmp",
    "night_snow": "night_snow.bmp",
    "overcast": "overcast.bmp",
    "rain_thunder": "rain_thunder.bmp",
    "rain": "rain.bmp",
    "sleet": "sleet.bmp",
    "snow_thunder": "snow_thunder.bmp",
    "snow": "snow.bmp",
    "thunder": "thunder.bmp",
    "tornado": "tornado.bmp",
    "wind": "wind.bmp"
}

ICON_DIR = "assets/Weather_Icons"

def icon_path_for_code(code_str):
    return os.path.join(ICON_DIR, WEATHER_CODE_ICON_MAP.get(code_str, "cloudy.bmp"))

def zip_to_latlon(zip_code):
    try:
        geolocator = Nominatim(user_agent="eink-weather")
        location = geolocator.geocode({"postalcode": zip_code, "country": "USA"})
        if not location:
            raise ValueError(f"No lat/lon found for ZIP {zip_code}")
        return location.latitude, location.longitude
    except Exception as e:
        logger.exception(f"ZIP to lat/lon failed for {zip_code}")
        raise

def fetch_weather(lat, lon, forecast_mode, use_celsius):
    units = "celsius" if use_celsius else "fahrenheit"
    base_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    if forecast_mode == "hourly":
        base_url += f"&hourly=temperature_2m,apparent_temperature,weathercode&temperature_unit={units}"
    else:
        base_url += f"&daily=temperature_2m_max,temperature_2m_min,weathercode&temperature_unit={units}"
    base_url += "&timezone=auto"
    r = requests.get(base_url)
    r.raise_for_status()
    return r.json()

def render(epd, config):
    try:
        logger.debug("Rendering weather dashboard")
        width, height = epd.width, epd.height

        # Config values
        cfg = config.get('weather', {})
        font_path = cfg.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
        font_size = cfg.get('font_size', 24)
        invert = cfg.get('invert_colors', False)
        zip_code = cfg.get('location', '84101')
        use_celsius = cfg.get('units', 'C') == 'C'
        forecast_mode = cfg.get('forecast_mode', 'hourly')  # or 'daily'
        date_fmt = cfg.get('date_format', '%a %b %d')

        # Display colors
        white = 255 if not invert else 0
        black = 0 if not invert else 255

        # Font loading
        font = ImageFont.truetype(font_path, font_size)
        small_font = ImageFont.truetype(font_path, int(font_size * 0.6))

        # Geolocation
        lat, lon = zip_to_latlon(zip_code)

        # Fetch weather
        weather = fetch_weather(lat, lon, forecast_mode, use_celsius)
        current = weather["current_weather"]
        forecast = weather["hourly"] if forecast_mode == "hourly" else weather["daily"]

        # Start canvas
        black_img = Image.new('1', (width, height), white)
        red_img = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(black_img)

        # Draw date (top right)
        now = datetime.now()
        date_str = now.strftime(date_fmt)
        date_w, date_h = font.getsize(date_str)
        draw.text((width - date_w - 6, 4), date_str, font=font, fill=black)

        # Draw weather icon (top left)
        current_code = str(current.get("weathercode", "cloudy"))
        icon_path = icon_path_for_code(current_code)
        icon = Image.open(icon_path).convert('1')
        black_img.paste(icon, (4, 4))

        # Draw temp and feels like
        unit = "°C" if use_celsius else "°F"
        temp = round(current["temperature"])
        feels_like = round(forecast["apparent_temperature"][0]) if forecast_mode == "hourly" else temp

        draw.text((90, 20), f"{temp}{unit}", font=font, fill=black)
        draw.text((90, 20 + font_size + 2), f"Feels like {feels_like}{unit}", font=small_font, fill=black)

        # Forecast icons (bottom)
        forecast_y = height - 50
        spacing = (width - 8) // 5
        for i in range(5):
            if forecast_mode == "hourly":
                time = forecast["time"][i]
                f_temp = round(forecast["temperature_2m"][i])
                f_code = str(forecast["weathercode"][i])
                label = datetime.fromisoformat(time).strftime("%H:%M")
            else:
                time = forecast["time"][i]
                f_temp = round(forecast["temperature_2m_max"][i])
                f_code = str(forecast["weathercode"][i])
                label = datetime.fromisoformat(time).strftime("%a")

            x = 4 + i * spacing
            icon_path = icon_path_for_code(f_code)
            icon = Image.open(icon_path).convert('1').resize((40, 40))
            black_img.paste(icon, (x, forecast_y))
            draw.text((x, forecast_y + 42), f"{f_temp}{unit}", font=small_font, fill=black)
            draw.text((x, forecast_y + 56), label, font=small_font, fill=black)

        # Push to screen
        logger.debug("Sending image to display")
        epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))
        logger.debug("Weather dashboard rendered")

    except Exception as e:
        logger.exception(f"Weather rendering failed: {e}")
