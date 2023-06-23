from dataclasses import dataclass
from datetime import datetime

from .const import DEFAULT_ICON, TRANSPORT_TYPE_VISUALS, CONF_TYPE_SUBURBAN


@dataclass
class Departure:
    """Departure dataclass to store data from API"""

    trip_id: str
    line_name: str
    line_type: str
    timestamp: datetime
    time: str
    direction: str | None = None
    icon: str | None = None
    bg_color: str | None = None
    location: tuple[float, float] | None = None

    @classmethod
    def from_dict(cls, source):
        if source['type'] == CONF_TYPE_SUBURBAN:
            key = 'line'
        else:
            key = 'type'
        line_visuals = TRANSPORT_TYPE_VISUALS.get(source[key]) or {}
        timestamp = source['departureTime']
        return cls(
            trip_id=source["destination"],
            line_name=source['line'],
            line_type=source['type'],
            timestamp=timestamp,
            time="%s min" % source['departureTimeMinutes'],
            direction=source['destination'],
            icon=line_visuals.get("icon") or DEFAULT_ICON,
            bg_color=line_visuals.get("color") or "green",
            location=(0.0, 0.0),
        )

    def to_dict(self):
        return {
            "line_name": self.line_name,
            "line_type": self.line_type,
            "time": self.time,
            "direction": self.direction,
            "color": self.bg_color,
        }
