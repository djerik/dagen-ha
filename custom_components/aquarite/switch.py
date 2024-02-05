"""Aquarite Switch entity."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, BRAND, MODEL

async def async_setup_entry(hass : HomeAssistant, entry, async_add_entities) -> bool:
    """Set up a config entry."""
    dataservice = hass.data[DOMAIN].get(entry.entry_id)

    entities = []

    entities.append(AquariteSwitchEntity(hass, dataservice, "Electrolysis Cover", "hidro.cover_enabled"))

    """ entities.append(AquariteSwitchEntity(hass, dataservice, "Electrolysis Boost", "hidro.cloration_enabled")) """

    entities.append(AquariteRelayEntity(hass, dataservice, "Relay1", "relays.relay1.info.onoff"))
    entities.append(AquariteRelayEntity(hass, dataservice, "Relay2", "relays.relay2.info.onoff"))
    entities.append(AquariteRelayEntity(hass, dataservice, "Relay3", "relays.relay3.info.onoff"))
    
    async_add_entities(entities)

class AquariteSwitchEntity(CoordinatorEntity, SwitchEntity):
    """Aquarite Switch Entity."""

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize a Aquarite Switch Entity."""
        super().__init__(dataservice)
        """ self._attr_device_info =  """
        self._dataservice = dataservice
        self._attr_name = "Home_" + name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + name

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {
                (DOMAIN, self._dataservice.get_value("id"))
            },
            "name": "Home",
            "manufacturer": BRAND,
            "model": MODEL,
        }

    @property
    def is_on(self):
        """Return true if the device is on."""
        return bool(self._dataservice.get_value(self._value_path))
        
    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self._dataservice.turn_on_hidro_cover()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self._dataservice.turn_off_hidro_cover()

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id

class AquariteRelayEntity(CoordinatorEntity, SwitchEntity):
    """Aquarite Relay Entity."""

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize a Aquarite Relay Entity."""
        super().__init__(dataservice)
        """ self._attr_device_info =  """
        self._dataservice = dataservice
        self._attr_name = "Home_" + name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + name

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {
                (DOMAIN, self._dataservice.get_value("id"))
            },
            "name": "Home",
            "manufacturer": BRAND,
            "model": MODEL,
        }

    @property
    def is_on(self):
        """Return true if the device is on."""
        return bool(self._dataservice.get_value(self._value_path))
        
    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        attributes = {}
        attributes['name'] = self._dataservice.get_value("relays." + self.name.lower() + ".name")
        return attributes

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self._dataservice.turn_on_relay(self.name)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self._dataservice.turn_off_relay(self.name)

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id
