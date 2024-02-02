"""Aquarite Relay entity."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass : HomeAssistant, entry, async_add_entities) -> bool:
    """Set up a config entry."""
    dataservice = hass.data[DOMAIN].get(entry.entry_id)

    entities = []

    entities.append(AquariteSwitchEntity(hass, dataservice, "Relay1", "relays.relay1.info.onoff"))
    entities.append(AquariteSwitchEntity(hass, dataservice, "Relay2", "relays.relay2.info.onoff"))
    entities.append(AquariteSwitchEntity(hass, dataservice, "Relay3", "relays.relay3.info.onoff"))
    
    async_add_entities(entities)

class AquariteSwitchEntity(CoordinatorEntity, SwitchEntity):
    """Aquarite Relay Sensor Entity."""

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize a Aquarite Switch Entity."""
        super().__init__(dataservice)
        """ self._attr_device_info =  """
        self._dataservice = dataservice
        self._attr_name = name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + name

    @property
    def is_on(self):
        """Return true if the device is on."""
        return bool(self._dataservice.get_value(self._value_path))
        
    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        attributes = {}
        attributes['name'] = self._dataservice.get_value("relays.relay1.name")
        return attributes

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self._dataservice.turn_on_relay(self._attr_name)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self._dataservice.turn_off_relay(self._attr_name)

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id
