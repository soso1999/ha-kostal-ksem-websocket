"""KOSTAL KSEM WebSocket integration."""

from homeassistant.const import CONF_HOST, CONF_PASSWORD, Platform
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .coordinator import KsemCoordinator
from .ksem import CannotConnect, InvalidAuth, KsemClient

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass, entry):
    client = KsemClient(
        async_get_clientsession(hass), entry.data[CONF_HOST], entry.data[CONF_PASSWORD]
    )
    try:
        initial = await client.validate()
    except InvalidAuth:
        raise ConfigEntryAuthFailed("KSEM credentials rejected") from None
    except CannotConnect:
        raise ConfigEntryNotReady("KSEM stream unavailable") from None
    coordinator = KsemCoordinator(hass, entry, client, initial)
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    coordinator.start()
    return True


async def async_unload_entry(hass, entry):
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        await entry.runtime_data.stop()
        return True
    return False
