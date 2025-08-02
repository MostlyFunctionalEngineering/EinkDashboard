from dashboards import clock, weather, stocks, youtube

dashboards = {
    "clock": clock.render,
    "weather": weather.render,
    "stocks": stocks.render,
    "youtube": youtube.render
}

def show_dashboard(name, epd, config):
    if name not in dashboards:
        raise ValueError(f"No dashboard found for: {name}")
    dashboards[name](epd, config)
