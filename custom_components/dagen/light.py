"""Dagen light entity."""
from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass : HomeAssistant, entry, async_add_entities) -> bool:
    """Set up a config entry."""
    dataservice = hass.data[DOMAIN].get(entry.entry_id)

    entities = []

    entities.append(DagenLightEntity(hass, dataservice, "Light", "light.status"))

    async_add_entities(entities)

class DagenLightEntity(CoordinatorEntity, LightEntity):
    """Dagen Light Sensor Entity."""


    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize a Dagen Light Sensor Entity."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._attr_name = name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = bool(self._dataservice.get_value(self._value_path))
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self._dataservice.turn_on_light()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self._dataservice.turn_off_light()

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id
