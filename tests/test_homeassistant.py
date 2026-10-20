"""Home Assistant API imports, UI branches and coordinator lifecycle."""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from custom_components.ksem_ws.config_flow import KsemConfigFlow
from custom_components.ksem_ws.coordinator import KsemCoordinator
from custom_components.ksem_ws.ksem import CannotConnect, InvalidAuth
from custom_components.ksem_ws.sensor import SENSORS, KsemSensor


@pytest.mark.parametrize(
    "error, expected",
    [(InvalidAuth(), "invalid_auth"), (CannotConnect(), "cannot_connect"), (None, None)],
)
async def test_config_flow(tmp_path, error, expected):
    flow = KsemConfigFlow()
    flow.hass = HomeAssistant(str(tmp_path))
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = Mock()
    flow._validate = AsyncMock(side_effect=error)
    result = await flow.async_step_user({CONF_HOST: "KSEM.EXAMPLE", CONF_PASSWORD: "synthetic"})
    if expected:
        assert result["errors"]["base"] == expected
    else:
        assert result["type"] == "create_entry"
        assert result["data"] == {CONF_HOST: "ksem.example", CONF_PASSWORD: "synthetic"}


async def test_invalid_host_does_not_connect(tmp_path):
    flow = KsemConfigFlow()
    flow.hass = HomeAssistant(str(tmp_path))
    flow._validate = AsyncMock()
    result = await flow.async_step_user({CONF_HOST: "http://bad", CONF_PASSWORD: "synthetic"})
    assert result["errors"] == {"host": "invalid_host"}
    flow._validate.assert_not_called()


async def test_reauthentication():
    flow = KsemConfigFlow()
    entry = Mock(data={"host": "ksem.example"})
    flow._get_reauth_entry = Mock(return_value=entry)
    flow._validate = AsyncMock()
    flow.async_update_reload_and_abort = Mock(return_value={"type": "abort"})
    await flow.async_step_reauth_confirm({"password": "new-synthetic"})
    flow.async_update_reload_and_abort.assert_called_once_with(
        entry, data_updates={"password": "new-synthetic"}
    )


async def test_sensors_and_auth_failure(tmp_path):
    hass = HomeAssistant(str(tmp_path))
    entry = Mock(entry_id="synthetic-id", data={"host": "ksem.example"})
    from contextlib import asynccontextmanager

    class Client:
        @asynccontextmanager
        async def connect(self):
            raise InvalidAuth
            yield

    coordinator = KsemCoordinator(hass, entry, Client(), {"current_l1": 0.0})
    sensor = KsemSensor(coordinator, entry, SENSORS[0])
    assert sensor.native_value == 0
    assert sensor.available
    assert len(SENSORS) == 6
    await coordinator.run()
    assert not sensor.available
    entry.async_start_reauth.assert_called_once_with(hass)


async def test_stop_cancels_task(tmp_path):
    coordinator = KsemCoordinator(HomeAssistant(str(tmp_path)), Mock(), Mock(), {})
    coordinator.task = asyncio.create_task(asyncio.sleep(1000))
    task = coordinator.task
    await coordinator.stop()
    assert task.cancelled()
    assert coordinator.task is None


async def test_reconnect_clears_availability_then_recovers(tmp_path, monkeypatch):
    from contextlib import asynccontextmanager

    import custom_components.ksem_ws.coordinator as module

    hass = HomeAssistant(str(tmp_path))
    entry = Mock()

    class Client:
        connections = 0

        @asynccontextmanager
        async def connect(self):
            self.connections += 1
            yield object()

        async def receive(self, socket):
            if self.connections == 1:
                raise CannotConnect
            return {"current_l1": 2.0}

    client = Client()
    coordinator = KsemCoordinator(hass, entry, client, {"current_l1": 1.0})
    waits = []

    async def retry(delay):
        assert not coordinator.last_update_success
        waits.append(delay)

    monkeypatch.setattr(module.asyncio, "sleep", retry)
    original_update = coordinator.async_set_updated_data

    def received(data):
        original_update(data)
        raise asyncio.CancelledError

    coordinator.async_set_updated_data = received
    with pytest.raises(asyncio.CancelledError):
        await coordinator.run()
    assert waits == [5]
    assert client.connections == 2
    assert coordinator.last_update_success
    assert coordinator.data["current_l1"] == 2.0


async def test_setup_and_unload_mapping():
    from unittest.mock import patch

    from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

    import custom_components.ksem_ws as integration

    hass = Mock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    entry = Mock(data={"host": "ksem.example", "password": "synthetic"})
    for error, expected in (
        (InvalidAuth(), ConfigEntryAuthFailed),
        (CannotConnect(), ConfigEntryNotReady),
    ):
        with (
            patch.object(integration, "async_get_clientsession"),
            patch.object(integration, "KsemClient") as cls,
        ):
            cls.return_value.validate = AsyncMock(side_effect=error)
            with pytest.raises(expected):
                await integration.async_setup_entry(hass, entry)
    entry.runtime_data.stop = AsyncMock()
    assert await integration.async_unload_entry(hass, entry)
    entry.runtime_data.stop.assert_awaited_once()
