#!/usr/bin/env python3
"""
Comprehensive Register Mapping for Tracer3210AN Solar Charger
Scans all possible register addresses to build complete parameter map
"""

import serial
import time
import struct
from binascii import hexlify
import json

def calculate_crc16(data):
    """Calculate Modbus RTU CRC16"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)

def create_modbus_command(slave_id, function_code, start_addr, num_registers):
    """Create a proper Modbus RTU command with CRC"""
    data = struct.pack('>BBHH', slave_id, function_code, start_addr, num_registers)
    crc = calculate_crc16(data)
    return data + crc

def parse_modbus_response(response):
    """Parse Modbus RTU response"""
    if len(response) < 5:
        return None
    
    slave_id = response[0]
    function_code = response[1]
    
    if function_code & 0x80:  # Error response
        error_code = response[2]
        return {
            'slave_id': slave_id,
            'function_code': function_code & 0x7F,
            'error': True,
            'error_code': error_code
        }
    
    if function_code in [0x03, 0x04]:  # Read holding/input registers
        byte_count = response[2]
        data = response[3:3+byte_count]
        
        # Parse 16-bit registers
        registers = []
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                reg_value = struct.unpack('>H', data[i:i+2])[0]
                registers.append(reg_value)
        
        return {
            'slave_id': slave_id,
            'function_code': function_code,
            'error': False,
            'byte_count': byte_count,
            'registers': registers
        }
    
    return {'raw': response}

def scan_register_range(ser, slave_id, function_code, start_addr, end_addr, description=""):
    """Scan a range of registers"""
    print(f"\n--- Scanning {description} (FC{function_code:02X}: 0x{start_addr:04X}-0x{end_addr:04X}) ---")
    
    found_registers = {}
    
    for addr in range(start_addr, end_addr + 1):
        try:
            cmd = create_modbus_command(slave_id, function_code, addr, 1)
            
            ser.reset_input_buffer()
            ser.write(cmd)
            time.sleep(0.05)  # Shorter delay for faster scanning
            
            response = ser.read(ser.in_waiting or 20)
            
            if response:
                parsed = parse_modbus_response(response)
                if parsed and not parsed.get('error') and 'registers' in parsed:
                    value = parsed['registers'][0]
                    found_registers[addr] = value
                    print(f"  0x{addr:04X}: {value} (0x{value:04X})")
            
        except Exception as e:
            continue
    
    return found_registers

def scan_multi_register_blocks(ser, slave_id, function_code, start_addr, max_registers=10):
    """Try to read multiple consecutive registers at once"""
    print(f"\n--- Testing Multi-Register Reads (FC{function_code:02X} from 0x{start_addr:04X}) ---")
    
    multi_data = {}
    
    for num_regs in [2, 4, 8, 16, 32]:
        if num_regs > max_registers:
            continue
            
        try:
            cmd = create_modbus_command(slave_id, function_code, start_addr, num_regs)
            
            ser.reset_input_buffer()
            ser.write(cmd)
            time.sleep(0.1)
            
            response = ser.read(ser.in_waiting or 100)
            
            if response:
                parsed = parse_modbus_response(response)
                if parsed and not parsed.get('error') and 'registers' in parsed:
                    print(f"  {num_regs} registers from 0x{start_addr:04X}: {parsed['registers']}")
                    multi_data[num_regs] = parsed['registers']
                    
        except Exception as e:
            continue
    
    return multi_data

def comprehensive_register_scan(port, baudrate=115200, slave_id=1):
    """Comprehensive register scanning"""
    print(f"=== Comprehensive Register Mapping ===")
    print(f"Device: {port} at {baudrate} baud, Slave ID: {slave_id}")
    
    all_registers = {
        'input_registers': {},    # Function Code 04
        'holding_registers': {},  # Function Code 03
        'multi_register_data': {}
    }
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1, parity=serial.PARITY_NONE, 
                           stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
        print("✓ Serial connection established")
        
        # Define register ranges to scan based on common solar controller layouts
        register_ranges = [
            # Device Information
            (0x0000, 0x001F, "Device Information"),
            (0x0100, 0x011F, "Device Configuration"),
            
            # Real-time Data (PV)
            (0x3100, 0x311F, "PV Real-time Data"),
            (0x3200, 0x321F, "Battery Real-time Data"), 
            (0x3300, 0x331F, "Load Real-time Data"),
            
            # Statistics
            (0x3300, 0x333F, "Daily Statistics"),
            (0x3340, 0x337F, "Monthly Statistics"),
            (0x3380, 0x33BF, "Yearly Statistics"),
            (0x33C0, 0x33FF, "Historical Data"),
            
            # Settings and Configuration
            (0x9000, 0x903F, "System Settings"),
            (0x9040, 0x907F, "Battery Settings"),
            (0x9080, 0x90BF, "Load Settings"),
            (0x90C0, 0x90FF, "Protection Settings"),
            
            # Extended ranges
            (0xA000, 0xA01F, "Extended Data A"),
            (0xB000, 0xB01F, "Extended Data B"),
            (0xC000, 0xC01F, "Extended Data C"),
        ]
        
        # Scan Input Registers (Function Code 04) - Real-time data
        print("\n" + "="*60)
        print("SCANNING INPUT REGISTERS (Function Code 04)")
        print("="*60)
        
        for start, end, desc in register_ranges:
            found = scan_register_range(ser, slave_id, 0x04, start, end, desc)
            all_registers['input_registers'].update(found)
            time.sleep(0.1)  # Brief pause between ranges
        
        # Scan Holding Registers (Function Code 03) - Configuration data
        print("\n" + "="*60)
        print("SCANNING HOLDING REGISTERS (Function Code 03)")
        print("="*60)
        
        for start, end, desc in register_ranges:
            found = scan_register_range(ser, slave_id, 0x03, start, end, desc)
            all_registers['holding_registers'].update(found)
            time.sleep(0.1)
        
        # Test multi-register reads for efficient data retrieval
        print("\n" + "="*60)
        print("TESTING MULTI-REGISTER READS")
        print("="*60)
        
        # Test multi-register reads on known working addresses
        if all_registers['input_registers']:
            first_addr = min(all_registers['input_registers'].keys())
            multi_data = scan_multi_register_blocks(ser, slave_id, 0x04, first_addr, 16)
            all_registers['multi_register_data']['input'] = multi_data
        
        if all_registers['holding_registers']:
            first_addr = min(all_registers['holding_registers'].keys())
            multi_data = scan_multi_register_blocks(ser, slave_id, 0x03, first_addr, 8)
            all_registers['multi_register_data']['holding'] = multi_data
        
    except Exception as e:
        print(f"Error during scanning: {e}")
    finally:
        if 'ser' in locals():
            ser.close()
    
    return all_registers

def analyze_and_categorize_registers(register_data):
    """Analyze register values and categorize them"""
    print("\n" + "="*60)
    print("REGISTER ANALYSIS AND CATEGORIZATION")
    print("="*60)
    
    analysis = {
        'voltage_registers': [],
        'current_registers': [],
        'power_registers': [],
        'temperature_registers': [],
        'status_registers': [],
        'time_registers': [],
        'counter_registers': [],
        'configuration_registers': [],
        'unknown_registers': []
    }
    
    # Analyze input registers (real-time data)
    print("\nInput Registers Analysis:")
    for addr, value in register_data['input_registers'].items():
        category = categorize_register_value(addr, value)
        analysis[category].append((addr, value))
        
        # Convert common values for display
        voltage_val = value / 100.0
        current_val = value / 100.0
        temp_val = value / 100.0 - 273.15  # Kelvin to Celsius
        
        print(f"  0x{addr:04X}: {value:5d} (0x{value:04X}) -> {category}")
        if category == 'voltage_registers':
            print(f"    Voltage: {voltage_val:.2f}V")
        elif category == 'current_registers':
            print(f"    Current: {current_val:.2f}A")
        elif category == 'temperature_registers':
            print(f"    Temperature: {temp_val:.1f}°C")
    
    # Analyze holding registers (configuration)
    print("\nHolding Registers Analysis:")
    for addr, value in register_data['holding_registers'].items():
        category = categorize_register_value(addr, value, is_holding=True)
        analysis[category].append((addr, value))
        print(f"  0x{addr:04X}: {value:5d} (0x{value:04X}) -> {category}")
    
    return analysis

def categorize_register_value(addr, value, is_holding=False):
    """Categorize register based on address and value patterns"""
    
    # Address-based categorization
    if 0x3100 <= addr <= 0x310F:  # PV data range
        if addr in [0x3100, 0x3104, 0x310C]:  # Known voltage addresses
            return 'voltage_registers'
        elif addr in [0x3101, 0x3105, 0x310D]:  # Known current addresses
            return 'current_registers'
        elif addr in [0x3102, 0x3103]:  # Power registers
            return 'power_registers'
    
    elif 0x3200 <= addr <= 0x32FF:  # Battery/status range
        return 'status_registers'
    
    elif 0x9000 <= addr <= 0x90FF:  # Configuration range
        return 'configuration_registers'
    
    # Value-based categorization
    if 1000 <= value <= 3000:  # Typical voltage range (10-30V * 100)
        return 'voltage_registers'
    elif 0 <= value <= 5000 and value % 10 == 0:  # Current-like values
        return 'current_registers'
    elif value > 10000:  # Large values might be counters
        return 'counter_registers'
    elif value == 0:  # Zero values
        return 'unknown_registers'
    
    return 'unknown_registers'

def save_register_map(register_data, analysis, filename="register_map.json"):
    """Save complete register map to JSON file"""
    output_data = {
        'scan_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'device_info': {
            'model': 'Tracer3210AN',
            'protocol': 'Modbus RTU',
            'slave_id': 1,
            'baudrate': 115200
        },
        'registers': register_data,
        'analysis': {k: [(hex(addr), val) for addr, val in v] for k, v in analysis.items()},
        'register_count': {
            'input_registers': len(register_data['input_registers']),
            'holding_registers': len(register_data['holding_registers']),
            'total': len(register_data['input_registers']) + len(register_data['holding_registers'])
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✓ Complete register map saved to {filename}")
    return filename

def main():
    port = "/dev/tty.usbserial-00000000"
    
    print("Starting comprehensive register mapping...")
    print("This may take several minutes to complete.")
    
    # Perform comprehensive scan
    register_data = comprehensive_register_scan(port)
    
    # Analyze the results
    analysis = analyze_and_categorize_registers(register_data)
    
    # Save results
    map_file = save_register_map(register_data, analysis)
    
    # Print summary
    print("\n" + "="*60)
    print("SCAN SUMMARY")
    print("="*60)
    print(f"Input Registers Found: {len(register_data['input_registers'])}")
    print(f"Holding Registers Found: {len(register_data['holding_registers'])}")
    print(f"Total Registers: {len(register_data['input_registers']) + len(register_data['holding_registers'])}")
    
    print(f"\nRegister Categories:")
    for category, registers in analysis.items():
        if registers:
            print(f"  {category.replace('_', ' ').title()}: {len(registers)}")
    
    print(f"\n✓ Complete register map saved to: {map_file}")
    print("✓ Ready to build CLI interface with full parameter support!")

if __name__ == "__main__":
    main()
