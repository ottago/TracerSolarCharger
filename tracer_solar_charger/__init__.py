"""Tracer Solar Charger - Core library for CLI and Home Assistant integration."""

from .modbus_client import ModbusRTUClient
from .device_data import DeviceData
from .parameter_definitions import PARAMETERS

__version__ = "1.0.0"
__all__ = ["ModbusRTUClient", "DeviceData", "PARAMETERS"]
