"""GitHub sensor platform."""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
import logging
from pathlib import Path
import subprocess

import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
SCAN_INTERVAL = timedelta(minutes=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: Callable,
):
    """Set up sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    sensor = TapoP105Sensor(
        tapocli_path=Path(hass.config.config_dir)
        / "custom_components"
        / DOMAIN
        / "bin"
        / "tapo2",
        ip=config[CONF_IP_ADDRESS],
        username=config[CONF_USERNAME],
        password=config[CONF_PASSWORD],
    )
    async_add_entities([sensor], update_before_add=True)


# async def async_setup_platform(
#     hass: HomeAssistant,
#     config: ConfigType,
#     async_add_entities: Callable,
#     discovery_info: DiscoveryInfoType | None = None,
# ) -> None:
#     """Set up the sensor platform."""
#     # session = async_get_clientsession(hass)
#     # github = GitHubAPI(session, "requester", oauth_token=config[CONF_ACCESS_TOKEN])
#     # sensor = [GitHubRepoSensor(github, repo["path"]) for repo in config[CONF_REPOS]]
#     sensor = TapoP105Sensor(
#         config[CONF_IP_ADDRESS], config[CONF_USERNAME], config[CONF_PASSWORD]
#     )
#     async_add_entities(sensor, update_before_add=True)


class TapoP105Sensor(Entity):
    """Representation of a Tapo P105 sensor."""

    def __init__(
        self, tapocli_path: str, ip: str, username: str, password: str
    ) -> None:
        """Init for the tapo P105 sensor."""
        super().__init__()
        self.tapocli = tapocli_path
        self.ip = ip
        self.username = username
        self.password = password
        self._state = None
        self._id = None
        self.available = True
        self.has_entity_name = True

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the sensor."""
        return self._id

    @property
    def state(self) -> str | None:
        """Return status of the sensor."""
        return self._state

    async def async_update(self):
        """Update the sensor information."""
        res = subprocess.run(
            args="pwd", shell=True, capture_output=True, text=True, check=False
        )
        _LOGGER.log(level=logging.INFO, msg=res.stdout)
