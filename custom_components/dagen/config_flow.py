"""Config Flow."""
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .dagen import Dagen, UnauthorizedException

AUTH_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): cv.string, vol.Required(CONF_PASSWORD): cv.string}
)

class DagenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Da-gen config flow."""

    data: dict[str, Any] | None

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """First step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self.data = user_input

            # Return the form of the next step.
            return await self.async_step_pool()

        return self.async_show_form(
            step_id="user", data_schema=AUTH_SCHEMA, errors=errors
        )

    async def async_step_pool(self, user_input: dict[str, Any] | None = None):
        """Second step in config flow to choose the pool."""
        errors = {}
        if user_input is not None:
            self.data["pool_id"] = user_input["pool_id"]
            return self.async_create_entry(title=self.data['pools'][self.data["pool_id"]], data=self.data)

        try:
            api: Dagen = await Dagen.create(async_get_clientsession(self.hass), self.data[CONF_USERNAME], self.data[CONF_PASSWORD])
        except UnauthorizedException:
            errors["base"] = "auth_error"
            return self.async_show_form(
                step_id="user", data_schema=AUTH_SCHEMA, errors=errors
            )

        self.data['pools'] = await self.hass.async_add_executor_job(api.get_pools)

        POOL_SCHEMA = vol.Schema({vol.Required("pool_id"): vol.In(self.data['pools'])})

        return self.async_show_form(
            step_id="pool", data_schema=POOL_SCHEMA, errors=errors
        )

    async def async_step_reauth(self, user_input=None):
        """Reauth user."""
        return await self.async_step_user()
