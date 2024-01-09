"""Dagen value sensors."""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


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

    if dataservice.get_value( "main.hasCD"):
        entities.append(
            DagenValueSensorEntity(
                hass,
                dataservice,
                "CD",
                "modules.cl.current",
            ),
        )

    if dataservice.get_value( "main.hasCL"):
        entities.append(
            DagenValueSensorEntity(
                hass,
                dataservice,
                "Cl",
                "modules.cl.current",
            ),
        )

    if dataservice.get_value( "main.hasPH"):
        entities.append(
            DagenValueSensorEntity(
                hass,
                dataservice,
                "pH",
                "modules.ph.current",
            ),
        )

    if dataservice.get_value( "main.hasRX"):
        entities.append(
            DagenValueSensorEntity(
                hass,
                dataservice,
                "RX",
                "modules.rx.current",
            ),
        )

    if dataservice.get_value( "main.hasUV"):
        entities.append(
            DagenValueSensorEntity(
                hass,
                dataservice,
                "UV",
                "modules.rx.current",
            ),
        )

    if dataservice.get_value( "main.hasHidro"):
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

class DagenValueSensorEntity(CoordinatorEntity, SensorEntity):
    """Dagen Value Sensor Entity."""

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize Value Sensor such as pH."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._attr_name = name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + "-" + name

    @property
    def native_value(self):
        """Return value of sensor."""
        return float(self._dataservice.get_value(self._value_path)) / 100

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id

class DagenHydrolyserSensorEntity(CoordinatorEntity, SensorEntity):
    """Dagen Hydrolyser Sensor Entity."""

    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, hass : HomeAssistant, dataservice, name, value_path) -> None:
        """Initialize Hydrolyser Sensor."""
        super().__init__(dataservice)
        self._dataservice = dataservice
        self._attr_name = name
        self._value_path = value_path
        self._unique_id = dataservice.get_value("id") + "-" + name

    @property
    def native_value(self) -> float:
        """Return value of sensor."""
        return float(self._dataservice.get_value(self._value_path)) / 10

    @property
    def unique_id(self):
        """The unique id of the sensor."""
        return self._unique_id
