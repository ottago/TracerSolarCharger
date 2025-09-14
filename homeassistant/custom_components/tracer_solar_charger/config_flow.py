"""Config flow for Tracer Solar Charger integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_SLAVE_ID, CONF_BAUDRATE
from .modbus_client import TracerModbusClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE, default="/dev/ttyUSB0"): str,
        vol.Optional(CONF_SLAVE_ID, default=1): vol.All(int, vol.Range(min=1, max=247)),
        vol.Optional(CONF_BAUDRATE, default=115200): vol.In([9600, 19200, 38400, 57600, 115200]),
    }
)


async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    def test_connection():
        """Test connection in executor."""
        client = TracerModbusClient(
            port=data[CONF_DEVICE],
            baudrate=data[CONF_BAUDRATE],
            slave_id=data[CONF_SLAVE_ID],
        )
        
        try:
            with client:
                return client.test_connection()
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False
    
    # Test connection in executor to avoid blocking
    connection_ok = await hass.async_add_executor_job(test_connection)
    
    if not connection_ok:
        raise CannotConnect
    
    # Return info that you want to store in the config entry
    return {
        "title": f"Tracer Solar Charger ({data[CONF_DEVICE]})",
        "device": data[CONF_DEVICE],
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tracer Solar Charger."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Check if already configured
                await self.async_set_unique_id(user_input[CONF_DEVICE])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
