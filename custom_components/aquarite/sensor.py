"""Aquarite value sensors."""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfElectricPotential, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    BRAND,
    MODEL,
    PATH_HASCD,
    PATH_HASCL,
    PATH_HASHIDRO,
    PATH_HASPH,
    PATH_HASRX,
    PATH_HASUV,
)


async def async_setup_entry(hass : HomeAssistant, entry, async_add_entities) -> bool:
    """Set up a config entry."""
    dataservice = hass.data[DOMAIN].get(entry.entry_id)

    entities = []

    entities.append(
        AquariteTemperatureSensorEntity(
            hass,
            dataservice,
            "Temperature",
            "main.temperature",
        ),
    )

    if dataservice.get_value( PATH_HASCD ):
        entities.append(
            AquariteValueSensorEntity(
                hass,
                dataservice,
                "CD",
                "modules.cd.current",
            ),
        )

    if dataservice.get_value( PATH_HASCL ):
        entities.append(
            AquariteValueSensorEntity(
                hass,
                dataservice,
                "Cl",
                "modules.cl.current",
                None,
                None,
                "mdi:gauge"
            ),
        )

    if dataservice.get_value( PATH_HASPH ):
        entities.append(
            AquariteValueSensorEntity(
                hass,
                dataservice,
                "pH",
                "modules.ph.current",
                SensorDeviceClass.PH,
                None
            ),
        )

    if dataservice.get_value( PATH_HASRX ):
        entities.append(
            AquariteRxValueSensorEntity(
                hass,
                dataservice,
                "Rx",
                "modules.rx.current",
            ),
        )

    if dataservice.get_value( PATH_HASUV ):
        entities.append(
            AquariteValueSensorEntity(
                hass,
                dataservice,
                "UV",
                "modules.uv.current",
            ),
        )

    if dataservice.get_value( PATH_HASHIDRO ):
        entities.append(
            AquariteHydrolyserSensorEntity(
                hass,
                dataservice,
                "Electrolysis" if dataservice.get_value( "hidro.is_electrolysis") else "Hidrolysis",
                "hidro.current",
            ),
        )
    
    async_add_entities(entities)

class AquariteTemperatureSensorEntity(CoordinatorEntity, SensorEntity):
    """Aquarite Temperature Sensor Entity."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize Temperature Sensor."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._pool_id = dataservice.get_value("id") 
        self._attr_name = dataservice.get_pool_name(self._pool_id) + "_" +  name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + "-" + name

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {
                (DOMAIN, self._dataservice.get_value("id"))
            },
            "name": self._dataservice.get_pool_name(self._pool_id),
            "manufacturer": BRAND,
            "model": MODEL,
        }

    @property
    def native_value(self):
        """Return temperature."""
        return self._dataservice.get_value(self._value_path)

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id

class AquariteValueSensorEntity(CoordinatorEntity, SensorEntity):
    """Aquarite Value Sensor Entity."""

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path, device_class:SensorDeviceClass = None, native_unit_of_measurement:str = None, icon:str = None) -> None:
        """Initialize Value Sensor such as pH."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._pool_id = dataservice.get_value("id") 
        self._attr_name = dataservice.get_pool_name(self._pool_id) + "_" +  name
        self._value_path = value_path
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = native_unit_of_measurement
        self._attr_icon = icon
        self._unique_id = dataservice.get_value("id") + "-" + name

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {
                (DOMAIN, self._pool_id)
            },
            "name": self._dataservice.get_pool_name(self._pool_id),
            "manufacturer": BRAND,
            "model": MODEL,
        }

    @property
    def native_value(self):
        """Return value of sensor."""
        return float(self._dataservice.get_value(self._value_path)) / 100

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id

class AquariteHydrolyserSensorEntity(CoordinatorEntity, SensorEntity):
    """Aquarite Hydrolyser Sensor Entity."""

    _attr_icon = "mdi:gauge"
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize Hydrolyser Sensor."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._pool_id = dataservice.get_value("id") 
        self._attr_name = dataservice.get_pool_name(self._pool_id)+ "_" +  name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + "-" + name
        
    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {
                (DOMAIN, self._pool_id)
            },
            "name": self._dataservice.get_pool_name(self._pool_id),
            "manufacturer": BRAND,
            "model": MODEL,
        }

    @property
    def native_value(self) -> float:
        """Return value of sensor."""
        return float(self._dataservice.get_value(self._value_path)) / 10

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id

class AquariteRxValueSensorEntity(CoordinatorEntity, SensorEntity):
    """Aquarite Rx Sensor Entity."""

    _attr_icon = "mdi:gauge"
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize Hydrolyser Sensor."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._pool_id = dataservice.get_value("id") 
        self._attr_name = dataservice.get_pool_name(self._pool_id) + "_" +  name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + "-" + name

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {
                (DOMAIN, self._pool_id)
            },
            "name": self._dataservice.get_pool_name(self._pool_id),
            "manufacturer": BRAND,
            "model": MODEL,
        }
    
    @property
    def native_value(self) -> int:
        """Return value of sensor."""
        return int(self._dataservice.get_value(self._value_path))

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id
