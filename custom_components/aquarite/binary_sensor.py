"""Aquarite binary sensors."""
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PATH_HASCD, PATH_HASCL, PATH_HASPH, PATH_HASRX


async def async_setup_entry(hass : HomeAssistant, entry, async_add_entities) -> bool:
    """Set up a config entry."""
    dataservice = hass.data[DOMAIN].get(entry.entry_id)

    entities = []

    entities.append(AquariteBinarySensorEntity(hass, dataservice, "FL1", "hidro.fl1"))

    entities.append(AquariteBinarySensorEntity(hass, dataservice, "Filtration Status", "filtration.status"))
    
    entities.append(AquariteBinarySensorEntity(hass, dataservice, "Backwash Status", "backwash.status"))
   
    if dataservice.get_value( "main.hasCL"):
        entities.append(AquariteBinarySensorEntity(hass, dataservice, "FL2", "hidro.fl2"))

    if dataservice.get_value( PATH_HASCD ) or \
       dataservice.get_value( PATH_HASCL ) or \
       dataservice.get_value( PATH_HASPH ) or \
       dataservice.get_value( PATH_HASRX ):
        entities.append(AquariteBinarySensorTankEntity(hass, dataservice, "Acid Tank" ) )

    entities.append(AquariteBinarySensorEntity(hass, dataservice, "Electrolysis Low" if dataservice.get_value( "hidro.is_electrolysis") else "Hidrolysis Low", "hidro.low"))

    async_add_entities(entities)

class AquariteBinarySensorEntity(CoordinatorEntity, BinarySensorEntity):
    """Aquarite Binary Sensor Entity such flow sensors FL1 & FL2."""

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize a Aquarite Binary Sensor Entity."""
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
        if self._value_path == "backwash.status":
           return BinarySensorDeviceClass.RUNNING
            
        return BinarySensorDeviceClass.PROBLEM
    
    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id

class AquariteBinarySensorTankEntity(CoordinatorEntity, BinarySensorEntity):
    """Aquarite Binary Sensor Entity Tank."""

    def __init__(self, hass : HomeAssistant, dataservice, name) -> None:
        """Initialize a Aquarite Binary Sensor Entity."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._attr_name = name
        self._unique_id = dataservice.get_value("id") + "-" + name

    @property
    def is_on(self):
        """Return false if the tank is empty."""
        if( self._dataservice.get_value("modules.ph.tank") or \
            self._dataservice.get_value("modules.rx.tank") or \
            self._dataservice.get_value("modules.cl.tank") or \
            self._dataservice.get_value("modules.cd.tank")
        ):
            return True
        return False

    @property
    def device_class(self):
        """Return the class of the binary sensor."""
        return BinarySensorDeviceClass.PROBLEM

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id
