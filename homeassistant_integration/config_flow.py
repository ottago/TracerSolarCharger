"""Config flow for Tracer Solar Charger integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

# Import from copied shared library
from .tracer_solar_charger import ModbusRTUClient

from .const import DOMAIN, CONF_SLAVE_ID, CONF_BAUDRATE

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_PORT, default="/dev/ttyUSB0"): str,
    vol.Optional(CONF_SLAVE_ID, default=1): int,
    vol.Optional(CONF_BAUDRATE, default=115200): int,
})

async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    def test_connection():
        with ModbusRTUClient(
            data[CONF_PORT], 
            data[CONF_BAUDRATE], 
            data[CONF_SLAVE_ID],
            timeout=3.0
        ) as client:
            if not client.connect():
                return False
            info = client.read_device_info()
            return info.get('communication') == 'OK'
    
    # Test connection in executor
    connection_ok = await hass.async_add_executor_job(test_connection)
    
    if not connection_ok:
        raise CannotConnect
        
    return {"title": f"Tracer Solar Charger ({data[CONF_PORT]})"}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tracer Solar Charger."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
