"""Sensor platform for Tracer Solar Charger."""

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

# Import from our shared library
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from tracer_solar_charger import ModbusRTUClient, PARAMETERS

from .const import (
    DOMAIN,
    CONF_SLAVE_ID,
    CONF_BAUDRATE,
    DEFAULT_SCAN_INTERVAL,
    MANUFACTURER,
    MODEL,
    SENSOR_PARAMETERS,
    DEVICE_CLASSES,
    ICONS,
)

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
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via library."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with device: {exception}")

    def _fetch_data(self) -> Dict[str, Any]:
        """Fetch data from device."""
        data = {}
        
        with ModbusRTUClient(self.port, self.baudrate, self.slave_id, timeout=3.0) as client:
            if not client.connect():
                raise UpdateFailed("Failed to connect to device")
                
            for param_name in SENSOR_PARAMETERS:
                if param_name not in PARAMETERS:
                    continue
                    
                param = PARAMETERS[param_name]
                address = param['address']
                
                try:
                    # Handle combined registers (like power values)
                    if param.get('combine_registers'):
                        # Read both low and high registers
                        if param.get('function_code') == 4:
                            low_result = client.read_input_registers(address, 1)
                            high_result = client.read_input_registers(address + 1, 1)
                        else:
                            low_result = client.read_holding_registers(address, 1)
                            high_result = client.read_holding_registers(address + 1, 1)
                            
                        if low_result and high_result:
                            combined_value = (high_result[0] << 16) | low_result[0]
                            scaled_value = combined_value * param.get('scale', 1)
                            data[param_name] = scaled_value
                    else:
                        # Single register read
                        if param.get('function_code') == 4:
                            result = client.read_input_registers(address, 1)
                        else:
                            result = client.read_holding_registers(address, 1)
                            
                        if result:
                            raw_value = result[0]
                            scaled_value = raw_value * param.get('scale', 1)
                            data[param_name] = scaled_value
                            
                except Exception as e:
                    _LOGGER.warning(f"Failed to read {param_name}: {e}")
                    
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
        if self._attr_device_class in ['voltage', 'current', 'power', 'energy', 'temperature']:
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
        return self.coordinator.last_update_success and self.param_name in self.coordinator.data
