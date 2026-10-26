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
        
    def _send_request(self, request: bytes, retries: int = 1) -> Optional[bytes]:
        """Send a Modbus request and return a fully validated response frame.

        The RS485 bus may be shared with other devices, so a frame is only accepted when
        the slave ID, function code, length and CRC all match. Anything else (timeouts,
        another device's reply, corrupt frames) is retried and then reported as None.
        """
        for attempt in range(retries):
            response = self._transact(request)
            if response is not None:
                return response
            time.sleep(0.1 * (attempt + 1))
        return None

    def _transact(self, request: bytes) -> Optional[bytes]:
        """Single request/response exchange with frame validation."""
        if not self.serial_conn or not self.serial_conn.is_open:
            return None

        try:
            self.serial_conn.reset_input_buffer()  # discard leftovers from other devices
            self.serial_conn.write(request)
            time.sleep(0.05)

            header = self.serial_conn.read(3)  # slave_id + function_code + byte_count/exception
            if len(header) < 3:
                return None
            if header[0] != self.slave_id:
                return None  # reply from another device on the shared bus

            function = request[1]
            if header[1] == function | 0x80:
                self.serial_conn.read(2)  # exception frame: drain CRC, report as failure
                return None
            if header[1] != function:
                return None

            if function in (0x03, 0x04):
                remaining = header[2] + 2  # data + CRC
            else:
                remaining = 5  # write echoes are 8 bytes in total
            data = self.serial_conn.read(remaining)
            if len(data) < remaining:
                return None

            frame = header + data
            received_crc = struct.unpack('<H', frame[-2:])[0]
            if self._calculate_crc(frame[:-2]) != received_crc:
                return None
            return frame

        except Exception as e:
            print(f"Communication error: {e}")
            return None

    def _read_registers(self, function: int, start_address: int, count: int,
                        retries: int = 3) -> Optional[List[int]]:
        """Read registers with function 0x03/0x04, returning exactly `count` values or None."""
        request = struct.pack('>BBHH', self.slave_id, function, start_address, count)
        request += struct.pack('<H', self._calculate_crc(request))

        response = self._send_request(request, retries=retries)
        if not response or response[2] != count * 2 or len(response) != 5 + count * 2:
            return None

        return list(struct.unpack('>%dH' % count, response[3:3 + count * 2]))

    def read_input_registers(self, start_address: int, count: int = 1) -> Optional[List[int]]:
        """Read input registers (function code 0x04)"""
        return self._read_registers(0x04, start_address, count)

    def read_holding_registers(self, start_address: int, count: int = 1) -> Optional[List[int]]:
        """Read holding registers (function code 0x03)"""
        return self._read_registers(0x03, start_address, count)

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
        """Read two registers and combine them into a 32-bit value.

        Adjacent registers are fetched in one request so the two halves always belong to
        the same sample (separate reads can straddle an update and give a torn value).
        """
        if high_address == low_address + 1:
            result = self.read_input_registers(low_address, 2)
            if result:
                return (result[1] << 16) | result[0]
            return None

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
