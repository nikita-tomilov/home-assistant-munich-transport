"""Munich public transport (MVG) integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from mvg import MvgApi

from .const import (
    DOMAIN,  # noqa
    SCAN_INTERVAL,  # noqa
    CONF_DEPARTURES,
    CONF_DEPARTURES_WALKING_TIME,
    CONF_DEPARTURES_WHITELIST,
    CONF_TYPE_BUS,
    CONF_TYPE_SUBURBAN,
    CONF_TYPE_SUBWAY,
    CONF_TYPE_TRAM,
    CONF_DEPARTURES_NAME,
    DEFAULT_ICON,
)
from .departure import Departure

_LOGGER = logging.getLogger(__name__)

TRANSPORT_TYPES_SCHEMA = {
    vol.Optional(CONF_TYPE_SUBURBAN, default=True): bool,
    vol.Optional(CONF_TYPE_SUBWAY, default=True): bool,
    vol.Optional(CONF_TYPE_TRAM, default=True): bool,
    vol.Optional(CONF_TYPE_BUS, default=True): bool,
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_DEPARTURES): [
            {
                vol.Required(CONF_DEPARTURES_NAME): str,
                vol.Optional(CONF_DEPARTURES_WALKING_TIME, default=1): int,
                vol.Optional(CONF_DEPARTURES_WHITELIST, default=""): str,
                **TRANSPORT_TYPES_SCHEMA,
            }
        ]
    }
)


async def async_setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        _: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    if CONF_DEPARTURES in config:
        for departure in config[CONF_DEPARTURES]:
            add_entities([TransportSensor(hass, departure)])


def add_departure_time_minutes(entry):
    timestamp1 = datetime.fromtimestamp(entry['time'])
    timestamp2 = datetime.fromtimestamp(entry['planned'])
    timestamp = min(timestamp1, timestamp2)
    time_until_departure = timestamp - datetime.now()
    time_until_departure_minutes = int(time_until_departure.total_seconds() / 60)
    entry['departureTime'] = timestamp
    entry['departureTimeMinutes'] = time_until_departure_minutes
    return entry


class TransportSensor(SensorEntity):
    departures: list[Departure] = []

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        self.hass: HomeAssistant = hass
        self.config: dict = config
        self.station_name: str = config.get(CONF_DEPARTURES_NAME)
        self.walking_time: int = config.get(CONF_DEPARTURES_WALKING_TIME) or 1
        self.whitelist: str = config.get(CONF_DEPARTURES_WHITELIST) or ""
        self.whitelist_entries = []
        # we add +1 minute anyway to delete the "just gone" transport

    @property
    def name(self) -> str:
        return self.station_name

    @property
    def icon(self) -> str:
        next_departure = self.next_departure()
        if next_departure:
            return next_departure.icon
        return DEFAULT_ICON

    @property
    def unique_id(self) -> str:
        return f"stop_{self.station_name}_departures"

    @property
    def state(self) -> str:
        next_departure = self.next_departure()
        if next_departure:
            return f"Next {next_departure.line_name} at {next_departure.time}"
        return "N/A"

    @property
    def extra_state_attributes(self):
        return {
            "departures": [departure.to_dict() for departure in self.departures or []]
        }

    def update(self):
        self.departures = self.fetch_departures()

    def is_whitelisted(self, entry):
        if self.whitelist == "":
            return True
        if len(self.whitelist_entries) == 0:
            self.whitelist_entries = self.whitelist.split(",")
            self.whitelist_entries = list(map(lambda x: x.lower(), self.whitelist_entries))
        destination = entry["destination"].lower()
        for whitelist_entry in self.whitelist_entries:
            if whitelist_entry in destination:
                return True
        return False

    def fetch_departures(self) -> Optional[list[Departure]]:
        station = MvgApi.station(self.station_name)

        if station is None:
            _LOGGER.warning("Could not find %s" % self.station_name)
            return []

        stop_id = station['id']
        _LOGGER.debug(f"OK: station ID for {self.station_name}: {stop_id}")

        mvgapi = MvgApi(stop_id)
        departures = mvgapi.departures(limit=100)
        departures = list(map(lambda x: add_departure_time_minutes(x), departures))
        departures = list(
            filter(lambda d: self.walking_time < int(d['departureTimeMinutes']) and not bool(
                d['cancelled']) and self.is_whitelisted(d), departures))

        _LOGGER.debug(f"OK: departures for {stop_id}: {departures}")

        # convert api data into objects
        unsorted = [Departure.from_dict(departure) for departure in departures]
        return sorted(unsorted, key=lambda d: d.timestamp)

    def next_departure(self):
        if self.departures and isinstance(self.departures, list):
            return self.departures[0]
        return None
