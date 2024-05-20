"""config flow for tapo p105."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv

from .const import DEVICE_NAME, DOMAIN, UNIQUE_ID
from .tapocli import (
    AuthError,
    CannotConnectError,
    InvalidIpError,
    InvalidResponseError,
    TapoCli,
    UnknownError,
)

_LOGGER = logging.getLogger(__name__)

PARAM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


class TapoP105ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """tapo p105 config flow."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Invoke when a user initiates a flow via the user interface."""
        errors: dict[str, str] = {}
        if user_input is not None:
            cli = TapoCli(
                config_path=self.hass.config.config_dir,
                ip=user_input[CONF_IP_ADDRESS],
                username=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
            )
            try:
                dev_info = cli.info()
            except InvalidResponseError:
                errors["base"] = "response_error"
            except InvalidIpError:
                errors["ip"] = "ip_error"
            except CannotConnectError:
                errors["base"] = "connect_error"
            except AuthError:
                errors["base"] = "auth_error"
            except UnknownError:
                errors["base"] = "unknown_error"
            else:
                await self.async_set_unique_id(dev_info[UNIQUE_ID])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=dev_info[DEVICE_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=PARAM_SCHEMA, errors=errors
        )
