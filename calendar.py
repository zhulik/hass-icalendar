from datetime import datetime

import voluptuous as vol
import aiohttp

from icalendar import Calendar as iCal

from homeassistant.components.calendar import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    CalendarEventDevice,
    calculate_offset,
    get_date,
    is_offset_reached,
)

from homeassistant.const import (
    CONF_NAME,
    CONF_PASSWORD,
    CONF_URL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
)

import homeassistant.helpers.config_validation as cv

from . import DOMAIN

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_URL): vol.Url(),
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    if discovery_info is None:
        return
    config = hass.data[DOMAIN]
    add_entities([ICalendarEventDevice(config[CONF_NAME], config[CONF_URL])], True)


class ICalendarEventDevice(CalendarEventDevice):
    def __init__(self, name, url):
        self._url = url
        self._name = name
        self._calendar = None

    @property
    def device_state_attributes(self):
        return {}

    @property
    def event(self):
        if not self._calendar:
            return
        events = self._calendar.current_events
        if not events:
            events = self._calendar.upcoming_events
        if not events:
            return
        current = events[0]
        if current is None:
            return
        return {
            "summary": current.summary,
            "start": {"dateTime": current.start.isoformat()},
            "end": {"dateTime": current.end.isoformat()},
        }

    @property
    def name(self):
        return self._name

    async def async_update(self):
        content = await fetch(self._url)
        self._calendar = Calendar(content)

    async def async_get_events(self, hass, start_date, end_date):
        return [
            {
                "summary": e.summary,
                "start": {"dateTime": e.start.isoformat()},
                "end": {"dateTime": e.end.isoformat()},
            }
            for e in self._calendar.events
            if e.start >= start_date and e.end <= end_date
        ]


class Event:
    def __init__(self, component):
        self.summary = component.get("summary")
        self.start = component.get("dtstart").dt.astimezone()
        self.end = component.get("dtend").dt.astimezone()


class Calendar:
    def __init__(self, content):
        ical = iCal.from_ical(content)
        self.events = sorted(
            [Event(e) for e in ical.walk() if e.name == "VEVENT"],
            key=lambda e: e.start,
        )

    @property
    def current_events(self):
        now = datetime.now().astimezone()
        return [e for e in self.events if e.start < now and e.end > now]

    @property
    def upcoming_events(self):  # all upcoming events
        now = datetime.now().astimezone()
        return [e for e in self.events if e.start > now]

    @property
    def next_events(self):  # the next upcoming events
        upcoming = self.upcoming_events
        if not self.upcoming_events:
            return []
        start = self.upcoming_events[0].start
        return [e for e in upcoming if e.start == start]


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
