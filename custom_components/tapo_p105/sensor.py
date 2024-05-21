"""GitHub sensor platform."""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_NAME, DOMAIN, MODEL, SW_VERSION, UNIQUE_ID
from .coordinator import P105Coordinator
from .tapocli import TapoCli

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
    cli = TapoCli(
        hass.config.config_dir,
        config[CONF_IP_ADDRESS],
        config[CONF_USERNAME],
        config[CONF_PASSWORD],
    )
    coordinator = P105Coordinator(hass, cli)
    await coordinator.async_config_entry_first_refresh()

    sensor = TapoP105Sensor(coordinator)
    async_add_entities([sensor], update_before_add=True)


class TapoP105Sensor(CoordinatorEntity, Entity):
    """Representation of a Tapo P105 sensor."""

    def __init__(self, coordinator: P105Coordinator) -> None:
        """Init for the tapo P105 sensor."""
        super().__init__(coordinator)
        self.has_entity_name = True
        self._attr_name = self._sensor_config.name.strip().title()

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the sensor."""
        return self.coordinator.data[UNIQUE_ID]

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.data[UNIQUE_ID])},
            name=self.coordinator.data[DEVICE_NAME],
            sw_version=self.coordinator.data[SW_VERSION],
            model=self.coordinator.data[MODEL],
            manufacturer="TAPO",
        )
