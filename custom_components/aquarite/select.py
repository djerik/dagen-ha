"""Aquarite Select entity."""
from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

class PumpSelectOption:
    def __init__(self, value: int, text: str) -> None:
        self._value = value
        self._text = text

    @property
    def value(self):
        return self._value

    @property
    def text(self):
        return self._text

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
    def pump_options(self) -> list[PumpSelectOption]:
        allowed_values = list(['0', 'Manual', '1', 'Auto', '2', 'Heat', '3', 'Smart', '4', 'Intel'])
        return allowed_values
        
    @property
    def options(self) -> list[str]:
        return list(map(lambda option: option.text, self.pump_options))

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        pump_option = self.get_pump_state_by_text(option)

    def get_pump_state_by_value(self, value: int) -> PumpSelectOption:
        return next(option for option in self.pump_options if option.value == value)

    def get_pump_state_by_text(self, text: str) -> PumpSelectOption:
        return next(option for option in self.pump_options if option.text == text)

    @property
    def current_option(self):
        """Return current pump mode"""
        return self._dataservice.get_value(self._value_path)

    async def async_select_option(self, option: str):
       """Set pump mode"""
       await self._dataservice.set_pump_mode(self._attr_name, option)

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id
