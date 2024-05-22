"""GitHub sensor platform."""

from __future__ import annotations

from collections.abc import Callable
import logging

from homeassistant import config_entries, core

# from homeassistant.helpers.entity import Entity
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEVICE_NAME,
    DEVICE_ON,
    DOMAIN,
    HW_VERSION,
    MAC,
    MODEL,
    SW_VERSION,
    UNIQUE_ID,
)
from .coordinator import P105Coordinator
from .tapocli import TapoCli

_LOGGER = logging.getLogger(__name__)


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


class TapoP105Sensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Tapo P105 sensor."""

    def __init__(self, coordinator: P105Coordinator) -> None:
        """Init for the tapo P105 sensor."""
        super().__init__(coordinator)
        self.has_entity_name = True
        self._device_info = {
            "identifiers": {(DOMAIN, self.coordinator.data[UNIQUE_ID])},
            "name": self.coordinator.data[DEVICE_NAME],
            "sw_version": self.coordinator.data[SW_VERSION],
            "model": self.coordinator.data[MODEL],
            "manufacturer": "TAPO",
            "hw_version": self.coordinator.data[HW_VERSION],
            "connections": {
                (
                    dr.CONNECTION_NETWORK_MAC,
                    dr.format_mac(self.coordinator.data[MAC]),
                )
            },
        }
        self._attr_name = self.coordinator.data[DEVICE_NAME].strip().title()

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the sensor."""
        return self.coordinator.data[UNIQUE_ID]

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device_info

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device class."""
        return BinarySensorDeviceClass.PLUG

    @property
    def is_on(self) -> bool:
        """Return the device is on or off."""
        return self.coordinator.data[DEVICE_ON]

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()
