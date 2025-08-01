import dashboards.clock as clock

DASHBOARD_MAP = {
    'clock': clock.render,
}

def show_dashboard(name, epd, config):
    renderer = DASHBOARD_MAP.get(name)
    if renderer:
        renderer(epd, config)
    else:
        raise ValueError(f"No dashboard found for: {name}")
