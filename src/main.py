#!/usr/bin/env python3
"""
Solar Charger Interface - Main CLI Application
Command-line interface for Tracer3210AN Solar Charge Controller
"""

import argparse
import sys
import time
import json
from typing import Optional, Dict, List
from datetime import datetime

from communication.modbus_client import ModbusRTUClient
from models.device_data import DeviceDataManager, DeviceSnapshot

# Add writable parameters support
sys.path.append('..')
from writable_parameters import (
    get_writable_parameter, get_writable_parameters_by_category, 
    get_writable_categories, validate_voltage_sequence, BATTERY_TYPE_SETTINGS
)

class SolarChargerCLI:
    """Main CLI application class"""
    
    def __init__(self):
        self.data_manager = DeviceDataManager()
        self.client = None
    
    def create_argument_parser(self) -> argparse.ArgumentParser:
        """Create command line argument parser"""
        parser = argparse.ArgumentParser(
            description='Solar Charger Interface for Tracer3210AN',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --device /dev/ttyUSB0 discover
  %(prog)s --device /dev/ttyUSB0 read-all
  %(prog)s --device /dev/ttyUSB0 read-all --format json
  %(prog)s --device /dev/ttyUSB0 read pv_voltage battery_voltage
  %(prog)s --device /dev/ttyUSB0 monitor --interval 5
  %(prog)s --device /dev/ttyUSB0 list-parameters --category pv
  %(prog)s list-writable --detailed
  %(prog)s --device /dev/ttyUSB0 write battery_capacity 200
  %(prog)s --device /dev/ttyUSB0 write-config --battery-type LiFePO4
  %(prog)s --device /dev/ttyUSB0 backup-config
            """
        )
        
        # Connection parameters
        parser.add_argument('--device', '-d',
                          help='Serial device path (e.g., /dev/ttyUSB0, COM3)')
        parser.add_argument('--speed', '-s', type=int, default=115200,
                          help='Serial speed (default: 115200)')
        parser.add_argument('--slave-id', type=int, default=1,
                          help='Modbus slave ID (default: 1)')
        parser.add_argument('--timeout', type=float, default=2.0,
                          help='Communication timeout in seconds (default: 2.0)')
        
        # Output formatting
        parser.add_argument('--format', '-f', choices=['human', 'json', 'csv'],
                          default='human', help='Output format (default: human)')
        parser.add_argument('--output', '-o', type=str,
                          help='Output file (default: stdout)')
        
        # Commands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Discover command
        discover_parser = subparsers.add_parser('discover', help='Discover and test device connection')
        
        # Read all command
        read_all_parser = subparsers.add_parser('read-all', help='Read all available parameters')
        read_all_parser.add_argument('--category', '-c', 
                                   help='Filter by category (pv, battery, load, system, statistics, config)')
        read_all_parser.add_argument('--efficient', action='store_true',
                                   help='Use efficient multi-register reads')
        
        # Read specific parameters
        read_parser = subparsers.add_parser('read', help='Read specific parameters')
        read_parser.add_argument('parameters', nargs='+',
                               help='Parameter names or addresses to read')
        
        # Monitor command
        monitor_parser = subparsers.add_parser('monitor', help='Continuous monitoring mode')
        monitor_parser.add_argument('--interval', '-i', type=float, default=5.0,
                                  help='Update interval in seconds (default: 5.0)')
        monitor_parser.add_argument('--count', '-n', type=int,
                                  help='Number of readings (default: infinite)')
        monitor_parser.add_argument('--category', '-c',
                                  help='Monitor specific category only')
        
        # List parameters command
        list_parser = subparsers.add_parser('list-parameters', help='List available parameters')
        list_parser.add_argument('--category', '-c',
                               help='Filter by category')
        list_parser.add_argument('--detailed', action='store_true',
                               help='Show detailed parameter information')
        
        # Export command
        export_parser = subparsers.add_parser('export', help='Export current data')
        export_parser.add_argument('--include-config', action='store_true',
                                 help='Include configuration parameters')
        
        # Write single parameter command
        write_parser = subparsers.add_parser('write', help='Write configuration parameter')
        write_parser.add_argument('parameter', help='Parameter name to write')
        write_parser.add_argument('value', help='Value to write')
        write_parser.add_argument('--force', action='store_true',
                                help='Skip confirmation prompts')
        write_parser.add_argument('--dry-run', action='store_true',
                                help='Validate without writing')
        
        # Write multiple parameters command
        write_config_parser = subparsers.add_parser('write-config', help='Write multiple configuration parameters')
        write_config_parser.add_argument('--battery-type', help='Set battery type and apply recommended settings')
        write_config_parser.add_argument('--battery-capacity', type=float, help='Battery capacity in Ah')
        write_config_parser.add_argument('--config-file', help='JSON file with configuration parameters')
        write_config_parser.add_argument('--force', action='store_true',
                                       help='Skip confirmation prompts')
        write_config_parser.add_argument('--dry-run', action='store_true',
                                       help='Validate without writing')
        
        # List writable parameters command
        list_writable_parser = subparsers.add_parser('list-writable', help='List writable parameters')
        list_writable_parser.add_argument('--category', '-c', help='Filter by category')
        list_writable_parser.add_argument('--detailed', action='store_true',
                                        help='Show detailed parameter information including ranges')
        
        # Backup/restore commands
        backup_parser = subparsers.add_parser('backup-config', help='Backup current configuration')
        backup_parser.add_argument('--output', '-o', help='Backup file name')
        
        restore_parser = subparsers.add_parser('restore-config', help='Restore configuration from backup')
        restore_parser.add_argument('backup_file', help='Backup file to restore')
        restore_parser.add_argument('--force', action='store_true',
                                  help='Skip confirmation prompts')
        
        return parser
    
    def connect_device(self, device: str, speed: int, slave_id: int, timeout: float) -> bool:
        """Connect to the solar charger device"""
        try:
            self.client = ModbusRTUClient(device, speed, slave_id, timeout)
            if self.client.connect():
                if self.client.test_connection():
                    print(f"✓ Connected to solar charger on {device}")
                    return True
                else:
                    print(f"✗ Device connected but not responding properly")
                    return False
            else:
                print(f"✗ Failed to connect to {device}")
                return False
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def cmd_discover(self, args) -> int:
        """Discover and test device connection"""
        print("Solar Charger Discovery")
        print("=" * 40)
        
        if not self.connect_device(args.device, args.speed, args.slave_id, args.timeout):
            return 1
        
        try:
            with self.client:
                # Test basic communication
                print(f"Device: {args.device}")
                print(f"Speed: {args.speed} baud")
                print(f"Slave ID: {args.slave_id}")
                print(f"Protocol: Modbus RTU")
                
                # Read a few key parameters to verify communication
                test_reads = [
                    (0x3104, "Battery Voltage"),
                    (0x3100, "PV Voltage"),
                    (0x3108, "Load Voltage"),
                    (0x9000, "Battery Type (Config)")
                ]
                
                print("\nTesting key parameters:")
                for addr, desc in test_reads:
                    is_holding = addr >= 0x9000
                    value = self.client.read_single_register(addr, is_holding)
                    if value is not None:
                        print(f"  ✓ {desc}: {value} (0x{addr:04X})")
                    else:
                        print(f"  ✗ {desc}: No response (0x{addr:04X})")
                
                print(f"\n✓ Device discovery completed successfully")
                return 0
                
        except Exception as e:
            print(f"✗ Discovery failed: {e}")
            return 1
    
    def cmd_read_all(self, args) -> int:
        """Read all available parameters"""
        if not self.connect_device(args.device, args.speed, args.slave_id, args.timeout):
            return 1
        
        try:
            with self.client:
                if args.efficient:
                    snapshot = self._read_all_efficient(args.category)
                else:
                    snapshot = self._read_all_individual(args.category)
                
                if snapshot:
                    output = self.data_manager.format_for_output(snapshot, args.format)
                    self._write_output(output, args.output)
                    return 0
                else:
                    print("✗ Failed to read device data")
                    return 1
                    
        except Exception as e:
            print(f"✗ Read failed: {e}")
            return 1
    
    def _read_all_efficient(self, category_filter: Optional[str] = None) -> Optional[DeviceSnapshot]:
        """Read all parameters using efficient multi-register reads"""
        print("Reading device data (efficient mode)...")
        
        register_data = {}
        holding_data = {}
        
        read_blocks = self.data_manager.get_efficient_read_blocks()
        
        for block_name, block_info in read_blocks.items():
            if category_filter:
                # Skip blocks that don't match category filter
                if category_filter == 'config' and block_info['function_code'] != 3:
                    continue
                elif category_filter != 'config' and block_info['function_code'] == 3:
                    continue
            
            print(f"  Reading {block_info['description']}...")
            
            if block_info['function_code'] == 4:
                # Input registers
                block_data = self.client.read_register_block(
                    block_info['start_address'], 
                    block_info['count'], 
                    is_holding=False
                )
                if block_data:
                    register_data.update(block_data)
            else:
                # Holding registers
                block_data = self.client.read_register_block(
                    block_info['start_address'], 
                    block_info['count'], 
                    is_holding=True
                )
                if block_data:
                    holding_data.update(block_data)
        
        if register_data or holding_data:
            return self.data_manager.create_device_snapshot(register_data, holding_data)
        
        return None
    
    def _read_all_individual(self, category_filter: Optional[str] = None) -> Optional[DeviceSnapshot]:
        """Read all parameters individually (slower but more comprehensive)"""
        print("Reading device data (comprehensive mode)...")
        
        register_data = {}
        holding_data = {}
        
        # Get all parameters
        all_params = self.data_manager.get_parameter_list(category_filter)
        
        for param in all_params:
            addr = int(param['address'], 16)
            is_holding = param['function_code'] == 3
            
            value = self.client.read_single_register(addr, is_holding)
            if value is not None:
                if is_holding:
                    holding_data[addr] = value
                else:
                    register_data[addr] = value
        
        if register_data or holding_data:
            return self.data_manager.create_device_snapshot(register_data, holding_data)
        
        return None
    
    def cmd_read(self, args) -> int:
        """Read specific parameters"""
        if not self.connect_device(args.device, args.speed, args.slave_id, args.timeout):
            return 1
        
        try:
            with self.client:
                register_data = {}
                holding_data = {}
                
                # Get all available parameters for lookup
                all_params = self.data_manager.get_parameter_list()
                param_lookup = {p['name']: p for p in all_params}
                addr_lookup = {p['address']: p for p in all_params}
                
                for param_spec in args.parameters:
                    # Try to parse as address first
                    if param_spec.startswith('0x') or param_spec.startswith('0X'):
                        try:
                            addr = int(param_spec, 16)
                            if param_spec.upper() in addr_lookup:
                                param_info = addr_lookup[param_spec.upper()]
                                is_holding = param_info['function_code'] == 3
                            else:
                                # Unknown address, try both function codes
                                is_holding = addr >= 0x9000  # Heuristic
                        except ValueError:
                            print(f"✗ Invalid address format: {param_spec}")
                            continue
                    else:
                        # Look up by parameter name
                        if param_spec in param_lookup:
                            param_info = param_lookup[param_spec]
                            addr = int(param_info['address'], 16)
                            is_holding = param_info['function_code'] == 3
                        else:
                            print(f"✗ Unknown parameter: {param_spec}")
                            continue
                    
                    # Read the parameter
                    value = self.client.read_single_register(addr, is_holding)
                    if value is not None:
                        if is_holding:
                            holding_data[addr] = value
                        else:
                            register_data[addr] = value
                        print(f"✓ Read {param_spec}: {value}")
                    else:
                        print(f"✗ Failed to read {param_spec}")
                
                if register_data or holding_data:
                    snapshot = self.data_manager.create_device_snapshot(register_data, holding_data)
                    output = self.data_manager.format_for_output(snapshot, args.format)
                    self._write_output(output, args.output)
                    return 0
                else:
                    print("✗ No parameters successfully read")
                    return 1
                    
        except Exception as e:
            print(f"✗ Read failed: {e}")
            return 1
    
    def cmd_monitor(self, args) -> int:
        """Continuous monitoring mode"""
        if not self.connect_device(args.device, args.speed, args.slave_id, args.timeout):
            return 1
        
        try:
            with self.client:
                print(f"Starting monitoring mode (interval: {args.interval}s)")
                print("Press Ctrl+C to stop")
                print("=" * 60)
                
                count = 0
                while True:
                    try:
                        snapshot = self._read_all_efficient(args.category)
                        if snapshot:
                            if args.format == 'human':
                                # Clear screen and show current data
                                print("\033[2J\033[H")  # Clear screen
                                print(self.data_manager.format_for_output(snapshot, 'human'))
                            else:
                                output = self.data_manager.format_for_output(snapshot, args.format)
                                print(output)
                                print("-" * 40)
                        
                        count += 1
                        if args.count and count >= args.count:
                            break
                        
                        time.sleep(args.interval)
                        
                    except KeyboardInterrupt:
                        print("\nMonitoring stopped by user")
                        break
                
                return 0
                
        except Exception as e:
            print(f"✗ Monitoring failed: {e}")
            return 1
    
    def cmd_list_parameters(self, args) -> int:
        """List available parameters"""
        params = self.data_manager.get_parameter_list(args.category)
        
        if args.detailed:
            print("Available Parameters (Detailed)")
            print("=" * 80)
            
            current_category = None
            for param in sorted(params, key=lambda x: x['category']):
                if param['category'] != current_category:
                    current_category = param['category']
                    print(f"\n{current_category.upper()} PARAMETERS:")
                    print("-" * 40)
                
                fc_str = f"FC{param['function_code']:02d}"
                print(f"  {param['address']} ({fc_str}) {param['name']:<25} {param['description']}")
                if param['unit']:
                    print(f"    Unit: {param['unit']}")
        else:
            print("Available Parameters")
            print("=" * 50)
            
            categories = {}
            for param in params:
                if param['category'] not in categories:
                    categories[param['category']] = []
                categories[param['category']].append(param['name'])
            
            for category, param_names in categories.items():
                print(f"\n{category.upper()} ({len(param_names)} parameters):")
                for name in sorted(param_names):
                    print(f"  {name}")
        
        print(f"\nTotal: {len(params)} parameters")
        return 0
    
    def cmd_export(self, args) -> int:
        """Export current device data"""
        if not self.connect_device(args.device, args.speed, args.slave_id, args.timeout):
            return 1
        
        try:
            with self.client:
                # Read all data
                snapshot = self._read_all_efficient()
                
                if args.include_config:
                    # Also read configuration data
                    config_snapshot = self._read_all_efficient('config')
                    if config_snapshot:
                        snapshot.parameters.extend(config_snapshot.parameters)
                
                if snapshot:
                    # Create export data
                    export_data = {
                        'export_timestamp': datetime.now().isoformat(),
                        'device_info': snapshot.device_info,
                        'data': snapshot.to_dict()
                    }
                    
                    output = json.dumps(export_data, indent=2)
                    
                    # Default filename if not specified
                    if not args.output:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        args.output = f'solar_charger_export_{timestamp}.json'
                    
                    self._write_output(output, args.output)
                    print(f"✓ Data exported to {args.output}")
                    return 0
                else:
                    print("✗ Failed to read device data for export")
                    return 1
                    
        except Exception as e:
            print(f"✗ Export failed: {e}")
            return 1
    
    def cmd_write(self, args) -> int:
        """Write a single configuration parameter"""
        if not self.connect_device(args.device, args.speed, args.slave_id, args.timeout):
            return 1
        
        try:
            with self.client:
                # Get parameter definition
                param = get_writable_parameter(args.parameter)
                if not param:
                    print(f"✗ Parameter '{args.parameter}' is not writable or doesn't exist")
                    print("Use 'list-writable' to see available writable parameters")
                    return 1
                
                # Validate the value
                is_valid, error_msg, raw_value = param.validate_value(args.value)
                if not is_valid:
                    print(f"✗ Invalid value: {error_msg}")
                    return 1
                
                # Show what will be written
                print(f"Parameter: {param.description}")
                print(f"Current address: 0x{param.address:04X}")
                print(f"Value to write: {args.value} {param.unit}")
                print(f"Raw Modbus value: {raw_value}")
                
                if param.warning_message:
                    print(f"⚠️  WARNING: {param.warning_message}")
                
                if args.dry_run:
                    print("✓ Dry run - validation passed, no data written")
                    return 0
                
                # Confirmation
                if not args.force:
                    response = input("\nProceed with writing this value? (yes/no): ")
                    if response.lower() not in ['yes', 'y']:
                        print("Write operation cancelled")
                        return 0
                
                # Read current value first
                current_raw = self.client.read_single_register(param.address, is_holding=True)
                if current_raw is not None:
                    current_value = current_raw * param.scale
                    print(f"Current value: {current_value} {param.unit} (raw: {current_raw})")
                
                # Write the new value
                print(f"Writing new value...")
                success = self.client.write_single_register(param.address, raw_value)
                
                if success:
                    print("✓ Write successful")
                    
                    # Verify the write
                    time.sleep(0.5)
                    verify_raw = self.client.read_single_register(param.address, is_holding=True)
                    if verify_raw == raw_value:
                        verify_value = verify_raw * param.scale
                        print(f"✓ Verification successful: {verify_value} {param.unit}")
                    else:
                        print(f"⚠️  Verification failed: expected {raw_value}, got {verify_raw}")
                    
                    return 0
                else:
                    print("✗ Write failed")
                    return 1
                    
        except Exception as e:
            print(f"✗ Write operation failed: {e}")
            return 1
    
    def cmd_list_writable(self, args) -> int:
        """List writable parameters"""
        params = get_writable_parameters_by_category(args.category)
        
        if args.detailed:
            print("Writable Parameters (Detailed)")
            print("=" * 80)
            
            categories = {}
            for param in params.values():
                if param.category not in categories:
                    categories[param.category] = []
                categories[param.category].append(param)
            
            for category, param_list in categories.items():
                print(f"\n{category.upper().replace('_', ' ')} PARAMETERS:")
                print("-" * 50)
                
                for param in sorted(param_list, key=lambda x: x.address):
                    print(f"  {param.name}")
                    print(f"    Address: 0x{param.address:04X}")
                    print(f"    Description: {param.description}")
                    print(f"    Unit: {param.unit}")
                    
                    if param.min_value is not None or param.max_value is not None:
                        range_str = f"Range: "
                        if param.min_value is not None:
                            range_str += f"{param.min_value}"
                        else:
                            range_str += "no min"
                        range_str += " to "
                        if param.max_value is not None:
                            range_str += f"{param.max_value}"
                        else:
                            range_str += "no max"
                        range_str += f" {param.unit}"
                        print(f"    {range_str}")
                    
                    if param.valid_values:
                        print(f"    Valid values: {param.valid_values}")
                    
                    if param.warning_message:
                        print(f"    ⚠️  WARNING: {param.warning_message}")
                    
                    print()
        else:
            print("Writable Parameters")
            print("=" * 50)
            
            categories = {}
            for param in params.values():
                if param.category not in categories:
                    categories[param.category] = []
                categories[param.category].append(param.name)
            
            for category, param_names in categories.items():
                print(f"\n{category.upper().replace('_', ' ')} ({len(param_names)} parameters):")
                for name in sorted(param_names):
                    print(f"  {name}")
        
        print(f"\nTotal writable parameters: {len(params)}")
        return 0
    
    def cmd_write_config(self, args) -> int:
        """Write multiple configuration parameters"""
        if not self.connect_device(args.device, args.speed, args.slave_id, args.timeout):
            return 1
        
        try:
            with self.client:
                config_to_write = {}
                
                # Handle battery type with recommended settings
                if args.battery_type:
                    if args.battery_type not in BATTERY_TYPE_SETTINGS:
                        print(f"✗ Unknown battery type: {args.battery_type}")
                        print(f"Available types: {list(BATTERY_TYPE_SETTINGS.keys())}")
                        return 1
                    
                    print(f"Setting battery type to {args.battery_type} with recommended settings:")
                    
                    # Add battery type
                    config_to_write['battery_type'] = args.battery_type
                    
                    # Add recommended voltage settings
                    recommended = BATTERY_TYPE_SETTINGS[args.battery_type]
                    for setting_name, value in recommended.items():
                        config_to_write[setting_name] = value
                        print(f"  {setting_name}: {value}")
                
                # Handle battery capacity
                if args.battery_capacity:
                    config_to_write['battery_capacity'] = args.battery_capacity
                
                # Handle config file
                if args.config_file:
                    try:
                        with open(args.config_file, 'r') as f:
                            file_config = json.load(f)
                        config_to_write.update(file_config)
                        print(f"Loaded configuration from {args.config_file}")
                    except Exception as e:
                        print(f"✗ Failed to load config file: {e}")
                        return 1
                
                if not config_to_write:
                    print("✗ No configuration parameters specified")
                    print("Use --battery-type, --battery-capacity, or --config-file")
                    return 1
                
                # Validate all parameters
                validated_params = []  # Use list instead of dict
                validation_errors = []
                
                for param_name, value in config_to_write.items():
                    param = get_writable_parameter(param_name)
                    if not param:
                        validation_errors.append(f"Parameter '{param_name}' is not writable")
                        continue
                    
                    is_valid, error_msg, raw_value = param.validate_value(value)
                    if not is_valid:
                        validation_errors.append(f"{param_name}: {error_msg}")
                    else:
                        validated_params.append((param, value, raw_value))
                
                if validation_errors:
                    print("✗ Validation errors:")
                    for error in validation_errors:
                        print(f"  {error}")
                    return 1
                
                # Check voltage sequence
                voltage_settings = {param.name: val for param, val, _ in validated_params}
                voltage_warnings = validate_voltage_sequence(voltage_settings)
                
                if voltage_warnings:
                    print("⚠️  Voltage sequence warnings:")
                    for warning in voltage_warnings:
                        print(f"  {warning}")
                
                # Show summary
                print(f"\nConfiguration to write ({len(validated_params)} parameters):")
                for param, value, raw_value in validated_params:
                    print(f"  {param.description}: {value} {param.unit} (0x{param.address:04X})")
                    if param.warning_message:
                        print(f"    ⚠️  {param.warning_message}")
                
                if args.dry_run:
                    print("✓ Dry run - validation passed, no data written")
                    return 0
                
                # Confirmation
                if not args.force:
                    print(f"\n⚠️  You are about to modify {len(validated_params)} configuration parameters.")
                    print("This will change how your solar charger operates!")
                    response = input("Proceed with writing configuration? (yes/no): ")
                    if response.lower() not in ['yes', 'y']:
                        print("Configuration write cancelled")
                        return 0
                
                # Write parameters
                success_count = 0
                failed_params = []
                
                for param, value, raw_value in validated_params:
                    print(f"Writing {param.name}: {value} {param.unit}...")
                    
                    if self.client.write_single_register(param.address, raw_value):
                        success_count += 1
                        print(f"  ✓ Success")
                        
                        # Verify the write
                        time.sleep(0.2)
                        verify_raw = self.client.read_single_register(param.address, is_holding=True)
                        if verify_raw == raw_value:
                            print(f"  ✓ Verified")
                        else:
                            print(f"  ⚠️  Verification failed: expected {raw_value}, got {verify_raw}")
                    else:
                        failed_params.append(param.name)
                        print(f"  ✗ Failed")
                    
                    time.sleep(0.1)  # Brief delay between writes
                
                print(f"\nWrite complete: {success_count}/{len(validated_params)} parameters written successfully")
                
                if failed_params:
                    print(f"Failed parameters: {', '.join(failed_params)}")
                
                if success_count == len(validated_params):
                    print("✓ All parameters written successfully")
                    return 0
                else:
                    print("⚠️  Some parameters failed to write")
                    return 1
                    
        except Exception as e:
            print(f"✗ Configuration write failed: {e}")
            return 1
    
    def cmd_backup_config(self, args) -> int:
        """Backup current configuration"""
        if not self.connect_device(args.device, args.speed, args.slave_id, args.timeout):
            return 1
        
        try:
            with self.client:
                print("Reading current configuration...")
                
                # Read all writable parameters
                config_backup = {
                    'backup_timestamp': datetime.now().isoformat(),
                    'device_info': {
                        'model': 'Tracer3210AN',
                        'device': args.device,
                        'slave_id': args.slave_id,
                        'baudrate': args.speed
                    },
                    'parameters': {},
                    'metadata': {
                        'total_parameters': 0,
                        'successful_reads': 0,
                        'failed_reads': 0
                    }
                }
                
                writable_params = get_writable_parameters_by_category()
                read_count = 0
                failed_count = 0
                
                for param in writable_params.values():
                    print(f"  Reading {param.name}...")
                    raw_value = self.client.read_single_register(param.address, is_holding=True)
                    
                    if raw_value is not None:
                        actual_value = raw_value * param.scale
                        
                        # Handle enum values
                        if param.valid_values and isinstance(param.valid_values, list):
                            if raw_value < len(param.valid_values):
                                display_value = param.valid_values[raw_value]
                            else:
                                display_value = f"Unknown ({raw_value})"
                        else:
                            display_value = actual_value
                        
                        config_backup['parameters'][param.name] = {
                            'address': f'0x{param.address:04X}',
                            'raw_value': raw_value,
                            'actual_value': actual_value,
                            'display_value': display_value,
                            'unit': param.unit,
                            'description': param.description,
                            'category': param.category
                        }
                        read_count += 1
                        print(f"    ✓ {display_value} {param.unit}")
                    else:
                        failed_count += 1
                        print(f"    ✗ Failed to read")
                
                config_backup['metadata']['total_parameters'] = len(writable_params)
                config_backup['metadata']['successful_reads'] = read_count
                config_backup['metadata']['failed_reads'] = failed_count
                
                # Generate filename if not provided
                if not args.output:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    args.output = f'solar_charger_config_backup_{timestamp}.json'
                
                # Save backup
                with open(args.output, 'w') as f:
                    json.dump(config_backup, f, indent=2)
                
                print(f"\n✓ Configuration backup saved: {args.output}")
                print(f"✓ Backed up {read_count}/{len(writable_params)} parameters")
                
                if failed_count > 0:
                    print(f"⚠️  {failed_count} parameters failed to read")
                
                return 0
                
        except Exception as e:
            print(f"✗ Backup failed: {e}")
            return 1
    
    def cmd_restore_config(self, args) -> int:
        """Restore configuration from backup"""
        if not self.connect_device(args.device, args.speed, args.slave_id, args.timeout):
            return 1
        
        try:
            # Load backup file
            print(f"Loading backup file: {args.backup_file}")
            with open(args.backup_file, 'r') as f:
                backup_data = json.load(f)
            
            print(f"✓ Backup loaded successfully")
            print(f"Backup date: {backup_data.get('backup_timestamp', 'Unknown')}")
            
            # Show backup info
            if 'device_info' in backup_data:
                device_info = backup_data['device_info']
                print(f"Original device: {device_info.get('device', 'Unknown')}")
                print(f"Original model: {device_info.get('model', 'Unknown')}")
            
            parameters = backup_data.get('parameters', {})
            if not parameters:
                print("✗ No parameters found in backup file")
                return 1
            
            print(f"Found {len(parameters)} parameters to restore")
            
            # Show what will be restored
            print("\nParameters to restore:")
            categories = {}
            for name, info in parameters.items():
                category = info.get('category', 'unknown')
                if category not in categories:
                    categories[category] = []
                categories[category].append((name, info))
            
            for category, param_list in categories.items():
                print(f"\n  {category.upper().replace('_', ' ')}:")
                for name, info in param_list:
                    display_val = info.get('display_value', info.get('actual_value', 'Unknown'))
                    unit = info.get('unit', '')
                    print(f"    {name}: {display_val} {unit}")
            
            if not args.force:
                print(f"\n⚠️  You are about to restore {len(parameters)} configuration parameters.")
                print("This will overwrite your current settings!")
                print("Consider creating a backup of current settings first.")
                response = input("Proceed with restore? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    print("Restore cancelled")
                    return 0
            
            with self.client:
                success_count = 0
                failed_params = []
                skipped_params = []
                
                print(f"\nRestoring configuration...")
                
                for name, info in parameters.items():
                    param = get_writable_parameter(name)
                    if not param:
                        skipped_params.append(name)
                        print(f"  ⚠️  Skipping {name} (not writable or not found)")
                        continue
                    
                    raw_value = info['raw_value']
                    display_value = info.get('display_value', info.get('actual_value'))
                    
                    print(f"  Restoring {name}: {display_value} {info.get('unit', '')}...")
                    
                    if self.client.write_single_register(param.address, raw_value):
                        success_count += 1
                        print(f"    ✓ Success")
                        
                        # Verify the write
                        time.sleep(0.2)
                        verify_raw = self.client.read_single_register(param.address, is_holding=True)
                        if verify_raw == raw_value:
                            print(f"    ✓ Verified")
                        else:
                            print(f"    ⚠️  Verification failed: expected {raw_value}, got {verify_raw}")
                    else:
                        failed_params.append(name)
                        print(f"    ✗ Failed")
                    
                    time.sleep(0.1)  # Brief delay between writes
                
                # Summary
                total_attempted = len(parameters) - len(skipped_params)
                print(f"\nRestore complete:")
                print(f"  ✓ Successfully restored: {success_count}")
                print(f"  ✗ Failed to restore: {len(failed_params)}")
                print(f"  ⚠️  Skipped (not writable): {len(skipped_params)}")
                print(f"  📊 Success rate: {success_count}/{total_attempted} ({100*success_count/total_attempted if total_attempted > 0 else 0:.1f}%)")
                
                if failed_params:
                    print(f"\nFailed parameters: {', '.join(failed_params)}")
                
                if skipped_params:
                    print(f"Skipped parameters: {', '.join(skipped_params)}")
                
                return 0 if success_count > 0 else 1
                
        except FileNotFoundError:
            print(f"✗ Backup file not found: {args.backup_file}")
            return 1
        except json.JSONDecodeError:
            print(f"✗ Invalid backup file format: {args.backup_file}")
            return 1
        except Exception as e:
            print(f"✗ Restore failed: {e}")
            return 1
    
    def _write_output(self, content: str, filename: Optional[str]):
        """Write output to file or stdout"""
        if filename:
            with open(filename, 'w') as f:
                f.write(content)
            print(f"✓ Output written to {filename}")
        else:
            print(content)
    
    def run(self, args: List[str] = None) -> int:
        """Main entry point"""
        parser = self.create_argument_parser()
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return 1
        
        # Commands that require device connection
        device_commands = ['discover', 'read-all', 'read', 'monitor', 'export', 
                          'write', 'write-config', 'backup-config', 'restore-config']
        
        if parsed_args.command in device_commands and not parsed_args.device:
            print(f"Error: --device is required for '{parsed_args.command}' command")
            return 1
        
        # Dispatch to command handlers
        command_handlers = {
            'discover': self.cmd_discover,
            'read-all': self.cmd_read_all,
            'read': self.cmd_read,
            'monitor': self.cmd_monitor,
            'list-parameters': self.cmd_list_parameters,
            'export': self.cmd_export,
            'write': self.cmd_write,
            'write-config': self.cmd_write_config,
            'list-writable': self.cmd_list_writable,
            'backup-config': self.cmd_backup_config,
            'restore-config': self.cmd_restore_config
        }
        
        handler = command_handlers.get(parsed_args.command)
        if handler:
            return handler(parsed_args)
        else:
            print(f"Unknown command: {parsed_args.command}")
            return 1

def main():
    """Main entry point for the CLI application"""
    cli = SolarChargerCLI()
    return cli.run()

if __name__ == '__main__':
    sys.exit(main())
