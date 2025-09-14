"""Sensor platform for Tracer Solar Charger integration."""

import logging
from typing import Any, Dict, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MANUFACTURER,
    MODEL,
    SENSOR_TYPES,
    BATTERY_STATUS_BITS,
    CHARGING_STATUS_BITS,
    LOAD_STATUS_BITS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tracer Solar Charger sensors from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    
    # Create sensor entities for each sensor type
    for sensor_key, sensor_config in SENSOR_TYPES.items():
        entities.append(
            TracerSolarChargerSensor(
                coordinator=coordinator,
                config_entry=config_entry,
                sensor_key=sensor_key,
                sensor_config=sensor_config,
            )
        )
    
    async_add_entities(entities, True)


class TracerSolarChargerSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Tracer Solar Charger sensor."""

    def __init__(
        self,
        coordinator,
        config_entry: ConfigEntry,
        sensor_key: str,
        sensor_config: Dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self._config_entry = config_entry
        self._sensor_key = sensor_key
        self._sensor_config = sensor_config
        self._attr_name = f"Solar Charger {sensor_config['name']}"
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_key}"
        
        # Set device class and state class
        if "device_class" in sensor_config:
            self._attr_device_class = getattr(SensorDeviceClass, sensor_config["device_class"].upper(), None)
        
        if "state_class" in sensor_config:
            self._attr_state_class = getattr(SensorStateClass, sensor_config["state_class"].upper(), None)
        
        # Set unit and icon
        self._attr_native_unit_of_measurement = sensor_config.get("unit")
        self._attr_icon = sensor_config.get("icon")
        
        # Set device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name="Tracer Solar Charger",
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version="1.0",
            via_device=(DOMAIN, config_entry.entry_id),
        )

    @property
    def native_value(self) -> Optional[float]:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        address = self._sensor_config["address"]
        raw_value = self.coordinator.data.get(address)
        
        if raw_value is None:
            return None
        
        # Handle combined registers (32-bit values)
        if self._sensor_config.get("combine_registers"):
            high_address = self._sensor_config.get("high_address")
            high_value = self.coordinator.data.get(high_address, 0)
            # Combine low and high words into 32-bit value
            combined_value = (high_value << 16) | raw_value
            raw_value = combined_value
        
        # Handle status/enum types
        if self._sensor_config.get("type") == "status":
            return self._format_status_value(raw_value)
        elif self._sensor_config.get("type") == "enum":
            enum_values = self._sensor_config.get("enum_values", {})
            return enum_values.get(raw_value, f"Unknown ({raw_value})")
        
        # Apply scaling
        scaled_value = raw_value * self._sensor_config.get("scale", 1)
        
        # Apply offset if present (for temperature conversions)
        if "offset" in self._sensor_config:
            scaled_value += self._sensor_config["offset"]
        
        return round(scaled_value, 2)

    def _format_status_value(self, raw_value: int) -> str:
        """Format status register values as human-readable text."""
        if self._sensor_key == "battery_status":
            return self._format_bitfield(raw_value, BATTERY_STATUS_BITS)
        elif self._sensor_key == "charging_status":
            return self._format_bitfield(raw_value, CHARGING_STATUS_BITS)
        elif self._sensor_key == "load_status":
            return self._format_bitfield(raw_value, LOAD_STATUS_BITS)
        else:
            return str(raw_value)

    def _format_bitfield(self, value: int, bit_definitions: Dict[int, str]) -> str:
        """Format a bitfield value using bit definitions."""
        active_bits = []
        for bit, description in bit_definitions.items():
            if value & (1 << bit):
                active_bits.append(description)
        
        return ", ".join(active_bits) if active_bits else "Normal"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        attributes = {
            "category": self._sensor_config.get("category"),
            "address": f"0x{self._sensor_config['address']:04X}",
        }
        
        # Add raw value for debugging
        if self.coordinator.data:
            raw_value = self.coordinator.data.get(self._sensor_config["address"])
            if raw_value is not None:
                attributes["raw_value"] = raw_value
        
        return attributes

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self._sensor_config["address"] in self.coordinator.data
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
