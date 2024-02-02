"""Aquarite Select entity."""
from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass : HomeAssistant, entry, async_add_entities) -> bool:
    """Set up a config entry."""
    dataservice = hass.data[DOMAIN].get(entry.entry_id)

    entities = []

    entities.append(AquariteSelectEntity(hass, dataservice, "Pump Mode", "filtration.mode"))
    
    async_add_entities(entities)

class AquariteSelectEntity(CoordinatorEntity, SelectEntity):
    """Aquarite Select Entity."""

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize a Aquarite Select Entity."""
        super().__init__(dataservice)
         """ self._attr_device_info =  """
        self._dataservice = dataservice
        self._attr_name = name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + name

    @property
    def current_option(self):
        """Return current pump mode"""
        return self._dataservice.get_value(self._value_path)

    async def async_select_option(self, **kwargs):
       """Set pump mode"""
       await self._dataservice.set_pump_mode(self._attr_name)

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id