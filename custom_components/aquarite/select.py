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
        self._allowed_values = ["Manual", "Auto", "Heating", "Smart", "Intel"]
       
    @property
    def options(self) -> list[str]:
        return list(self._allowed_values)

    @property
    def current_option(self) -> str:
        """Return current pump mode"""      
        return self._allowed_values[self._dataservice.get_value(self._value_path)]

    async def async_select_option(self, option: str):
       """Set pump mode"""
       await self._dataservice.set_pump_mode(self._attr_name, self._allowed_values.index(option))

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id
