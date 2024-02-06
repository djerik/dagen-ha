"""Aquarite light entity."""
from homeassistant.components.light import LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, BRAND, MODEL
from .aquarite import Aquarite, UnauthorizedException

async def async_setup_entry(hass : HomeAssistant, entry, async_add_entities) -> bool:
    """Set up a config entry."""
    dataservice = hass.data[DOMAIN].get(entry.entry_id)

    entities = []

    entities.append(AquariteLightEntity(hass, dataservice, "Light", "light.status"))

    async_add_entities(entities)

class AquariteLightEntity(CoordinatorEntity, LightEntity):
    """Aquarite Light Sensor Entity."""

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize a Aquarite Light Sensor Entity."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._pool_id = dataservice.get_value("id") 
        self._attr_name = dataservice.get_pool_name(self._pool_id)+ "_" +  name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + name

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {
                (DOMAIN, self._dataservice.get_value("id"))
            },
            "name": dataservice.get_value("poolName"),
            "manufacturer": BRAND,
            "model": MODEL,
        }

    @property
    def is_on(self):
        """Return true if the device is on."""
        return bool(self._dataservice.get_value(self._value_path))

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
