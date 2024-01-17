"""Config Flow."""
from typing import Any, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .aquarite import Aquarite, UnauthorizedException

AUTH_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): cv.string, vol.Required(CONF_PASSWORD): cv.string}
)

class AquariteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Aquarite config flow."""

    data: Optional[dict[str, Any]]

    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None):
        """First step"."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self.data = user_input

            # Return the form of the next step.
            return await self.async_step_pool()

        return self.async_show_form(
            step_id="user", data_schema=AUTH_SCHEMA, errors=errors
        )

    async def async_step_pool(self, user_input: Optional[dict[str, Any]] = None):
        """Second step in config flow to choose the pool."""
        errors = {}
        if user_input is not None:
            self.data["pool_id"] = user_input["pool_id"]
            return await self.async_create_entry(title=self.data['pools'][ self.data["pool_id"] ], data=self.data)

        try:
            api : Aquarite = await Aquarite.create( async_get_clientsession(self.hass), self.data[CONF_USERNAME], self.data[CONF_PASSWORD])
        except UnauthorizedException:
            errors["base"] = "auth_error"
            return self.async_show_form(
                step_id="user", data_schema=AUTH_SCHEMA, errors=errors
            )

        self.data['pools'] = await api.get_pools()

        POOL_SCHEMA = vol.Schema({vol.Optional("pool_id"): vol.In(self.data['pools'])})

        return self.async_show_form(
            step_id="pool", data_schema=POOL_SCHEMA, errors=errors
        )

    async def async_step_reauth(self, user_input=None):
        """Reauth user."""
        return await self.async_step_user()

    async def async_create_entry(self, title: str, data: dict) -> dict:
        """Create an oauth config entry or update existing entry for reauth."""
        existing_entry = ""
        if existing_entry:
            self.hass.config_entries.async_update_entry(existing_entry, data=data)
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="reauth_successful")
        return super().async_create_entry(title=title, data=data)
