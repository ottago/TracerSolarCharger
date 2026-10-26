"""Constants for the Tracer Solar Charger integration."""

DOMAIN = "tracer_solar_charger"

# Configuration keys
CONF_SLAVE_ID = "slave_id"
CONF_BAUDRATE = "baudrate"
CONF_SCAN_INTERVAL = "scan_interval"

# Default values
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_TIMEOUT = 3  # seconds

# Device information
MANUFACTURER = "EPEVER"
MODEL = "Tracer3210AN"

# Key parameters to expose as sensors (only existing parameters)
SENSOR_PARAMETERS = [
    "pv_voltage",
    "pv_current",
    "pv_power",
    "battery_voltage",
    "battery_current",
    "battery_soc",
    "battery_temp",
    "load_voltage",
    "load_current",
    "load_power",
    "device_temp",
    "battery_status",
    "charging_equipment_status",
    "fault_status"
]

# Home Assistant device classes for parameters
DEVICE_CLASSES = {
    "voltage": ["pv_voltage", "battery_voltage", "load_voltage"],
    "current": ["pv_current", "battery_current", "load_current"],
    "power": ["pv_power", "load_power"],
    "energy": ["generated_energy_today_combined", "consumed_energy_today_combined"],
    "temperature": ["battery_temp", "device_temp"],
    "battery": ["battery_soc"]
}

# Icons for different parameter types
ICONS = {
    "pv": "mdi:solar-panel",
    "battery": "mdi:battery",
    "load": "mdi:power-plug",
    "system": "mdi:chip",
    "statistics": "mdi:chart-line",
    "configuration": "mdi:cog"
}

# Plausible value ranges (after scaling) for a Tracer3210AN (12/24V, 30A). Readings outside
# these come from corrupt frames on the shared RS485 bus and are discarded (sensor unavailable).
VALID_RANGES = {
    "pv_voltage": (0, 100),
    "pv_current": (0, 40),
    "pv_power": (0, 1000),
    "battery_voltage": (5, 35),
    "battery_current": (0, 40),
    "battery_soc": (0, 100),
    "battery_temp": (-40, 100),
    "load_voltage": (0, 35),
    "load_current": (0, 40),
    "load_power": (0, 1000),
    "device_temp": (-40, 120),
}

# Raw register values meaning "no data"; never a real reading
INVALID_RAW_VALUES = (0xFFFF, 0xFFFFFFFF)

# A sudden exact zero from a previously non-zero reading is re-read once before it is
# trusted (bus glitches often return zeros; real drops to zero, e.g. at dusk, persist).
CONFIRM_ZERO_PARAMETERS = (
    "pv_voltage",
    "pv_current",
    "pv_power",
    "battery_current",
    "battery_voltage",
    "load_voltage",
)
