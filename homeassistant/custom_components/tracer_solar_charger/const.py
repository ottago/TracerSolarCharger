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

# Sensor types and their properties
SENSOR_TYPES = {
    # PV Parameters
    "pv_voltage": {
        "name": "PV Voltage",
        "address": 0x3100,
        "unit": "V",
        "scale": 0.01,
        "device_class": "voltage",
        "state_class": "measurement",
        "category": "pv",
        "icon": "mdi:solar-panel",
    },
    "pv_current": {
        "name": "PV Current",
        "address": 0x3101,
        "unit": "A",
        "scale": 0.01,
        "device_class": "current",
        "state_class": "measurement",
        "category": "pv",
        "icon": "mdi:current-dc",
    },
    "pv_power": {
        "name": "PV Power",
        "address": 0x3102,  # Low word, will combine with high word
        "unit": "W",
        "scale": 0.01,
        "device_class": "power",
        "state_class": "measurement",
        "category": "pv",
        "icon": "mdi:solar-power",
        "combine_registers": True,
        "high_address": 0x3103,
    },
    
    # Battery Parameters
    "battery_voltage": {
        "name": "Battery Voltage",
        "address": 0x3104,
        "unit": "V",
        "scale": 0.01,
        "device_class": "voltage",
        "state_class": "measurement",
        "category": "battery",
        "icon": "mdi:battery",
    },
    "battery_current": {
        "name": "Battery Current",
        "address": 0x3105,
        "unit": "A",
        "scale": 0.01,
        "device_class": "current",
        "state_class": "measurement",
        "category": "battery",
        "icon": "mdi:current-dc",
    },
    "battery_power": {
        "name": "Battery Power",
        "address": 0x3106,
        "unit": "W",
        "scale": 0.01,
        "device_class": "power",
        "state_class": "measurement",
        "category": "battery",
        "icon": "mdi:battery-charging",
        "combine_registers": True,
        "high_address": 0x3107,
    },
    "battery_soc": {
        "name": "Battery State of Charge",
        "address": 0x311A,
        "unit": "%",
        "scale": 1,
        "device_class": "battery",
        "state_class": "measurement",
        "category": "battery",
        "icon": "mdi:battery-50",
    },
    "battery_temp": {
        "name": "Battery Temperature",
        "address": 0x3110,
        "unit": "°C",
        "scale": 0.01,
        "offset": -273.15,
        "device_class": "temperature",
        "state_class": "measurement",
        "category": "battery",
        "icon": "mdi:thermometer",
    },
    
    # Load Parameters
    "load_voltage": {
        "name": "Load Voltage",
        "address": 0x310C,
        "unit": "V",
        "scale": 0.01,
        "device_class": "voltage",
        "state_class": "measurement",
        "category": "load",
        "icon": "mdi:flash",
    },
    "load_current": {
        "name": "Load Current",
        "address": 0x310D,
        "unit": "A",
        "scale": 0.01,
        "device_class": "current",
        "state_class": "measurement",
        "category": "load",
        "icon": "mdi:current-ac",
    },
    "load_power": {
        "name": "Load Power",
        "address": 0x310A,
        "unit": "W",
        "scale": 0.01,
        "device_class": "power",
        "state_class": "measurement",
        "category": "load",
        "icon": "mdi:lightning-bolt",
        "combine_registers": True,
        "high_address": 0x310B,
    },
    
    # System Parameters
    "device_temp": {
        "name": "Device Temperature",
        "address": 0x3111,
        "unit": "°C",
        "scale": 0.01,
        "offset": -273.15,
        "device_class": "temperature",
        "state_class": "measurement",
        "category": "system",
        "icon": "mdi:thermometer",
    },
    "heat_sink_temp": {
        "name": "Heat Sink Temperature",
        "address": 0x3113,
        "unit": "°C",
        "scale": 0.01,
        "offset": -273.15,
        "device_class": "temperature",
        "state_class": "measurement",
        "category": "system",
        "icon": "mdi:thermometer",
    },
    
    # Status Parameters
    "battery_status": {
        "name": "Battery Status",
        "address": 0x3200,
        "unit": "",
        "scale": 1,
        "category": "status",
        "icon": "mdi:battery-alert",
        "type": "status",
    },
    "charging_status": {
        "name": "Charging Status",
        "address": 0x3201,
        "unit": "",
        "scale": 1,
        "category": "status",
        "icon": "mdi:battery-charging",
        "type": "status",
    },
    "load_status": {
        "name": "Load Status",
        "address": 0x3202,
        "unit": "",
        "scale": 1,
        "category": "status",
        "icon": "mdi:power-plug",
        "type": "status",
    },
    
    # Energy Statistics
    "energy_generated_today": {
        "name": "Energy Generated Today",
        "address": 0x3306,
        "unit": "kWh",
        "scale": 0.01,
        "device_class": "energy",
        "state_class": "total_increasing",
        "category": "statistics",
        "icon": "mdi:solar-power",
        "combine_registers": True,
        "high_address": 0x3307,
    },
    "energy_consumed_today": {
        "name": "Energy Consumed Today",
        "address": 0x3304,
        "unit": "kWh",
        "scale": 0.01,
        "device_class": "energy",
        "state_class": "total_increasing",
        "category": "statistics",
        "icon": "mdi:lightning-bolt",
        "combine_registers": True,
        "high_address": 0x3305,
    },
    "energy_generated_total": {
        "name": "Total Energy Generated",
        "address": 0x3308,
        "unit": "kWh",
        "scale": 0.01,
        "device_class": "energy",
        "state_class": "total_increasing",
        "category": "statistics",
        "icon": "mdi:counter",
        "combine_registers": True,
        "high_address": 0x3309,
    },
    "max_battery_voltage_today": {
        "name": "Max Battery Voltage Today",
        "address": 0x3302,
        "unit": "V",
        "scale": 0.01,
        "device_class": "voltage",
        "state_class": "measurement",
        "category": "statistics",
        "icon": "mdi:battery-arrow-up",
    },
    "min_battery_voltage_today": {
        "name": "Min Battery Voltage Today",
        "address": 0x3303,
        "unit": "V",
        "scale": 0.01,
        "device_class": "voltage",
        "state_class": "measurement",
        "category": "statistics",
        "icon": "mdi:battery-arrow-down",
    },
    "battery_full_charges": {
        "name": "Battery Full Charges",
        "address": 0x330C,
        "unit": "cycles",
        "scale": 1,
        "state_class": "total_increasing",
        "category": "statistics",
        "icon": "mdi:battery-sync",
    },
    "operating_days": {
        "name": "Operating Days",
        "address": 0x330A,
        "unit": "days",
        "scale": 1,
        "state_class": "total_increasing",
        "category": "statistics",
        "icon": "mdi:calendar-clock",
    },
    
    # Configuration Parameters (read-only in HA)
    "battery_type": {
        "name": "Battery Type",
        "address": 0x9000,
        "unit": "",
        "scale": 1,
        "category": "config",
        "icon": "mdi:battery-outline",
        "type": "enum",
        "enum_values": {0: "User Defined", 1: "Sealed", 2: "GEL", 3: "Flooded", 4: "LiFePO4"},
    },
    "battery_capacity": {
        "name": "Battery Capacity",
        "address": 0x9001,
        "unit": "Ah",
        "scale": 1,
        "category": "config",
        "icon": "mdi:battery-outline",
    },
    "float_voltage": {
        "name": "Float Voltage Setting",
        "address": 0x9008,
        "unit": "V",
        "scale": 0.01,
        "device_class": "voltage",
        "category": "config",
        "icon": "mdi:sine-wave",
    },
    "low_voltage_disconnect": {
        "name": "Low Voltage Disconnect Setting",
        "address": 0x900D,
        "unit": "V",
        "scale": 0.01,
        "device_class": "voltage",
        "category": "config",
        "icon": "mdi:battery-alert-variant",
    },
}

# Status bit definitions for status sensors
BATTERY_STATUS_BITS = {
    0: "Normal",
    1: "Over Temperature",
    2: "Low Temperature", 
    3: "Over Voltage",
    4: "Under Voltage",
    5: "Over Current",
    6: "Over Discharge",
    7: "Battery Inner Resistance Abnormal",
    8: "Wrong Identification for Rated Voltage"
}

CHARGING_STATUS_BITS = {
    0: "Charging Deactivated",
    1: "Charging Activated", 
    2: "MPPT Charging Mode",
    3: "Equalizing Charging Mode",
    4: "Boost Charging Mode",
    5: "Floating Charging Mode",
    6: "Current Limiting"
}

LOAD_STATUS_BITS = {
    0: "Load Disconnected",
    1: "Load Connected",
    2: "Output Over Voltage",
    3: "Boost Over Voltage", 
    4: "High Voltage Side Short Circuit",
    5: "Input Over Voltage",
    6: "Output Over Current",
    7: "Input Over Current"
}
