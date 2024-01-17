class AquariteDataService:
    """Get and update the latest data."""

    def __init__(self, hass, api, pool_id):
        """Initialize the data object."""
        self.api = api
        self.pool_id = pool_id

        self.hass = hass
        self.coordinator = None

    @callback
    def async_setup(self):
        """Coordinator creation."""
        self.coordinator = DataUpdateCoordinator(
            self.hass,
            _LOGGER,
            name="AquariteDataService",
            update_method=self.async_update_data,
            update_interval=self.update_interval,
        )

    @property
    def update_interval(self):
        return UPDATE_DELAY

    async def async_update_data(self):
        try:
            self.roomdata = await self.hass.async_add_executor_job(
                self.api.get_rooms, self.location_id
            )
        except KeyError as ex:
            raise UpdateFailed("Missing overview data, skipping update") from ex

    def get_value(self, value_path):
        return snapshot.get(value_path)
