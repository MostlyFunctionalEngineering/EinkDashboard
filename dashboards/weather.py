from PIL import Image, ImageDraw, ImageFont
import os
import logging
import requests
from datetime import datetime, time
from dateutil import parser
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)

# Weathercode icon mapping (default to day icons)
WEATHERCODE_ICON_MAP = {
    0:  "day_clear.bmp",
    1:  "day_partial_cloudy.bmp",
    2:  "day_partial_cloudy.bmp",
    3:  "overcast.bmp",
    45: "fog.bmp",
    48: "fog.bmp",
    51: "day_rain.bmp",
    53: "day_rain.bmp", 
    55: "day_rain.bmp",
    56: "day_rain.bmp",
    57: "day_rain.bmp",
    61: "rain.bmp",
    63: "rain.bmp",
    65: "rain.bmp",
    66: "sleet.bmp",
    67: "sleet.bmp",
    71: "day_snow.bmp",
    73: "day_snow.bmp",
    75: "day_snow.bmp",
    77: "day_snow.bmp",
    80: "day_rain.bmp",
    81: "day_rain.bmp",
    82: "day_rain.bmp",
    85: "day_snow.bmp",
    86: "day_snow.bmp",
    95: "rain_thunder.bmp",
    96: "rain_thunder.bmp",
    99: "rain_thunder.bmp"
}

ICON_DIR = "assets/Weather_Icons"

def is_night(now, sunrise_str, sunset_str):
    try:
        sunrise = datetime.fromisoformat(sunrise_str).time()
        sunset = datetime.fromisoformat(sunset_str).time()
        return now.time() < sunrise or now.time() > sunset
    except Exception as e:
        logger.warning(f"Could not parse sunrise/sunset: {e}")
        return False

def adjust_icon_for_daylight(base_icon, night):
    if night:
        if base_icon.startswith("day_clear"):
            return "night_clear.bmp"
        elif base_icon.startswith("day_partial_cloudy"):
            return "night_partial_cloud.bmp"
        elif base_icon.startswith("day_rain"):
            return "night_rain.bmp"
        elif base_icon.startswith("day_snow"):
            return "night_snow.bmp"
        elif base_icon.startswith("day_snow_thunder"):
            return "night_snow_thunder.bmp"
        elif base_icon.startswith("day_sleet"):
            return "night_sleet.bmp"
    return base_icon

def icon_path_for_code(code, night=False):
    filename = WEATHERCODE_ICON_MAP.get(int(code), "cloudy.bmp")
    adjusted = adjust_icon_for_daylight(filename, night)
    return os.path.join(ICON_DIR, adjusted)

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

def degrees_to_compass(deg):
    dirs = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    ix = round(deg / 22.5) % 16
    return dirs[ix]

def fetch_weather(lat, lon, forecast_mode, use_celsius):
    units = "celsius" if use_celsius else "fahrenheit"
    base_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&current_weather=true&timezone=auto"
        f"&daily=sunrise,sunset,temperature_2m_max,temperature_2m_min,weathercode"
        f"&hourly=temperature_2m,apparent_temperature,weathercode,relative_humidity_2m"
        f"&temperature_unit={units}"
    )
    r = requests.get(base_url)
    r.raise_for_status()
    return r.json()

def render(epd, config):
    try:
        logger.debug("Rendering weather dashboard")
        height, width = epd.width, epd.height

        cfg = config.get('weather', {})
        bg_path = cfg.get('background')
        font_path = cfg.get('font_path', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
        font_size = cfg.get('font_size', 24)
        invert = cfg.get('invert_colors', False)
        zip_code = cfg.get('location', '84101')
        use_celsius = cfg.get('units', 'C') == 'C'
        forecast_mode = cfg.get('forecast_mode', 'hourly')
        date_fmt = cfg.get('date_format', '%a %b %d')

        white = 255 if not invert else 0
        text_color = 0

        font = ImageFont.truetype(font_path, font_size)
        small_font = ImageFont.truetype(font_path, int(font_size * 0.6))

        lat, lon = zip_to_latlon(zip_code)
        weather = fetch_weather(lat, lon, forecast_mode, use_celsius)

        current = weather["current_weather"]
        hourly = weather.get("hourly", {})
        forecast = weather["hourly"] if forecast_mode == "hourly" else weather["daily"]

        now = datetime.now()
        hourly_times = [parser.isoparse(t) for t in hourly["time"]]
        now_rounded = now.replace(minute=0, second=0, microsecond=0)

        # Find the closest match
        try:
            humidity_index = next(i for i, t in enumerate(hourly_times) if t == now_rounded)
            humidity = round(hourly["relative_humidity_2m"][humidity_index])
        except StopIteration:
            humidity = None

        sunrise = weather["daily"]["sunrise"][0]
        sunset = weather["daily"]["sunset"][0]
        night = is_night(now, sunrise, sunset)

        black_img = Image.new('1', (width, height), white)

        if bg_path and os.path.exists(bg_path):
            try:
                background = Image.open(bg_path).convert('1').resize((width, height))
                black_img.paste(background)
                logger.debug(f"Applied background image: {bg_path}")
            except Exception as e:
                logger.warning(f"Failed to load background image: {bg_path}, error: {e}")

        draw = ImageDraw.Draw(black_img)

        # Date (top right)
        date_str = now.strftime(date_fmt)
        bbox = font.getbbox(date_str)
        date_w, date_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((width - date_w - 6, 4), date_str, font=font, fill=text_color)

        # Current icon
        current_code = current.get("weathercode", 0)
        icon_path = icon_path_for_code(current_code, night)
        icon = Image.open(icon_path).convert('1')
        black_img.paste(icon, (4, 4))

        # Temp and humidity
        unit = "°C" if use_celsius else "°F"
        temp = round(current["temperature"])
        temp_str = f"{temp}{unit}"
        draw.text((93, 36), temp_str, font=font, fill=text_color)
        if humidity is not None:
            hum_str = f" {humidity}%RH"
            bbox = font.getbbox(temp_str)
            temp_w = bbox[2] - bbox[0]
            draw.text((93 + temp_w + 15, 36), hum_str, font=font, fill=text_color)

        # Wind speed and direction (bottom-left corner)
        wind_kmh = current.get("windspeed", 0)
        wind_dir = current.get("winddirection", 0)

        wind_knots = round(wind_kmh * 0.539957)
        wind_compass = degrees_to_compass(wind_dir)

        # Format text
        speed_str = str(wind_knots)
        units_str = "kts"
        dir_str = wind_compass

        # Text dimensions
        speed_bbox = font.getbbox(speed_str)
        speed_w = speed_bbox[2] - speed_bbox[0]
        speed_h = speed_bbox[3] - speed_bbox[1]

        units_bbox = small_font.getbbox(units_str)
        dir_bbox = small_font.getbbox(dir_str)
        units_h = units_bbox[3] - units_bbox[1]
        dir_h = dir_bbox[3] - dir_bbox[1]
        label_spacing = 2

        # Anchor position (bottom-left, raised 6px)
        margin = 7
        y_anchor = height - speed_h - margin - 6  # raise entire block 6px

        # Draw wind speed
        draw.text((margin, y_anchor), speed_str, font=font, fill=text_color)

        # Draw units and direction inline
        label_str = f"{units_str} {dir_str}"
        label_bbox = small_font.getbbox(label_str)
        label_h = label_bbox[3] - label_bbox[1]
        x_labels = margin + speed_w + 6

        draw.text((x_labels, y_anchor + (speed_h - label_h) // 2), label_str, font=small_font, fill=text_color)

        # Forecast (bottom), skipping today
        forecast_y = height - 60
        spacing = 52
        icon_size = 40  # pixels
        for i in range(1, 4):
            if forecast_mode == "hourly":
                t = forecast["time"][i]
                f_temp = round(forecast["temperature_2m"][i])
                f_code = forecast["weathercode"][i]
                label = datetime.fromisoformat(t).strftime("%H:%M")
            else:
                t = forecast["time"][i]
                f_temp = round(forecast["temperature_2m_max"][i])
                f_code = forecast["weathercode"][i]
                label = datetime.fromisoformat(t).strftime("%a")

            x = width - (4 - i) * spacing

            # Forecast icon
            icon_path = icon_path_for_code(f_code, False)
            icon = Image.open(icon_path).convert('1').resize((icon_size, icon_size))
            black_img.paste(icon, (x, forecast_y))

            # Forecast text layout
            temp_str = f"{f_temp}{unit}"
            date_bbox = small_font.getbbox(label)
            temp_bbox = small_font.getbbox(temp_str)

            date_h = date_bbox[3] - date_bbox[1]
            temp_h = temp_bbox[3] - temp_bbox[1]

            date_y = forecast_y + icon_size + 2
            temp_y = date_y + date_h + 2

            draw.text((x, date_y), label, font=small_font, fill=text_color)
            draw.text((x, temp_y), temp_str, font=small_font, fill=text_color)


        # Rotate and invert if needed
        rotated_black = black_img.rotate(90, expand=True)

        if invert:
            rotated_black = Image.eval(rotated_black, lambda px: 255 - px)

        epd.display_fast(epd.getbuffer(rotated_black))
        logger.debug("Weather dashboard rendered")

    except Exception as e:
        logger.exception(f"Weather rendering failed: {e}")
