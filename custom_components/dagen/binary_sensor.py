"""Dagen binary sensors."""
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass : HomeAssistant, entry, async_add_entities) -> bool:
    """Set up a config entry."""
    dataservice = hass.data[DOMAIN].get(entry.entry_id)

    entities = []

    entities.append(DagenBinarySensorEntity(hass, dataservice, "FL1", "hidro.fl1"))

    if dataservice.get_value( "main.hasCL"):
        entities.append(DagenBinarySensorEntity(hass, dataservice, "FL2", "hidro.fl2"))

    entities.append(DagenBinarySensorEntity(hass, dataservice, "Hidrolysis Low", "hidro.low"))

    async_add_entities(entities)

class DagenBinarySensorEntity(CoordinatorEntity, BinarySensorEntity):
    """Dagen Binary Sensor Entity such flow sensors FL1 & FL2."""

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize a Dagen Binary Sensor Entity."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._attr_name = name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + "-" + name

    @property
    def is_on(self):
        """Return true if the device is on."""
        return bool(self._dataservice.get_value(self._value_path))

    @property
    def device_class(self):
        """Return the class of the binary sensor."""
        return BinarySensorDeviceClass.PROBLEM

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id
