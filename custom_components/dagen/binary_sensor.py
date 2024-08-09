"""Dagen binary sensors."""
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PATH_HASCD, PATH_HASCL, PATH_HASPH, PATH_HASRX


async def async_setup_entry(hass : HomeAssistant, entry, async_add_entities) -> bool:
    """Set up a config entry."""
    dataservice = hass.data[DOMAIN].get(entry.entry_id)

    entities = []

    entities.append(DagenBinarySensorEntity(hass, dataservice, "FL1", "hidro.fl1"))

    if dataservice.get_value( "main.hasCL"):
        entities.append(DagenBinarySensorEntity(hass, dataservice, "FL2", "hidro.fl2"))

    if dataservice.get_value( PATH_HASCD ) or \
       dataservice.get_value( PATH_HASCL ) or \
       dataservice.get_value( PATH_HASPH ) or \
       dataservice.get_value( PATH_HASRX ):
        entities.append(DagenBinarySensorTankEntity(hass, dataservice, "Acid Tank" ) )

    entities.append(DagenBinarySensorEntity(hass, dataservice, "Electrolysis Low" if dataservice.get_value( "hidro.is_electrolysis") else "Hidrolysis Low", "hidro.low"))

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

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = bool(self._dataservice.get_value(self._value_path))
        self.async_write_ha_state()

    @property
    def device_class(self):
        """Return the class of the binary sensor."""
        return BinarySensorDeviceClass.PROBLEM

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id

class DagenBinarySensorTankEntity(CoordinatorEntity, BinarySensorEntity):
    """Dagen Binary Sensor Entity Tank."""

    def __init__(self, hass : HomeAssistant, dataservice, name) -> None:
        """Initialize a Dagen Binary Sensor Entity."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._attr_name = name
        self._unique_id = dataservice.get_value("id") + "-" + name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if( self._dataservice.get_value("modules.ph.tank") or \
            self._dataservice.get_value("modules.rx.tank") or \
            self._dataservice.get_value("modules.cl.tank") or \
            self._dataservice.get_value("modules.cd.tank")
        ):
            self._attr_is_on = True
        else:
            self._attr_is_on = False
        self.async_write_ha_state()

    @property
    def device_class(self):
        """Return the class of the binary sensor."""
        return BinarySensorDeviceClass.PROBLEM

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id
