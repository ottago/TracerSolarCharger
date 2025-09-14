"""
Tracer Solar Charger integration for Home Assistant.
Provides monitoring of Tracer3210AN solar charge controller via Modbus RTU.
"""
import asyncio
import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_SLAVE_ID, CONF_BAUDRATE, DEFAULT_SCAN_INTERVAL
from .modbus_client import TracerModbusClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DEVICE): cv.string,
                vol.Optional(CONF_PORT, default="/dev/ttyUSB0"): cv.string,
                vol.Optional(CONF_SLAVE_ID, default=1): cv.positive_int,
                vol.Optional(CONF_BAUDRATE, default=115200): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


class TracerSolarChargerCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Tracer Solar Charger."""

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        """Initialize the coordinator."""
        self.config = config
        self.client = TracerModbusClient(
            port=config[CONF_DEVICE],
            baudrate=config.get(CONF_BAUDRATE, 115200),
            slave_id=config.get(CONF_SLAVE_ID, 1),
        )
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from the solar charger."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with solar charger: {err}")

    def _fetch_data(self):
        """Fetch data from the solar charger (runs in executor)."""
        try:
            with self.client:
                # Read all available parameters efficiently
                data = {}
                
                # Read real-time data blocks
                realtime_blocks = [
                    (0x3100, 16, "realtime_core"),      # PV, Battery, Load core data
                    (0x3110, 16, "realtime_extended"),  # Temperatures, SOC
                    (0x3200, 3, "status"),              # System status
                    (0x3300, 31, "statistics"),         # Daily statistics
                ]
                
                for start_addr, count, block_name in realtime_blocks:
                    block_data = self.client.read_register_block(start_addr, count, is_holding=False)
                    if block_data:
                        data.update(block_data)
                
                # Read configuration data (less frequently)
                config_blocks = [
                    (0x9000, 8, "config_voltages"),     # Core voltage settings
                    (0x9008, 8, "config_extended"),     # Extended configuration
                ]
                
                for start_addr, count, block_name in config_blocks:
                    block_data = self.client.read_register_block(start_addr, count, is_holding=True)
                    if block_data:
                        data.update(block_data)
                
                return data
                
        except Exception as err:
            _LOGGER.error("Failed to fetch data from solar charger: %s", err)
            raise


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Tracer Solar Charger component."""
    if DOMAIN not in config:
        return True

    hass.data.setdefault(DOMAIN, {})
    
    # Create coordinator
    coordinator = TracerSolarChargerCoordinator(hass, config[DOMAIN])
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN]["coordinator"] = coordinator
    
    # Load platforms
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.helpers.discovery.async_load_platform(platform, DOMAIN, {}, config)
        )
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tracer Solar Charger from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    coordinator = TracerSolarChargerCoordinator(hass, entry.data)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
