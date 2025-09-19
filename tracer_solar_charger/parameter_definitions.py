#!/usr/bin/env python3
"""
Comprehensive Parameter Definitions for Tracer3210AN Solar Charger
Maps all discovered registers to meaningful parameter names, units, and scaling
"""

# Real-time Data Parameters (Input Registers - Function Code 04)
REALTIME_PARAMETERS = {
    # PV (Solar Panel) Data - 0x3100 series
    0x3100: {
        'name': 'pv_voltage',
        'description': 'PV Array Voltage',
        'unit': 'V',
        'scale': 0.01,
        'category': 'pv'
    },
    0x3101: {
        'name': 'pv_current',
        'description': 'PV Array Current',
        'unit': 'A',
        'scale': 0.01,
        'category': 'pv'
    },
    0x3102: {
        'name': 'pv_power_low',
        'description': 'PV Power (Low Word)',
        'unit': 'W',
        'scale': 0.01,
        'category': 'pv'
    },
    0x3103: {
        'name': 'pv_power_high',
        'description': 'PV Power (High Word)',
        'unit': 'W',
        'scale': 0.01,
        'category': 'pv'
    },
    
    # Combined PV Power (calculated from low + high words)
    0x3102: {
        'name': 'pv_power',
        'description': 'PV Power',
        'unit': 'W',
        'scale': 0.01,
        'category': 'pv',
        'combine_registers': True,
        'high_address': 0x3103
    },
    0x3104: {
        'name': 'battery_voltage',
        'description': 'Battery Voltage',
        'unit': 'V',
        'scale': 0.01,
        'category': 'battery'
    },
    0x3105: {
        'name': 'battery_current',
        'description': 'Battery Charging Current',
        'unit': 'A',
        'scale': 0.01,
        'category': 'battery'
    },
    0x3106: {
        'name': 'battery_power_low',
        'description': 'Battery Power (Low Word)',
        'unit': 'W',
        'scale': 0.01,
        'category': 'battery'
    },
    0x3107: {
        'name': 'battery_power_high',
        'description': 'Battery Power (High Word)',
        'unit': 'W',
        'scale': 0.01,
        'category': 'battery'
    },
    0x3108: {
        'name': 'load_voltage',
        'description': 'Load Voltage',
        'unit': 'V',
        'scale': 0.01,
        'category': 'load'
    },
    0x3109: {
        'name': 'load_current',
        'description': 'Load Current',
        'unit': 'A',
        'scale': 0.01,
        'category': 'load'
    },
    0x310A: {
        'name': 'load_power_low',
        'description': 'Load Power (Low Word)',
        'unit': 'W',
        'scale': 0.01,
        'category': 'load'
    },
    0x310B: {
        'name': 'load_power_high',
        'description': 'Load Power (High Word)',
        'unit': 'W',
        'scale': 0.01,
        'category': 'load'
    },
    
    # Combined Load Power (calculated from low + high words)  
    0x310A: {
        'name': 'load_power',
        'description': 'Load Power',
        'unit': 'W',
        'scale': 0.01,
        'category': 'load',
        'combine_registers': True,
        'high_address': 0x310B
    },
    0x310C: {
        'name': 'battery_voltage_2',
        'description': 'Battery Voltage (Secondary)',
        'unit': 'V',
        'scale': 0.01,
        'category': 'battery'
    },
    0x310D: {
        'name': 'load_current_2',
        'description': 'Load Current (Secondary)',
        'unit': 'A',
        'scale': 0.01,
        'category': 'load'
    },
    0x310E: {
        'name': 'load_power_combined',
        'description': 'Load Power Combined',
        'unit': 'W',
        'scale': 0.01,
        'category': 'load'
    },
    0x310F: {
        'name': 'reserved_310f',
        'description': 'Reserved Register 310F',
        'unit': '',
        'scale': 1,
        'category': 'system'
    },
    0x3110: {
        'name': 'battery_temp',
        'description': 'Battery Temperature',
        'unit': '°C',
        'scale': 0.01,
        'offset': 0.0,
        'category': 'battery'
    },
    0x3111: {
        'name': 'device_temp',
        'description': 'Device Temperature',
        'unit': '°C',
        'scale': 0.01,
        'offset': 0.0,
        'category': 'system'
    },
    0x3112: {
        'name': 'ambient_temp',
        'description': 'Ambient Temperature',
        'unit': '°C',
        'scale': 0.01,
        'offset': 0.0,
        'category': 'system'
    },
    0x3113: {
        'name': 'heat_sink_temp',
        'description': 'Heat Sink Temperature',
        'unit': '°C',
        'scale': 0.01,
        'offset': 0.0,
        'category': 'system'
    },
    0x311A: {
        'name': 'battery_soc',
        'description': 'Battery State of Charge',
        'unit': '%',
        'scale': 1,
        'category': 'battery'
    },
    0x311B: {
        'name': 'remote_temp',
        'description': 'Remote Temperature Sensor',
        'unit': '°C',
        'scale': 0.01,
        'category': 'system'
    },
    0x311D: {
        'name': 'battery_voltage_min',
        'description': 'Battery Minimum Voltage',
        'unit': 'V',
        'scale': 0.01,
        'category': 'battery'
    },
    
    # Battery Status - 0x3200 series
    0x3200: {
        'name': 'battery_status',
        'description': 'Battery Status',
        'unit': '',
        'scale': 1,
        'category': 'battery',
        'type': 'status'
    },
    0x3201: {
        'name': 'charging_equipment_status',
        'description': 'Charging Equipment Status',
        'unit': '',
        'scale': 1,
        'category': 'system',
        'type': 'status'
    },
    0x3202: {
        'name': 'discharging_equipment_status',
        'description': 'Discharging Equipment Status',
        'unit': '',
        'scale': 1,
        'category': 'system',
        'type': 'status'
    },
    
    # Statistics - 0x3300 series (Daily/Historical Data)
    0x3300: {
        'name': 'max_pv_voltage_today',
        'description': 'Maximum PV Voltage Today',
        'unit': 'V',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3301: {
        'name': 'min_pv_voltage_today',
        'description': 'Minimum PV Voltage Today',
        'unit': 'V',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3302: {
        'name': 'max_battery_voltage_today',
        'description': 'Maximum Battery Voltage Today',
        'unit': 'V',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3303: {
        'name': 'min_battery_voltage_today',
        'description': 'Minimum Battery Voltage Today',
        'unit': 'V',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3304: {
        'name': 'consumed_energy_today_low',
        'description': 'Consumed Energy Today (Low Word)',
        'unit': 'kWh',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3305: {
        'name': 'consumed_energy_today_high',
        'description': 'Consumed Energy Today (High Word)',
        'unit': 'kWh',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3306: {
        'name': 'generated_energy_today_low',
        'description': 'Generated Energy Today (Low Word)',
        'unit': 'kWh',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3307: {
        'name': 'generated_energy_today_high',
        'description': 'Generated Energy Today (High Word)',
        'unit': 'kWh',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3308: {
        'name': 'generated_energy_total_low',
        'description': 'Total Generated Energy (Low Word)',
        'unit': 'kWh',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3309: {
        'name': 'generated_energy_total_high',
        'description': 'Total Generated Energy (High Word)',
        'unit': 'kWh',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x330A: {
        'name': 'operating_days_total',
        'description': 'Total Operating Days',
        'unit': 'days',
        'scale': 1,
        'category': 'statistics'
    },
    0x330B: {
        'name': 'battery_over_discharges',
        'description': 'Battery Over-discharge Count',
        'unit': 'count',
        'scale': 1,
        'category': 'statistics'
    },
    0x330C: {
        'name': 'battery_full_charges',
        'description': 'Battery Full Charge Count',
        'unit': 'count',
        'scale': 1,
        'category': 'statistics'
    },
    0x330D: {
        'name': 'charging_amp_hours_low',
        'description': 'Charging Amp-hours (Low Word)',
        'unit': 'Ah',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x330E: {
        'name': 'charging_amp_hours_high',
        'description': 'Charging Amp-hours (High Word)',
        'unit': 'Ah',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x330F: {
        'name': 'discharging_amp_hours_low',
        'description': 'Discharging Amp-hours (Low Word)',
        'unit': 'Ah',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3310: {
        'name': 'discharging_amp_hours_high',
        'description': 'Discharging Amp-hours (High Word)',
        'unit': 'Ah',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3311: {
        'name': 'cumulative_power_generation_low',
        'description': 'Cumulative Power Generation (Low Word)',
        'unit': 'kWh',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3312: {
        'name': 'cumulative_power_generation_high',
        'description': 'Cumulative Power Generation (High Word)',
        'unit': 'kWh',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3313: {
        'name': 'cumulative_power_consumption_low',
        'description': 'Cumulative Power Consumption (Low Word)',
        'unit': 'kWh',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3314: {
        'name': 'cumulative_power_consumption_high',
        'description': 'Cumulative Power Consumption (High Word)',
        'unit': 'kWh',
        'scale': 0.01,
        'category': 'statistics'
    },
    0x3315: {
        'name': 'load_status',
        'description': 'Load Status',
        'unit': '',
        'scale': 1,
        'category': 'load',
        'type': 'status'
    },
    0x3316: {
        'name': 'street_light_status',
        'description': 'Street Light Status',
        'unit': '',
        'scale': 1,
        'category': 'load',
        'type': 'status'
    },
    0x3317: {
        'name': 'street_light_brightness',
        'description': 'Street Light Brightness',
        'unit': '%',
        'scale': 1,
        'category': 'load'
    },
    0x3318: {
        'name': 'charging_state',
        'description': 'Charging State',
        'unit': '',
        'scale': 1,
        'category': 'battery',
        'type': 'status'
    },
    0x3319: {
        'name': 'fault_status',
        'description': 'Fault Status',
        'unit': '',
        'scale': 1,
        'category': 'system',
        'type': 'status'
    },
    0x331A: {
        'name': 'target_voltage',
        'description': 'Target Voltage',
        'unit': 'V',
        'scale': 0.01,
        'category': 'battery'
    },
    0x331B: {
        'name': 'period_1_time',
        'description': 'Period 1 Time',
        'unit': 'min',
        'scale': 1,
        'category': 'system'
    },
    0x331C: {
        'name': 'period_2_time',
        'description': 'Period 2 Time',
        'unit': 'min',
        'scale': 1,
        'category': 'system'
    },
    0x331D: {
        'name': 'period_1_power',
        'description': 'Period 1 Power',
        'unit': '%',
        'scale': 1,
        'category': 'system'
    },
    0x331E: {
        'name': 'period_2_power',
        'description': 'Period 2 Power',
        'unit': '%',
        'scale': 1,
        'category': 'system'
    },
}

# Configuration Parameters (Holding Registers - Function Code 03)
CONFIG_PARAMETERS = {
    # System Settings - 0x9000 series
    0x9000: {
        'name': 'battery_type',
        'description': 'Battery Type',
        'unit': '',
        'scale': 1,
        'category': 'config',
        'type': 'enum',
        'values': {0: 'User Defined', 1: 'Sealed', 2: 'GEL', 3: 'Flooded', 4: 'LiFePO4'}
    },
    0x9001: {
        'name': 'battery_capacity',
        'description': 'Battery Capacity',
        'unit': 'Ah',
        'scale': 1,
        'category': 'config'
    },
    0x9002: {
        'name': 'temperature_compensation',
        'description': 'Temperature Compensation Coefficient',
        'unit': 'mV/°C/2V',
        'scale': 1,
        'category': 'config'
    },
    0x9003: {
        'name': 'high_voltage_disconnect',
        'description': 'High Voltage Disconnect',
        'unit': 'V',
        'scale': 0.01,
        'category': 'config'
    },
    0x9004: {
        'name': 'charging_limit_voltage',
        'description': 'Charging Limit Voltage',
        'unit': 'V',
        'scale': 0.01,
        'category': 'config'
    },
    0x9005: {
        'name': 'over_voltage_reconnect',
        'description': 'Over Voltage Reconnect',
        'unit': 'V',
        'scale': 0.01,
        'category': 'config'
    },
    0x9006: {
        'name': 'equalization_voltage',
        'description': 'Equalization Voltage',
        'unit': 'V',
        'scale': 0.01,
        'category': 'config'
    },
    0x9007: {
        'name': 'boost_voltage',
        'description': 'Boost Voltage',
        'unit': 'V',
        'scale': 0.01,
        'category': 'config'
    },
    0x9008: {
        'name': 'float_voltage',
        'description': 'Float Voltage',
        'unit': 'V',
        'scale': 0.01,
        'category': 'config'
    },
    0x9009: {
        'name': 'boost_reconnect_voltage',
        'description': 'Boost Reconnect Voltage',
        'unit': 'V',
        'scale': 0.01,
        'category': 'config'
    },
    0x900A: {
        'name': 'low_voltage_reconnect',
        'description': 'Low Voltage Reconnect',
        'unit': 'V',
        'scale': 0.01,
        'category': 'config'
    },
    0x900B: {
        'name': 'under_voltage_recover',
        'description': 'Under Voltage Recover',
        'unit': 'V',
        'scale': 0.01,
        'category': 'config'
    },
    0x900C: {
        'name': 'under_voltage_warning',
        'description': 'Under Voltage Warning',
        'unit': 'V',
        'scale': 0.01,
        'category': 'config'
    },
    0x900D: {
        'name': 'low_voltage_disconnect',
        'description': 'Low Voltage Disconnect',
        'unit': 'V',
        'scale': 0.01,
        'category': 'config'
    },
    0x900E: {
        'name': 'discharging_limit_voltage',
        'description': 'Discharging Limit Voltage',
        'unit': 'V',
        'scale': 0.01,
        'category': 'config'
    },
    0x9010: {
        'name': 'real_time_clock_1',
        'description': 'Real Time Clock (Seconds/Minutes)',
        'unit': '',
        'scale': 1,
        'category': 'config'
    },
    0x9011: {
        'name': 'real_time_clock_2',
        'description': 'Real Time Clock (Hours/Day)',
        'unit': '',
        'scale': 1,
        'category': 'config'
    },
    0x9013: {
        'name': 'equalization_duration',
        'description': 'Equalization Duration',
        'unit': 'min',
        'scale': 1,
        'category': 'config'
    },
    0x9014: {
        'name': 'boost_duration',
        'description': 'Boost Duration',
        'unit': 'min',
        'scale': 1,
        'category': 'config'
    },
    0x9015: {
        'name': 'discharge_percentage',
        'description': 'Discharge Percentage',
        'unit': '%',
        'scale': 1,
        'category': 'config'
    },
    0x9016: {
        'name': 'charging_percentage',
        'description': 'Charging Percentage',
        'unit': '%',
        'scale': 1,
        'category': 'config'
    },
    0x9017: {
        'name': 'management_mode',
        'description': 'Management Mode',
        'unit': '',
        'scale': 1,
        'category': 'config',
        'type': 'bitfield'
    },
}

# Status bit definitions
BATTERY_STATUS_BITS = {
    0: 'Normal',
    1: 'Over Temperature',
    2: 'Low Temperature',
    3: 'Over Voltage',
    4: 'Under Voltage',
    5: 'Over Current',
    6: 'Over Discharge',
    7: 'Battery Inner Resistance Abnormal',
    8: 'Wrong Identification for Rated Voltage'
}

CHARGING_STATUS_BITS = {
    0: 'Charging Deactivated',
    1: 'Charging Activated',
    2: 'MPPT Charging Mode',
    3: 'Equalizing Charging Mode',
    4: 'Boost Charging Mode',
    5: 'Floating Charging Mode',
    6: 'Current Limiting'
}

DISCHARGING_STATUS_BITS = {
    0: 'Discharging Deactivated',
    1: 'Discharging Activated',
    2: 'Output Over Voltage',
    3: 'Boost Over Voltage',
    4: 'High Voltage Side Short Circuit',
    5: 'Input Over Voltage',
    6: 'Output Over Current',
    7: 'Input Over Current'
}

def get_parameter_info(address, is_holding_register=False):
    """Get parameter information for a given register address"""
    if is_holding_register:
        return CONFIG_PARAMETERS.get(address)
    else:
        return REALTIME_PARAMETERS.get(address)

def format_value(address, raw_value, is_holding_register=False):
    """Format raw register value according to parameter definition"""
    param_info = get_parameter_info(address, is_holding_register)
    
    if not param_info:
        return {
            'raw': raw_value,
            'formatted': raw_value,
            'unit': '',
            'description': f'Unknown Register 0x{address:04X}'
        }
    
    # Apply scaling
    scaled_value = raw_value * param_info.get('scale', 1)
    
    # Apply offset if present (for temperature conversions)
    if 'offset' in param_info:
        scaled_value += param_info['offset']
    
    # Handle special formatting
    if param_info.get('type') == 'status':
        formatted_value = format_status_value(address, raw_value)
    elif param_info.get('type') == 'enum':
        formatted_value = param_info.get('values', {}).get(raw_value, f'Unknown ({raw_value})')
    else:
        # Format numeric values with appropriate decimal places
        if isinstance(scaled_value, float):
            # For floating-point values, format to 2 decimal places
            formatted_value = round(scaled_value, 2)
        else:
            # For integer values, keep as-is
            formatted_value = scaled_value
    
    return {
        'name': param_info['name'],
        'description': param_info['description'],
        'raw': raw_value,
        'formatted': formatted_value,
        'unit': param_info['unit'],
        'category': param_info['category']
    }

def format_status_value(address, raw_value):
    """Format status register values as human-readable text"""
    if address == 0x3200:  # Battery Status
        return format_bitfield(raw_value, BATTERY_STATUS_BITS)
    elif address == 0x3201:  # Charging Equipment Status
        return format_bitfield(raw_value, CHARGING_STATUS_BITS)
    elif address == 0x3202:  # Discharging Equipment Status
        return format_bitfield(raw_value, DISCHARGING_STATUS_BITS)
    else:
        return raw_value

def format_bitfield(value, bit_definitions):
    """Format a bitfield value using bit definitions"""
    active_bits = []
    for bit, description in bit_definitions.items():
        if value & (1 << bit):
            active_bits.append(description)
    
    return active_bits if active_bits else ['Normal']

def get_all_parameters():
    """Get all available parameters organized by category"""
    all_params = {}
    
    # Add real-time parameters
    for addr, info in REALTIME_PARAMETERS.items():
        category = info['category']
        if category not in all_params:
            all_params[category] = []
        all_params[category].append({
            'address': addr,
            'hex_address': f'0x{addr:04X}',
            'function_code': 4,
            **info
        })
    
    # Add configuration parameters
    for addr, info in CONFIG_PARAMETERS.items():
        category = info['category']
        if category not in all_params:
            all_params[category] = []
        all_params[category].append({
            'address': addr,
            'hex_address': f'0x{addr:04X}',
            'function_code': 3,
            **info
        })
    
    return all_params

# Create unified PARAMETERS dictionary for easy access by name
PARAMETERS = {}

# Add real-time parameters
for addr, info in REALTIME_PARAMETERS.items():
    param_name = info['name']
    PARAMETERS[param_name] = {
        'address': addr,
        'function_code': 4,
        **info
    }

# Add configuration parameters  
for addr, info in CONFIG_PARAMETERS.items():
    param_name = info['name']
    PARAMETERS[param_name] = {
        'address': addr,
        'function_code': 3,
        **info
    }

if __name__ == "__main__":
    # Test the parameter definitions
    params = get_all_parameters()
    print("Available Parameter Categories:")
    for category, param_list in params.items():
        print(f"  {category.title()}: {len(param_list)} parameters")
    
    print(f"\nTotal Parameters: {sum(len(p) for p in params.values())}")
    print(f"Parameters by name: {len(PARAMETERS)}")
