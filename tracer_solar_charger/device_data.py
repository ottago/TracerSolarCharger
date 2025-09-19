#!/usr/bin/env python3
"""
Device data models and formatting for Tracer3210AN Solar Charger
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime

class DeviceData:
    """Container for device data with formatting capabilities"""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.timestamp = datetime.now()
        
    def set_parameter(self, name: str, value: Any, unit: str = "", category: str = ""):
        """Set a parameter value with metadata"""
        self.data[name] = {
            'value': value,
            'unit': unit,
            'category': category,
            'timestamp': self.timestamp.isoformat()
        }
        
    def get_parameter(self, name: str) -> Optional[Any]:
        """Get parameter value"""
        return self.data.get(name, {}).get('value')
        
    def get_category_data(self, category: str) -> Dict[str, Any]:
        """Get all parameters for a specific category"""
        return {k: v for k, v in self.data.items() if v.get('category') == category}
        
    def format_human_readable(self, category: Optional[str] = None) -> str:
        """Format data in human-readable format"""
        output = []
        data_to_format = self.get_category_data(category) if category else self.data
        
        if category:
            output.append(f"\n=== {category.upper()} PARAMETERS ===")
        else:
            output.append(f"\n=== TRACER3210AN STATUS ({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}) ===")
            
        for name, info in data_to_format.items():
            value = info['value']
            unit = info.get('unit', '')
            
            # Format numeric values to 2 decimal places
            if isinstance(value, float):
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
                
            line = f"{name.replace('_', ' ').title()}: {formatted_value}"
            if unit:
                line += f" {unit}"
            output.append(line)
            
        return '\n'.join(output)
        
    def format_json(self, category: Optional[str] = None) -> str:
        """Format data as JSON"""
        data_to_format = self.get_category_data(category) if category else self.data
        return json.dumps(data_to_format, indent=2, default=str)
        
    def format_csv_header(self, category: Optional[str] = None) -> str:
        """Generate CSV header"""
        data_to_format = self.get_category_data(category) if category else self.data
        headers = ['timestamp'] + list(data_to_format.keys())
        return ','.join(headers)
        
    def format_csv_row(self, category: Optional[str] = None) -> str:
        """Format data as CSV row"""
        data_to_format = self.get_category_data(category) if category else self.data
        values = [self.timestamp.isoformat()]
        
        for info in data_to_format.values():
            value = info['value']
            if isinstance(value, float):
                values.append(f"{value:.2f}")
            else:
                values.append(str(value))
                
        return ','.join(values)
        
    def get_all_categories(self) -> List[str]:
        """Get list of all categories in the data"""
        categories = set()
        for info in self.data.values():
            if info.get('category'):
                categories.add(info['category'])
        return sorted(list(categories))
