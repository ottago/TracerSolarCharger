"""Sensor platform for Tracer Solar Charger."""

import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

# Import from copied shared library
from .tracer_solar_charger import ModbusRTUClient, PARAMETERS

from .const import (
    DOMAIN,
    CONF_SLAVE_ID,
    CONF_BAUDRATE,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    MANUFACTURER,
    MODEL,
    SENSOR_PARAMETERS,
    VALID_RANGES,
    INVALID_RAW_VALUES,
    CONFIRM_ZERO_PARAMETERS,
    DEVICE_CLASSES,
    ICONS,
)

from . import get_port_lock

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    
    coordinator = TracerDataUpdateCoordinator(hass, config_entry)
    await coordinator.async_config_entry_first_refresh()
    
    entities = []
    for param_name in SENSOR_PARAMETERS:
        if param_name in PARAMETERS:
            entities.append(TracerSensorEntity(coordinator, param_name))
    
    async_add_entities(entities)

class TracerDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Tracer device."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize."""
        self.config_entry = config_entry
        self.port = config_entry.data[CONF_PORT]
        self.slave_id = config_entry.data.get(CONF_SLAVE_ID, 1)
        self.baudrate = config_entry.data.get(CONF_BAUDRATE, 115200)
        self._port_lock = get_port_lock(hass, self.port)
        self._last_good: Dict[str, float] = {}
        scan_interval = config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via library, holding the port lock."""
        async with self._port_lock:
            try:
                return await self.hass.async_add_executor_job(self._fetch_data)
            except Exception as exception:
                raise UpdateFailed(f"Error communicating with device: {exception}")

    def _read_parameter(self, client: ModbusRTUClient, param_name: str) -> Optional[float]:
        """Read one parameter; None when the read failed or the value is not plausible."""
        param = PARAMETERS[param_name]
        address = param['address']

        if param.get('combine_registers'):
            raw_value = client.read_combined_registers(address, param['high_address'])
        else:
            if param.get('function_code') == 4:
                result = client.read_input_registers(address, 1)
            else:
                result = client.read_holding_registers(address, 1)
            raw_value = result[0] if result else None

        if raw_value is None:
            return None
        if raw_value in INVALID_RAW_VALUES:
            _LOGGER.debug(f"Discarding {param_name}: raw value {raw_value:#x} means no data")
            return None

        scaled_value = raw_value * param.get('scale', 1)
        valid_range = VALID_RANGES.get(param_name)
        if valid_range and not valid_range[0] <= scaled_value <= valid_range[1]:
            _LOGGER.debug(f"Discarding {param_name}: {scaled_value} outside {valid_range}")
            return None

        return scaled_value

    def _fetch_data(self) -> Dict[str, Any]:
        """Fetch data from device."""
        data = {}
        _LOGGER.debug(f"Attempting to fetch data from {self.port}")

        try:
            with ModbusRTUClient(self.port, self.baudrate, self.slave_id, timeout=3.0) as client:
                if not client.connect():
                    _LOGGER.error(f"Failed to connect to device at {self.port}")
                    raise UpdateFailed("Failed to connect to device")

                _LOGGER.debug(f"Connected successfully to {self.port}")

                for param_name in SENSOR_PARAMETERS:
                    if param_name not in PARAMETERS:
                        _LOGGER.warning(f"Parameter {param_name} not found in PARAMETERS")
                        continue

                    try:
                        value = self._read_parameter(client, param_name)

                        # Confirm a sudden drop to exactly zero before trusting it
                        if (value == 0
                                and param_name in CONFIRM_ZERO_PARAMETERS
                                and self._last_good.get(param_name, 0) > 0):
                            value = self._read_parameter(client, param_name)
                            _LOGGER.debug(f"Re-read {param_name} after zero: {value}")

                        if value is None:
                            _LOGGER.debug(f"No valid data for {param_name}")
                            continue

                        data[param_name] = value
                        self._last_good[param_name] = value
                        _LOGGER.debug(f"Read {param_name}: {value}")

                    except Exception as e:
                        _LOGGER.error(f"Failed to read {param_name}: {e}")

        except Exception as e:
            _LOGGER.error(f"Connection error: {e}")
            raise UpdateFailed(f"Connection error: {e}")

        _LOGGER.info(f"Successfully read {len(data)} parameters")
        return data

class TracerSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of a Tracer sensor."""

    def __init__(self, coordinator: TracerDataUpdateCoordinator, param_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self.param_name = param_name
        self.param_info = PARAMETERS[param_name]
        
        self._attr_name = f"Tracer {self.param_info.get('description', param_name.replace('_', ' ').title())}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{param_name}"
        
        # Set device class
        for device_class, params in DEVICE_CLASSES.items():
            if param_name in params:
                self._attr_device_class = device_class
                break
                
        # Set icon based on category
        category = self.param_info.get('category', 'system')
        self._attr_icon = ICONS.get(category, "mdi:gauge")
        
        # Set unit of measurement
        self._attr_native_unit_of_measurement = self.param_info.get('unit')
        
        # Set state class for numeric sensors
        if hasattr(self, '_attr_device_class') and self._attr_device_class in ['voltage', 'current', 'power', 'energy', 'temperature']:
            self._attr_state_class = "measurement"

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "Tracer Solar Charger",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": "1.0.0",
        }

    @property
    def native_value(self) -> Optional[float]:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.param_name)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success 
            and self.param_name in self.coordinator.data 
            and self.coordinator.data[self.param_name] is not None
        )

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        return {
            "address": f"0x{self.param_info['address']:04X}",
            "category": self.param_info.get('category', 'unknown'),
        }
