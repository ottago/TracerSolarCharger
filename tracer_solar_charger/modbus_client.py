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
        
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        
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
            print(f"Connection failed: {e}")
            return False
            
    def disconnect(self):
        """Close serial connection"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            
    def _calculate_crc(self, data: bytes) -> int:
        """Calculate Modbus CRC16"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc
        
    def _send_request(self, request: bytes) -> Optional[bytes]:
        """Send Modbus request and receive response"""
        if not self.serial_conn or not self.serial_conn.is_open:
            return None
            
        try:
            self.serial_conn.flushInput()  # Clear input buffer
            self.serial_conn.write(request)
            time.sleep(0.05)  # Reduced delay
            
            # Read response header first (slave_id + function_code + byte_count)
            header = self.serial_conn.read(3)
            if len(header) < 3:
                return None
                
            # Calculate expected response length based on function code
            if header[1] in [0x03, 0x04]:  # Read registers
                byte_count = header[2]
                remaining = byte_count + 2  # data + CRC
            else:
                remaining = 5  # Standard response length
                
            # Read remaining bytes
            data = self.serial_conn.read(remaining)
            if len(data) < remaining:
                return None
                
            return header + data
            
        except Exception as e:
            print(f"Communication error: {e}")
            return None
            
    def read_input_registers(self, start_address: int, count: int = 1) -> Optional[List[int]]:
        """Read input registers (function code 0x04)"""
        request = struct.pack('>BBHH', self.slave_id, 0x04, start_address, count)
        crc = self._calculate_crc(request)
        request += struct.pack('<H', crc)
        
        response = self._send_request(request)
        if not response or len(response) < 5:
            return None
            
        if response[1] != 0x04:
            return None
            
        byte_count = response[2]
        if len(response) < 5 + byte_count:
            return None
            
        values = []
        for i in range(0, byte_count, 2):
            value = struct.unpack('>H', response[3 + i:5 + i])[0]
            values.append(value)
            
        return values
        
    def read_holding_registers(self, start_address: int, count: int = 1) -> Optional[List[int]]:
        """Read holding registers (function code 0x03)"""
        request = struct.pack('>BBHH', self.slave_id, 0x03, start_address, count)
        crc = self._calculate_crc(request)
        request += struct.pack('<H', crc)
        
        response = self._send_request(request)
        if not response or len(response) < 5:
            return None
            
        if response[1] != 0x03:
            return None
            
        byte_count = response[2]
        if len(response) < 5 + byte_count:
            return None
            
        values = []
        for i in range(0, byte_count, 2):
            value = struct.unpack('>H', response[3 + i:5 + i])[0]
            values.append(value)
            
        return values
        
    def write_single_register(self, address: int, value: int) -> bool:
        """Write single holding register (function code 0x06)"""
        request = struct.pack('>BBHH', self.slave_id, 0x06, address, value)
        crc = self._calculate_crc(request)
        request += struct.pack('<H', crc)
        
        response = self._send_request(request)
        if not response or len(response) < 8:
            return False
            
        return response[1] == 0x06 and struct.unpack('>H', response[2:4])[0] == address
        
    def read_combined_registers(self, low_address: int, high_address: int) -> Optional[int]:
        """Read two registers and combine them into a 32-bit value"""
        low_result = self.read_input_registers(low_address, 1)
        high_result = self.read_input_registers(high_address, 1)
        
        if low_result and high_result:
            return (high_result[0] << 16) | low_result[0]
        return None
        
    def read_device_info(self) -> Dict[str, Union[str, int]]:
        """Read basic device information for discovery"""
        info = {}
        
        # Try to read a known register to verify communication
        result = self.read_input_registers(0x3100, 1)  # PV voltage
        if result is not None:
            info['communication'] = 'OK'
            info['pv_voltage'] = result[0] * 0.01
        else:
            info['communication'] = 'FAILED'
            
        return info
