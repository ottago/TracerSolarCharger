#!/usr/bin/env python3
"""
Device Data Models for Tracer3210AN Solar Charger
Handles parameter definitions, formatting, and data organization
"""

import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add the project root to the path to import parameter_definitions
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from parameter_definitions import (
    REALTIME_PARAMETERS, CONFIG_PARAMETERS, 
    format_value, get_all_parameters,
    BATTERY_STATUS_BITS, CHARGING_STATUS_BITS, DISCHARGING_STATUS_BITS
)

@dataclass
class ParameterReading:
    """Single parameter reading with metadata"""
    address: int
    name: str
    description: str
    raw_value: int
    formatted_value: Any
    unit: str
    category: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'address': f'0x{self.address:04X}',
            'name': self.name,
            'description': self.description,
            'raw_value': self.raw_value,
            'formatted_value': self.formatted_value,
            'unit': self.unit,
            'category': self.category,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class DeviceSnapshot:
    """Complete device data snapshot"""
    timestamp: datetime
    device_info: Dict[str, Any]
    parameters: List[ParameterReading]
    
    def get_by_category(self, category: str) -> List[ParameterReading]:
        """Get parameters by category"""
        return [p for p in self.parameters if p.category == category]
    
    def get_by_name(self, name: str) -> Optional[ParameterReading]:
        """Get parameter by name"""
        for p in self.parameters:
            if p.name == name:
                return p
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'device_info': self.device_info,
            'parameters': [p.to_dict() for p in self.parameters],
            'summary': self.get_summary()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get key parameter summary"""
        summary = {}
        
        # Key real-time values
        key_params = [
            'pv_voltage', 'pv_current', 'battery_voltage', 'battery_current',
            'load_voltage', 'load_current', 'battery_soc', 'battery_temp'
        ]
        
        for param_name in key_params:
            param = self.get_by_name(param_name)
            if param:
                summary[param_name] = {
                    'value': param.formatted_value,
                    'unit': param.unit
                }
        
        # Status information
        battery_status = self.get_by_name('battery_status')
        if battery_status:
            summary['battery_status'] = battery_status.formatted_value
        
        charging_status = self.get_by_name('charging_equipment_status')
        if charging_status:
            summary['charging_status'] = charging_status.formatted_value
        
        return summary

class DeviceDataManager:
    """Manages device data collection and formatting"""
    
    def __init__(self):
        self.device_info = {
            'model': 'Tracer3210AN',
            'protocol': 'Modbus RTU',
            'slave_id': 1,
            'baudrate': 115200
        }
        self.all_parameters = get_all_parameters()
    
    def create_parameter_reading(self, address: int, raw_value: int, is_holding: bool = False) -> Optional[ParameterReading]:
        """Create a formatted parameter reading"""
        formatted_data = format_value(address, raw_value, is_holding)
        
        if 'name' not in formatted_data:
            # Unknown parameter
            return ParameterReading(
                address=address,
                name=f'unknown_0x{address:04x}',
                description=formatted_data['description'],
                raw_value=raw_value,
                formatted_value=raw_value,
                unit='',
                category='unknown',
                timestamp=datetime.now()
            )
        
        return ParameterReading(
            address=address,
            name=formatted_data['name'],
            description=formatted_data['description'],
            raw_value=raw_value,
            formatted_value=formatted_data['formatted'],
            unit=formatted_data['unit'],
            category=formatted_data['category'],
            timestamp=datetime.now()
        )
    
    def create_device_snapshot(self, register_data: Dict[int, int], holding_data: Dict[int, int] = None) -> DeviceSnapshot:
        """Create a complete device snapshot from register data"""
        parameters = []
        
        # Process input registers (real-time data)
        for address, value in register_data.items():
            param = self.create_parameter_reading(address, value, is_holding=False)
            if param:
                parameters.append(param)
        
        # Process holding registers (configuration data)
        if holding_data:
            for address, value in holding_data.items():
                param = self.create_parameter_reading(address, value, is_holding=True)
                if param:
                    parameters.append(param)
        
        return DeviceSnapshot(
            timestamp=datetime.now(),
            device_info=self.device_info,
            parameters=parameters
        )
    
    def get_efficient_read_blocks(self) -> Dict[str, Dict[str, Any]]:
        """Get optimized register blocks for efficient reading"""
        return {
            'realtime_core': {
                'function_code': 4,
                'start_address': 0x3100,
                'count': 16,
                'description': 'Core real-time data (PV, Battery, Load)'
            },
            'realtime_extended': {
                'function_code': 4,
                'start_address': 0x3110,
                'count': 16,
                'description': 'Extended real-time data (Temperatures, SOC)'
            },
            'status': {
                'function_code': 4,
                'start_address': 0x3200,
                'count': 3,
                'description': 'System status registers'
            },
            'statistics_daily': {
                'function_code': 4,
                'start_address': 0x3300,
                'count': 16,
                'description': 'Daily statistics (first block)'
            },
            'statistics_extended': {
                'function_code': 4,
                'start_address': 0x3310,
                'count': 15,
                'description': 'Extended statistics'
            },
            'config_voltages': {
                'function_code': 3,
                'start_address': 0x9000,
                'count': 8,
                'description': 'Core voltage configuration'
            },
            'config_extended': {
                'function_code': 3,
                'start_address': 0x9008,
                'count': 8,
                'description': 'Extended configuration'
            }
        }
    
    def get_parameter_list(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available parameters, optionally filtered by category"""
        param_list = []
        
        for cat, params in self.all_parameters.items():
            if category and cat != category:
                continue
                
            for param in params:
                param_list.append({
                    'address': param['hex_address'],
                    'name': param['name'],
                    'description': param['description'],
                    'unit': param['unit'],
                    'category': param['category'],
                    'function_code': param['function_code']
                })
        
        return param_list
    
    def get_categories(self) -> List[str]:
        """Get list of available parameter categories"""
        return list(self.all_parameters.keys())
    
    def format_for_output(self, snapshot: DeviceSnapshot, output_format: str = 'human') -> str:
        """Format device snapshot for different output types"""
        if output_format == 'json':
            import json
            return json.dumps(snapshot.to_dict(), indent=2)
        
        elif output_format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow(['Address', 'Name', 'Description', 'Value', 'Unit', 'Category', 'Raw Value'])
            
            # Data rows
            for param in snapshot.parameters:
                writer.writerow([
                    f'0x{param.address:04X}',
                    param.name,
                    param.description,
                    param.formatted_value,
                    param.unit,
                    param.category,
                    param.raw_value
                ])
            
            return output.getvalue()
        
        elif output_format == 'human':
            return self._format_human_readable(snapshot)
        
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _format_human_readable(self, snapshot: DeviceSnapshot) -> str:
        """Format snapshot in human-readable format"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"Solar Charger Status - {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        
        # Group by category
        categories = {}
        for param in snapshot.parameters:
            if param.category not in categories:
                categories[param.category] = []
            categories[param.category].append(param)
        
        # Display each category
        category_order = ['pv', 'battery', 'load', 'system', 'statistics', 'config']
        
        for category in category_order:
            if category in categories:
                lines.append(f"\n{category.upper()} PARAMETERS:")
                lines.append("-" * 40)
                
                for param in sorted(categories[category], key=lambda x: x.address):
                    # Format the value with consistent decimal places for floats
                    if isinstance(param.formatted_value, float):
                        value_str = f"{param.formatted_value:.2f}"
                    else:
                        value_str = f"{param.formatted_value}"
                    
                    if param.unit:
                        value_str += f" {param.unit}"
                    
                    lines.append(f"  {param.description:<30} {value_str:>15}")
        
        # Add any remaining categories
        for category, params in categories.items():
            if category not in category_order:
                lines.append(f"\n{category.upper()} PARAMETERS:")
                lines.append("-" * 40)
                
                for param in sorted(params, key=lambda x: x.address):
                    # Format the value with consistent decimal places for floats
                    if isinstance(param.formatted_value, float):
                        value_str = f"{param.formatted_value:.2f}"
                    else:
                        value_str = f"{param.formatted_value}"
                    
                    if param.unit:
                        value_str += f" {param.unit}"
                    
                    lines.append(f"  {param.description:<30} {value_str:>15}")
        
        return "\n".join(lines)
