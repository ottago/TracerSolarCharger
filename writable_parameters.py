#!/usr/bin/env python3
"""
Writable Parameter Definitions for Tracer3210AN Solar Charger
Defines which parameters can be written and their validation rules
"""

from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass

@dataclass
class WritableParameter:
    """Definition of a writable parameter"""
    address: int
    name: str
    description: str
    unit: str
    scale: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    valid_values: Optional[List[Union[int, str]]] = None
    warning_message: Optional[str] = None
    category: str = 'config'
    
    def validate_value(self, value: Union[int, float, str]) -> tuple[bool, str, int]:
        """
        Validate a value for this parameter
        Returns: (is_valid, error_message, raw_modbus_value)
        """
        try:
            # Handle enum values
            if self.valid_values and isinstance(value, str):
                if value in self.valid_values:
                    raw_value = self.valid_values.index(value)
                else:
                    return False, f"Invalid value '{value}'. Valid options: {self.valid_values}", 0
            else:
                # Convert to numeric
                if isinstance(value, str):
                    numeric_value = float(value)
                else:
                    numeric_value = float(value)
                
                # Check range
                if self.min_value is not None and numeric_value < self.min_value:
                    return False, f"Value {numeric_value} below minimum {self.min_value} {self.unit}", 0
                
                if self.max_value is not None and numeric_value > self.max_value:
                    return False, f"Value {numeric_value} above maximum {self.max_value} {self.unit}", 0
                
                # Convert to raw Modbus value
                raw_value = int(numeric_value / self.scale)
            
            return True, "", raw_value
            
        except ValueError as e:
            return False, f"Invalid numeric value: {e}", 0

# Writable configuration parameters
WRITABLE_PARAMETERS = {
    # Battery Configuration
    0x9000: WritableParameter(
        address=0x9000,
        name='battery_type',
        description='Battery Type',
        unit='',
        scale=1,
        valid_values=['User Defined', 'Sealed', 'GEL', 'Flooded', 'LiFePO4'],
        warning_message='Changing battery type will reset voltage thresholds to defaults',
        category='battery_config'
    ),
    
    0x9001: WritableParameter(
        address=0x9001,
        name='battery_capacity',
        description='Battery Capacity',
        unit='Ah',
        scale=1,
        min_value=10,
        max_value=1000,
        warning_message='Ensure this matches your actual battery capacity',
        category='battery_config'
    ),
    
    0x9002: WritableParameter(
        address=0x9002,
        name='temperature_compensation',
        description='Temperature Compensation Coefficient',
        unit='mV/°C/2V',
        scale=1,
        min_value=0,
        max_value=500,
        category='battery_config'
    ),
    
    # Voltage Thresholds
    0x9003: WritableParameter(
        address=0x9003,
        name='high_voltage_disconnect',
        description='High Voltage Disconnect',
        unit='V',
        scale=0.01,
        min_value=12.0,
        max_value=17.0,
        warning_message='CRITICAL: This protects against overcharging. Set carefully!',
        category='voltage_protection'
    ),
    
    0x9004: WritableParameter(
        address=0x9004,
        name='charging_limit_voltage',
        description='Charging Limit Voltage',
        unit='V',
        scale=0.01,
        min_value=12.0,
        max_value=17.0,
        warning_message='Should be slightly below high voltage disconnect',
        category='voltage_protection'
    ),
    
    0x9005: WritableParameter(
        address=0x9005,
        name='over_voltage_reconnect',
        description='Over Voltage Reconnect',
        unit='V',
        scale=0.01,
        min_value=12.0,
        max_value=17.0,
        category='voltage_protection'
    ),
    
    0x9006: WritableParameter(
        address=0x9006,
        name='equalization_voltage',
        description='Equalization Voltage',
        unit='V',
        scale=0.01,
        min_value=12.0,
        max_value=17.0,
        warning_message='Only for flooded batteries. Not recommended for sealed/LiFePO4',
        category='charging_voltages'
    ),
    
    0x9007: WritableParameter(
        address=0x9007,
        name='boost_voltage',
        description='Boost Voltage',
        unit='V',
        scale=0.01,
        min_value=12.0,
        max_value=17.0,
        category='charging_voltages'
    ),
    
    0x9008: WritableParameter(
        address=0x9008,
        name='float_voltage',
        description='Float Voltage',
        unit='V',
        scale=0.01,
        min_value=12.0,
        max_value=16.0,
        category='charging_voltages'
    ),
    
    0x9009: WritableParameter(
        address=0x9009,
        name='boost_reconnect_voltage',
        description='Boost Reconnect Voltage',
        unit='V',
        scale=0.01,
        min_value=10.0,
        max_value=15.0,
        category='charging_voltages'
    ),
    
    0x900A: WritableParameter(
        address=0x900A,
        name='low_voltage_reconnect',
        description='Low Voltage Reconnect',
        unit='V',
        scale=0.01,
        min_value=10.0,
        max_value=15.0,
        category='load_protection'
    ),
    
    0x900B: WritableParameter(
        address=0x900B,
        name='under_voltage_recover',
        description='Under Voltage Recover',
        unit='V',
        scale=0.01,
        min_value=10.0,
        max_value=15.0,
        category='load_protection'
    ),
    
    0x900C: WritableParameter(
        address=0x900C,
        name='under_voltage_warning',
        description='Under Voltage Warning',
        unit='V',
        scale=0.01,
        min_value=10.0,
        max_value=15.0,
        category='load_protection'
    ),
    
    0x900D: WritableParameter(
        address=0x900D,
        name='low_voltage_disconnect',
        description='Low Voltage Disconnect',
        unit='V',
        scale=0.01,
        min_value=9.0,
        max_value=14.0,
        warning_message='CRITICAL: This protects against deep discharge. Set carefully!',
        category='load_protection'
    ),
    
    0x900E: WritableParameter(
        address=0x900E,
        name='discharging_limit_voltage',
        description='Discharging Limit Voltage',
        unit='V',
        scale=0.01,
        min_value=9.0,
        max_value=14.0,
        warning_message='Should be slightly below low voltage disconnect',
        category='load_protection'
    ),
    
    # Timing Parameters
    0x9013: WritableParameter(
        address=0x9013,
        name='equalization_duration',
        description='Equalization Duration',
        unit='min',
        scale=1,
        min_value=0,
        max_value=300,
        warning_message='Only for flooded batteries. Set to 0 for sealed/LiFePO4',
        category='charging_timing'
    ),
    
    0x9014: WritableParameter(
        address=0x9014,
        name='boost_duration',
        description='Boost Duration',
        unit='min',
        scale=1,
        min_value=10,
        max_value=300,
        category='charging_timing'
    ),
    
    0x9015: WritableParameter(
        address=0x9015,
        name='discharge_percentage',
        description='Discharge Percentage',
        unit='%',
        scale=1,
        min_value=20,
        max_value=100,
        category='load_control'
    ),
    
    0x9016: WritableParameter(
        address=0x9016,
        name='charging_percentage',
        description='Charging Percentage',
        unit='%',
        scale=1,
        min_value=0,
        max_value=100,
        category='load_control'
    ),
}

# Battery type specific recommended settings
BATTERY_TYPE_SETTINGS = {
    'LiFePO4': {
        'high_voltage_disconnect': 14.6,
        'charging_limit_voltage': 14.4,
        'boost_voltage': 14.4,
        'float_voltage': 13.8,
        'low_voltage_disconnect': 11.1,
        'equalization_voltage': 14.4,  # Same as boost for LiFePO4
        'equalization_duration': 0,    # No equalization needed
        'temperature_compensation': 0   # LiFePO4 doesn't need temp compensation
    },
    'Sealed': {
        'high_voltage_disconnect': 15.0,
        'charging_limit_voltage': 14.8,
        'boost_voltage': 14.4,
        'float_voltage': 13.8,
        'low_voltage_disconnect': 11.1,
        'equalization_voltage': 14.6,
        'equalization_duration': 120,
        'temperature_compensation': 300
    },
    'GEL': {
        'high_voltage_disconnect': 15.0,
        'charging_limit_voltage': 14.8,
        'boost_voltage': 14.2,
        'float_voltage': 13.8,
        'low_voltage_disconnect': 11.1,
        'equalization_voltage': 14.4,
        'equalization_duration': 120,
        'temperature_compensation': 300
    },
    'Flooded': {
        'high_voltage_disconnect': 15.5,
        'charging_limit_voltage': 15.0,
        'boost_voltage': 14.8,
        'float_voltage': 13.8,
        'low_voltage_disconnect': 11.1,
        'equalization_voltage': 15.5,
        'equalization_duration': 120,
        'temperature_compensation': 300
    }
}

def get_writable_parameter(address_or_name: Union[int, str]) -> Optional[WritableParameter]:
    """Get writable parameter by address or name"""
    if isinstance(address_or_name, int):
        return WRITABLE_PARAMETERS.get(address_or_name)
    else:
        for param in WRITABLE_PARAMETERS.values():
            if param.name == address_or_name:
                return param
    return None

def get_writable_parameters_by_category(category: Optional[str] = None) -> Dict[int, WritableParameter]:
    """Get writable parameters filtered by category"""
    if category:
        return {addr: param for addr, param in WRITABLE_PARAMETERS.items() 
                if param.category == category}
    return WRITABLE_PARAMETERS

def get_writable_categories() -> List[str]:
    """Get list of writable parameter categories"""
    categories = set()
    for param in WRITABLE_PARAMETERS.values():
        categories.add(param.category)
    return sorted(list(categories))

def validate_voltage_sequence(settings: Dict[str, float]) -> List[str]:
    """Validate that voltage settings are in correct sequence"""
    warnings = []
    
    # Check charging voltage sequence
    if 'high_voltage_disconnect' in settings and 'charging_limit_voltage' in settings:
        if settings['charging_limit_voltage'] >= settings['high_voltage_disconnect']:
            warnings.append("Charging limit voltage should be below high voltage disconnect")
    
    if 'boost_voltage' in settings and 'float_voltage' in settings:
        if settings['float_voltage'] >= settings['boost_voltage']:
            warnings.append("Float voltage should be below boost voltage")
    
    # Check discharge voltage sequence
    if 'low_voltage_disconnect' in settings and 'under_voltage_warning' in settings:
        if settings['under_voltage_warning'] <= settings['low_voltage_disconnect']:
            warnings.append("Under voltage warning should be above low voltage disconnect")
    
    return warnings

if __name__ == "__main__":
    # Test the parameter definitions
    print("Writable Parameters:")
    for category in get_writable_categories():
        params = get_writable_parameters_by_category(category)
        print(f"\n{category.upper().replace('_', ' ')} ({len(params)} parameters):")
        for param in params.values():
            print(f"  {param.name} - {param.description}")
    
    print(f"\nTotal writable parameters: {len(WRITABLE_PARAMETERS)}")
