"""Constants for the Tracer Solar Charger integration."""

DOMAIN = "tracer_solar_charger"

# Configuration keys
CONF_SLAVE_ID = "slave_id"
CONF_BAUDRATE = "baudrate"

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
