#!/usr/bin/env python3
"""
Modbus RTU Client for Tracer3210AN Solar Charger
Handles all Modbus communication with proper CRC and error handling
"""

import serial
import struct
import time
from typing import List, Dict, Optional, Union
from binascii import hexlify

class ModbusRTUClient:
    """Modbus RTU client for solar charger communication"""
    
    def __init__(self, port: str, baudrate: int = 115200, slave_id: int = 1, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.slave_id = slave_id
        self.timeout = timeout
        self.serial_conn = None
        
    def connect(self) -> bool:
        """Establish serial connection"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            return True
        except Exception as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        if self.connect():
            return self
        raise ConnectionError(f"Failed to connect to {self.port}")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    def calculate_crc16(self, data: bytes) -> bytes:
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
    
    def create_modbus_command(self, function_code: int, start_addr: int, num_registers: int) -> bytes:
        """Create a Modbus RTU command with CRC"""
        data = struct.pack('>BBHH', self.slave_id, function_code, start_addr, num_registers)
        crc = self.calculate_crc16(data)
        return data + crc
    
    def parse_modbus_response(self, response: bytes) -> Optional[Dict]:
        """Parse Modbus RTU response"""
        if len(response) < 5:
            return None
        
        slave_id = response[0]
        function_code = response[1]
        
        # Check for error response
        if function_code & 0x80:
            error_code = response[2]
            return {
                'slave_id': slave_id,
                'function_code': function_code & 0x7F,
                'error': True,
                'error_code': error_code,
                'error_message': self.get_error_message(error_code)
            }
        
        # Parse successful response
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
    
    def get_error_message(self, error_code: int) -> str:
        """Get human-readable error message"""
        error_messages = {
            1: "Illegal Function",
            2: "Illegal Data Address",
            3: "Illegal Data Value",
            4: "Slave Device Failure",
            5: "Acknowledge",
            6: "Slave Device Busy",
            8: "Memory Parity Error"
        }
        return error_messages.get(error_code, f"Unknown Error ({error_code})")
    
    def read_registers(self, function_code: int, start_addr: int, num_registers: int = 1) -> Optional[List[int]]:
        """Read registers from device"""
        if not self.serial_conn or not self.serial_conn.is_open:
            raise ConnectionError("Serial connection not established")
        
        try:
            # Create and send command
            cmd = self.create_modbus_command(function_code, start_addr, num_registers)
            
            self.serial_conn.reset_input_buffer()
            self.serial_conn.write(cmd)
            time.sleep(0.05)  # Brief delay for response
            
            # Read response
            response = self.serial_conn.read(self.serial_conn.in_waiting or (5 + num_registers * 2))
            
            if not response:
                return None
            
            # Parse response
            parsed = self.parse_modbus_response(response)
            
            if parsed and not parsed.get('error'):
                return parsed.get('registers', [])
            elif parsed and parsed.get('error'):
                print(f"Modbus Error: {parsed.get('error_message', 'Unknown error')}")
                return None
            
        except Exception as e:
            print(f"Error reading registers 0x{start_addr:04X}: {e}")
            return None
        
        return None
    
    def read_input_registers(self, start_addr: int, num_registers: int = 1) -> Optional[List[int]]:
        """Read input registers (Function Code 04)"""
        return self.read_registers(0x04, start_addr, num_registers)
    
    def read_holding_registers(self, start_addr: int, num_registers: int = 1) -> Optional[List[int]]:
        """Read holding registers (Function Code 03)"""
        return self.read_registers(0x03, start_addr, num_registers)
    
    def read_single_register(self, address: int, is_holding: bool = False) -> Optional[int]:
        """Read a single register"""
        if is_holding:
            result = self.read_holding_registers(address, 1)
        else:
            result = self.read_input_registers(address, 1)
        
        return result[0] if result else None
    
    def read_register_block(self, start_addr: int, count: int, is_holding: bool = False) -> Optional[Dict[int, int]]:
        """Read a block of consecutive registers efficiently"""
        if is_holding:
            values = self.read_holding_registers(start_addr, count)
        else:
            values = self.read_input_registers(start_addr, count)
        
        if values:
            return {start_addr + i: values[i] for i in range(len(values))}
        
        return None
    
    def write_single_register(self, address: int, value: int) -> bool:
        """Write a single holding register (Function Code 06)"""
        if not self.serial_conn or not self.serial_conn.is_open:
            raise ConnectionError("Serial connection not established")
        
        try:
            # Create write single register command (Function Code 06)
            data = struct.pack('>BBHH', self.slave_id, 0x06, address, value)
            crc = self.calculate_crc16(data)
            cmd = data + crc
            
            self.serial_conn.reset_input_buffer()
            self.serial_conn.write(cmd)
            time.sleep(0.1)  # Wait for response
            
            # Read response
            response = self.serial_conn.read(self.serial_conn.in_waiting or 8)
            
            if not response:
                return False
            
            # Parse response
            parsed = self.parse_modbus_response(response)
            
            if parsed and not parsed.get('error'):
                return True
            elif parsed and parsed.get('error'):
                print(f"Modbus Write Error: {parsed.get('error_message', 'Unknown error')}")
                return False
            
        except Exception as e:
            print(f"Error writing register 0x{address:04X}: {e}")
            return False
        
        return False
    
    def write_multiple_registers(self, start_addr: int, values: List[int]) -> bool:
        """Write multiple holding registers (Function Code 16)"""
        if not self.serial_conn or not self.serial_conn.is_open:
            raise ConnectionError("Serial connection not established")
        
        try:
            num_registers = len(values)
            byte_count = num_registers * 2
            
            # Create write multiple registers command (Function Code 16)
            header = struct.pack('>BBHHB', self.slave_id, 0x10, start_addr, num_registers, byte_count)
            
            # Pack register values
            data_bytes = b''
            for value in values:
                data_bytes += struct.pack('>H', value)
            
            # Complete command with CRC
            data = header + data_bytes
            crc = self.calculate_crc16(data)
            cmd = data + crc
            
            self.serial_conn.reset_input_buffer()
            self.serial_conn.write(cmd)
            time.sleep(0.1)
            
            # Read response
            response = self.serial_conn.read(self.serial_conn.in_waiting or 8)
            
            if not response:
                return False
            
            # Parse response
            parsed = self.parse_modbus_response(response)
            
            if parsed and not parsed.get('error'):
                return True
            elif parsed and parsed.get('error'):
                print(f"Modbus Write Error: {parsed.get('error_message', 'Unknown error')}")
                return False
            
        except Exception as e:
            print(f"Error writing registers starting at 0x{start_addr:04X}: {e}")
            return False
        
        return False
    
    def test_connection(self) -> bool:
        """Test connection by reading a known register"""
        try:
            # Try to read battery voltage (known working register)
            result = self.read_input_registers(0x3104, 1)
            return result is not None
        except:
            return False
