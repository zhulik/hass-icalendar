DOMAIN = "icalendar"


async def async_setup(hass, config):
    hass.data[DOMAIN] = config[DOMAIN]

    hass.helpers.discovery.load_platform("calendar", DOMAIN, {}, config)

    return True
