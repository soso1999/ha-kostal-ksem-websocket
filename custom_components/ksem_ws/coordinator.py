"""Push coordinator with reconnect, stale detection and reauthentication."""

import asyncio
import logging
from contextlib import suppress

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .ksem import CannotConnect, InvalidAuth

_LOGGER = logging.getLogger(__name__)


class KsemCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, client, initial):
        super().__init__(hass, _LOGGER, name=DOMAIN, config_entry=entry)
        self.entry = entry
        self.client = client
        self.task = None
        self.async_set_updated_data(initial)

    def start(self):
        self.task = self.entry.async_create_background_task(self.hass, self.run(), "KSEM WebSocket")

    async def stop(self):
        if self.task:
            self.task.cancel()
            with suppress(asyncio.CancelledError):
                await self.task
            self.task = None

    async def run(self):
        delay = 5
        while True:
            try:
                async with self.client.connect() as socket:
                    while True:
                        data = await self.client.receive(socket)
                        self.async_set_updated_data(data)
                        delay = 5
            except InvalidAuth:
                self.async_set_update_error(CannotConnect("Authentication required"))
                self.entry.async_start_reauth(self.hass)
                return
            except (CannotConnect, TimeoutError):
                self.async_set_update_error(CannotConnect("KSEM stream unavailable"))
            await asyncio.sleep(delay)
            delay = min(delay * 2, 60)
