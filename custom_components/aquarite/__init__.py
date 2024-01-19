"""The Aquarite integration."""
from homeassistant import config_entries, core
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .coordinator import AquariteDataCoordinator
from .aquarite import Aquarite

PLATFORMS = [BINARY_SENSOR_DOMAIN, LIGHT_DOMAIN, SWITCH_DOMAIN, SENSOR_DOMAIN]

async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up the Hayward component."""
    api : Aquarite = await Aquarite.create( async_get_clientsession(hass), entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    coordinator = AquariteDataCoordinator(hass, api)

    coordinator.data = await hass.async_add_executor_job(api.get_pool,entry.data["pool_id"])

    hass.async_add_executor_job( api.subscribe, entry.data["pool_id"], coordinator.set_updated_data)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Async setup component."""
    return True
