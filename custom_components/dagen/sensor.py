"""Dagen value sensors."""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfElectricPotential, UnitOfTemperature, CONCENTRATION_PARTS_PER_MILLION
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
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
        DagenTemperatureSensorEntity(
            hass,
            dataservice,
            "Temperature",
            "main.temperature",
        ),
    )

    if dataservice.get_value( PATH_HASCD ):
        entities.append(
            DagenValueSensorEntity(
                hass,
                dataservice,
                "CD",
                "modules.cd.current",
            ),
        )

    if dataservice.get_value( PATH_HASCL ):
        entities.append(
            DagenValueSensorEntity(
                hass,
                dataservice,
                "Cl",
                "modules.cl.current",
                SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS,
                CONCENTRATION_PARTS_PER_MILLION,
                "mdi:gauge"
            ),
        )

    if dataservice.get_value( PATH_HASPH ):
        entities.append(
            DagenValueSensorEntity(
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
            DagenRxValueSensorEntity(
                hass,
                dataservice,
                "Rx",
                "modules.rx.current",
            ),
        )

    if dataservice.get_value( PATH_HASUV ):
        entities.append(
            DagenValueSensorEntity(
                hass,
                dataservice,
                "UV",
                "modules.uv.current",
            ),
        )

    if dataservice.get_value( PATH_HASHIDRO ):
        entities.append(
            DagenHydrolyserSensorEntity(
                hass,
                dataservice,
                "Electrolysis" if dataservice.get_value( "hidro.is_electrolysis") else "Hidrolysis",
                "hidro.current",
            ),
        )

    async_add_entities(entities)

class DagenTemperatureSensorEntity(CoordinatorEntity, SensorEntity):
    """Dagen Temperature Sensor Entity."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize Temperature Sensor."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._attr_name = name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + "-" + name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = float(self._dataservice.get_value(self._value_path))
        self.async_write_ha_state()

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id

class DagenValueSensorEntity(CoordinatorEntity, SensorEntity):
    """Dagen Value Sensor Entity."""

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path, device_class:SensorDeviceClass = None, native_unit_of_measurement:str = None, icon:str = None) -> None:
        """Initialize Value Sensor such as pH."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._attr_name = name
        self._value_path = value_path
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = native_unit_of_measurement
        self._attr_icon = icon
        self._unique_id = dataservice.get_value("id") + "-" + name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = float(self._dataservice.get_value(self._value_path)) / 100
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id

class DagenHydrolyserSensorEntity(CoordinatorEntity, SensorEntity):
    """Dagen Hydrolyser Sensor Entity."""

    _attr_icon = "mdi:gauge"
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize Hydrolyser Sensor."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._attr_name = name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + "-" + name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = float(self._dataservice.get_value(self._value_path)) / 10
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id

class DagenRxValueSensorEntity(CoordinatorEntity, SensorEntity):
    """Dagen Rx Sensor Entity."""

    _attr_icon = "mdi:gauge"
    _attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize Hydrolyser Sensor."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._attr_name = name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + "-" + name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = int(self._dataservice.get_value(self._value_path))
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id
