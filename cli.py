#!/usr/bin/env python3
"""
Command-line interface for Tracer3210AN Solar Charger
Uses shared tracer_solar_charger library
"""

import argparse
import sys
import json
from typing import Optional, List
from tracer_solar_charger import ModbusRTUClient, DeviceData, PARAMETERS

def discover_device(device_path: str, slave_id: int = 1, baudrate: int = 115200) -> bool:
    """Test device connection and communication"""
    print(f"Testing connection to {device_path}...")
    
    with ModbusRTUClient(device_path, baudrate, slave_id) as client:
        if not client.connect():
            print("❌ Failed to open serial connection")
            return False
            
        info = client.read_device_info()
        if info.get('communication') == 'OK':
            print("✅ Device communication successful")
            print(f"   PV Voltage: {info.get('pv_voltage', 'N/A')} V")
            return True
        else:
            print("❌ Device communication failed")
            return False

def read_parameters(device_path: str, param_names: List[str], slave_id: int = 1, 
                   baudrate: int = 115200, output_format: str = 'human') -> Optional[DeviceData]:
    """Read specific parameters from device"""
    
    device_data = DeviceData()
    
    with ModbusRTUClient(device_path, baudrate, slave_id) as client:
        if not client.connect():
            print("Failed to connect to device")
            return None
            
        for param_name in param_names:
            if param_name not in PARAMETERS:
                print(f"Warning: Unknown parameter '{param_name}'")
                continue
                
            param = PARAMETERS[param_name]
            address = param['address']
            
            # Read the register
            if param.get('combine_registers'):
                # Combined register (32-bit value from two 16-bit registers)
                result = client.read_combined_registers(address, param['high_address'])
                if result is not None:
                    scaled_value = result * param.get('scale', 1)
                    device_data.set_parameter(
                        param_name,
                        scaled_value,
                        param.get('unit', ''),
                        param.get('category', '')
                    )
            else:
                # Single register
                if param.get('function_code') == 4:
                    result = client.read_input_registers(address, 1)
                else:
                    result = client.read_holding_registers(address, 1)
                    
                if result:
                    raw_value = result[0]
                    scaled_value = raw_value * param.get('scale', 1)
                    
                    device_data.set_parameter(
                        param_name,
                        scaled_value,
                        param.get('unit', ''),
                        param.get('category', '')
                    )
                else:
                    print(f"Failed to read {param_name}")
                
    return device_data

def read_all_parameters(device_path: str, category: Optional[str] = None, 
                       slave_id: int = 1, baudrate: int = 115200) -> Optional[DeviceData]:
    """Read all parameters or parameters from specific category"""
    
    params_to_read = []
    for name, param in PARAMETERS.items():
        if category is None or param.get('category') == category:
            params_to_read.append(name)
            
    return read_parameters(device_path, params_to_read, slave_id, baudrate)

def list_parameters(category: Optional[str] = None, detailed: bool = False):
    """List available parameters"""
    
    if category:
        print(f"\n=== {category.upper()} PARAMETERS ===")
        params = {k: v for k, v in PARAMETERS.items() if v.get('category') == category}
    else:
        print("\n=== ALL AVAILABLE PARAMETERS ===")
        params = PARAMETERS
        
    for name, param in params.items():
        if detailed:
            print(f"{name}:")
            print(f"  Description: {param.get('description', 'N/A')}")
            print(f"  Address: 0x{param['address']:04X}")
            print(f"  Unit: {param.get('unit', 'N/A')}")
            print(f"  Category: {param.get('category', 'N/A')}")
            print()
        else:
            unit = param.get('unit', '')
            desc = param.get('description', name.replace('_', ' ').title())
            print(f"  {name:<25} - {desc} {f'({unit})' if unit else ''}")

def main():
    parser = argparse.ArgumentParser(description='Tracer3210AN Solar Charger Interface')
    parser.add_argument('--device', '-d', required=False, help='Serial device path')
    parser.add_argument('--slave-id', type=int, default=1, help='Modbus slave ID')
    parser.add_argument('--baudrate', type=int, default=115200, help='Serial baudrate')
    parser.add_argument('--format', '-f', choices=['human', 'json', 'csv'], 
                       default='human', help='Output format')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Discover command
    subparsers.add_parser('discover', help='Test device connection')
    
    # List parameters command
    list_parser = subparsers.add_parser('list-parameters', help='List available parameters')
    list_parser.add_argument('--detailed', action='store_true', help='Show detailed information')
    list_parser.add_argument('--category', help='Parameter category filter')
    
    # Read specific parameters
    read_parser = subparsers.add_parser('read', help='Read specific parameters')
    read_parser.add_argument('parameters', nargs='+', help='Parameter names to read')
    
    # Read all parameters
    read_all_parser = subparsers.add_parser('read-all', help='Read all parameters')
    read_all_parser.add_argument('--category', help='Parameter category filter')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    # Commands that don't need device connection
    if args.command == 'list-parameters':
        list_parameters(args.category, args.detailed)
        return
        
    # Commands that need device connection
    if not args.device:
        print("Error: --device is required for this command")
        return
        
    if args.command == 'discover':
        success = discover_device(args.device, args.slave_id, args.baudrate)
        sys.exit(0 if success else 1)
        
    elif args.command == 'read':
        device_data = read_parameters(args.device, args.parameters, 
                                    args.slave_id, args.baudrate)
        
    elif args.command == 'read-all':
        device_data = read_all_parameters(args.device, args.category, 
                                        args.slave_id, args.baudrate)
    else:
        print(f"Unknown command: {args.command}")
        return
        
    # Format and output results
    if device_data:
        if args.format == 'human':
            output = device_data.format_human_readable(args.category)
        elif args.format == 'json':
            output = device_data.format_json(args.category)
        elif args.format == 'csv':
            header = device_data.format_csv_header(args.category)
            row = device_data.format_csv_row(args.category)
            output = f"{header}\n{row}"
            
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Output written to {args.output}")
        else:
            print(output)

if __name__ == '__main__':
    main()
