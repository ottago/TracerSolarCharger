"""Config flow for Tracer Solar Charger integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .tracer_solar_charger import ModbusRTUClient

from .const import DOMAIN, CONF_SLAVE_ID, CONF_BAUDRATE, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

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
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle reconfiguration of connection settings."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])

        if user_input is None:
            return self.async_show_form(
                step_id="reconfigure",
                data_schema=vol.Schema({
                    vol.Required(CONF_PORT, default=entry.data.get(CONF_PORT, "/dev/ttyUSB0")): str,
                    vol.Optional(CONF_SLAVE_ID, default=entry.data.get(CONF_SLAVE_ID, 1)): int,
                    vol.Optional(CONF_BAUDRATE, default=entry.data.get(CONF_BAUDRATE, 115200)): int,
                }),
            )

        errors = {}

        try:
            await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_update_reload_and_abort(
                entry, data=user_input, reason="reconfigure_successful"
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({
                vol.Required(CONF_PORT, default=user_input.get(CONF_PORT)): str,
                vol.Optional(CONF_SLAVE_ID, default=user_input.get(CONF_SLAVE_ID, 1)): int,
                vol.Optional(CONF_BAUDRATE, default=user_input.get(CONF_BAUDRATE, 115200)): int,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Tracer Solar Charger."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.All(int, vol.Range(min=5, max=300)),
            }),
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
