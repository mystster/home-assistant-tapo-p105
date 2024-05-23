"""my coordinator using DataUpdateCoordinator."""

from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .tapocli import TapoCli

_LOGGER = logging.getLogger(__name__)


class P105Coordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, cli: TapoCli):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Tapo for p105",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(minutes=2),
        )
        self.cli = cli

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        return self.cli.info()
