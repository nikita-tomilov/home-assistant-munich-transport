from datetime import timedelta

DOMAIN = "munich_transport"
SCAN_INTERVAL = timedelta(seconds=90)

DEFAULT_ICON = "mdi:clock"

CONF_DEPARTURES = "departures"
CONF_DEPARTURES_NAME = "name"
CONF_DEPARTURES_WALKING_TIME = "walking_time"
CONF_DEPARTURES_WHITELIST = "whitelist"
CONF_TYPE_SUBURBAN = "S-Bahn"
CONF_TYPE_SUBWAY = "U-Bahn"
CONF_TYPE_TRAM = "Tram"
CONF_TYPE_BUS = "Bus"

TRANSPORT_TYPE_VISUALS = {
    CONF_TYPE_SUBWAY: {
        "code": "U",
        "icon": "mdi:subway",
        "color": "#0065AE",
    },
    CONF_TYPE_TRAM: {
        "code": "M",
        "icon": "mdi:tram",
        "color": "#E30613",
    },
    CONF_TYPE_BUS: {
        "code": "BUS",
        "icon": "mdi:bus",
        "color": "#133B4B"
    },
    "S1": {
        "code": "S",
        "icon": "mdi:subway-variant",
        "color": "#16bae7",
    },
    "S2": {
        "code": "S",
        "icon": "mdi:subway-variant",
        "color": "#76b82a",
    },
    "S3": {
        "code": "S",
        "icon": "mdi:subway-variant",
        "color": "#951b81",
    },
    "S4": {
        "code": "S",
        "icon": "mdi:subway-variant",
        "color": "#e30613",
    },
    "S6": {
        "code": "S",
        "icon": "mdi:subway-variant",
        "color": "#00975f",
    },
    "S7": {
        "code": "S",
        "icon": "mdi:subway-variant",
        "color": "#943126",
    },
    "S8": {
        "code": "S",
        "icon": "mdi:subway-variant",
        "color": "#ff6600",
    },
    "S20": {
        "code": "S",
        "icon": "mdi:subway-variant",
        "color": "#ea516d",
    },
}
