"""Coordinator for Aquarite."""
import asyncio
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

class AquariteDataCoordinator(DataUpdateCoordinator):
    """Aquarite custom coordinator."""

    def __init__(self, hass : HomeAssistant, api) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Aquarite",
        )
        self.api = api

    async def async_updated_data(self, data) -> None:
        """Update data."""
        super().async_set_updated_data(data)

    def set_updated_data(self, data) -> None:
        """Receive Data."""
        asyncio.run_coroutine_threadsafe( self.async_updated_data(data), self.hass.loop ).result()

    def get_value(self, path)-> Any:
        """Return part from document."""
        return self.data.get(path)

    async def turn_on_light(self)-> None:
        """Turn on pool light."""
        await self.api.turn_on_light( self.data.id )

    async def turn_off_light(self)-> None:
        """Turn off pool light."""
        await self.api.turn_off_light( self.data.id )
