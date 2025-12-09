from dashboards import clock, weather, stocks, youtube, text

dashboards = {
    "clock": clock.render,
    "weather": weather.render,
    "stocks": stocks.render,
    "youtube": youtube.render,
    "text": text.render
}

def show_dashboard(name, epd, config, flip_screen=False):
    if name not in dashboards:
        raise ValueError(f"No dashboard found for: {name}")
    dashboards[name](epd, config, flip_screen=flip_screen)
