"""Simplified Modbus RTU client for Home Assistant integration."""

import serial
import struct
import time
import logging
from typing import Dict, List, Optional

_LOGGER = logging.getLogger(__name__)


class TracerModbusClient:
    """Simplified Modbus RTU client for Tracer solar charger."""

    def __init__(self, port: str, baudrate: int = 115200, slave_id: int = 1, timeout: float = 3.0):
        """Initialize the Modbus client."""
        self.port = port
        self.baudrate = baudrate
        self.slave_id = slave_id
        self.timeout = timeout
        self.serial_conn = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def connect(self) -> bool:
        """Establish serial connection."""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            _LOGGER.debug("Connected to %s at %d baud", self.port, self.baudrate)
            return True
        except Exception as err:
            _LOGGER.error("Failed to connect to %s: %s", self.port, err)
            return False

    def disconnect(self):
        """Close serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            _LOGGER.debug("Disconnected from %s", self.port)

    def calculate_crc16(self, data: bytes) -> bytes:
        """Calculate Modbus RTU CRC16."""
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
        """Create a Modbus RTU command with CRC."""
        data = struct.pack('>BBHH', self.slave_id, function_code, start_addr, num_registers)
        crc = self.calculate_crc16(data)
        return data + crc

    def parse_modbus_response(self, response: bytes) -> Optional[Dict]:
        """Parse Modbus RTU response."""
        if len(response) < 5:
            return None

        slave_id = response[0]
        function_code = response[1]

        # Check for error response
        if function_code & 0x80:
            error_code = response[2]
            _LOGGER.warning("Modbus error %d from slave %d", error_code, slave_id)
            return None

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
                'registers': registers
            }

        return None

    def read_registers(self, function_code: int, start_addr: int, num_registers: int = 1) -> Optional[List[int]]:
        """Read registers from device."""
        if not self.serial_conn or not self.serial_conn.is_open:
            _LOGGER.error("Serial connection not established")
            return None

        try:
            # Create and send command
            cmd = self.create_modbus_command(function_code, start_addr, num_registers)

            self.serial_conn.reset_input_buffer()
            self.serial_conn.write(cmd)
            time.sleep(0.05)  # Brief delay for response

            # Read response
            response = self.serial_conn.read(self.serial_conn.in_waiting or (5 + num_registers * 2))

            if not response:
                _LOGGER.warning("No response from device for address 0x%04X", start_addr)
                return None

            # Parse response
            parsed = self.parse_modbus_response(response)

            if parsed and 'registers' in parsed:
                return parsed['registers']

        except Exception as err:
            _LOGGER.error("Error reading registers 0x%04X: %s", start_addr, err)

        return None

    def read_input_registers(self, start_addr: int, num_registers: int = 1) -> Optional[List[int]]:
        """Read input registers (Function Code 04)."""
        return self.read_registers(0x04, start_addr, num_registers)

    def read_holding_registers(self, start_addr: int, num_registers: int = 1) -> Optional[List[int]]:
        """Read holding registers (Function Code 03)."""
        return self.read_registers(0x03, start_addr, num_registers)

    def read_register_block(self, start_addr: int, count: int, is_holding: bool = False) -> Optional[Dict[int, int]]:
        """Read a block of consecutive registers efficiently."""
        if is_holding:
            values = self.read_holding_registers(start_addr, count)
        else:
            values = self.read_input_registers(start_addr, count)

        if values:
            return {start_addr + i: values[i] for i in range(len(values))}

        return None

    def test_connection(self) -> bool:
        """Test connection by reading a known register."""
        try:
            # Try to read battery voltage (known working register)
            result = self.read_input_registers(0x3104, 1)
            return result is not None
        except Exception:
            return False
