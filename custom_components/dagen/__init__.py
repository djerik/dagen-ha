"""The Dagen integration."""
from homeassistant import config_entries, core
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .coordinator import DagenDataCoordinator
from .dagen import Dagen

PLATFORMS = [BINARY_SENSOR_DOMAIN, LIGHT_DOMAIN, SENSOR_DOMAIN ]

async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up the Dagen component."""
    api : Dagen = await Dagen.create( async_get_clientsession(hass), entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    coordinator = DagenDataCoordinator(hass, api, entry.data["pool_id"])

    await coordinator.async_config_entry_first_refresh()
    hass.async_add_executor_job( api.subscribe, entry.data["pool_id"], coordinator.set_updated_data)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await coordinator.async_config_entry_first_refresh()

    return True


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Async setup component."""
    return True
