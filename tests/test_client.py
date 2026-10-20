"""Exercise actual aiohttp authentication and WebSocket traffic on loopback."""

import asyncio

import pytest
from aiohttp import ClientSession, web
from aiohttp.test_utils import TestServer
from test_protocol import frame

from custom_components.ksem_ws.const import CURRENT, WS_PATH
from custom_components.ksem_ws.ksem import CannotConnect, InvalidAuth, KsemClient, normalize_host


@pytest.mark.parametrize(
    "host, expected",
    [(" KSEM.EXAMPLE. ", "ksem.example"), ("[::1]", "[::1]"), ("127.0.0.1", "127.0.0.1")],
)
def test_host(host, expected):
    assert normalize_host(host) == expected


@pytest.mark.parametrize("host", ["http://example.com", "host:80", "x/a", "x@x", "", "-x", "x?y"])
def test_invalid_host(host):
    with pytest.raises(ValueError):
        normalize_host(host)


@pytest.mark.parametrize(
    "mode",
    [
        "ok",
        "bad_password",
        "invalid_grant",
        "server_error",
        "no_token",
        "closed",
        "malformed",
        "wrong_stream",
        "redirect",
    ],
)
async def test_transport(mode):
    calls = []

    async def login(request):
        calls.append("login")
        form = await request.post()
        assert form["username"] == "admin"
        assert form["password"] == "test-only-password"
        assert form["client_id"] == "emos"
        if mode == "bad_password":
            return web.Response(status=401)
        if mode == "invalid_grant":
            return web.json_response({"error": "invalid_grant"}, status=400)
        if mode == "server_error":
            return web.Response(status=500)
        if mode == "redirect":
            return web.Response(status=302, headers={"Location": "/unexpected"})
        return web.json_response({} if mode == "no_token" else {"access_token": "synthetic-token"})

    async def websocket(request):
        socket = web.WebSocketResponse()
        await socket.prepare(request)
        assert await socket.receive_str() == "Bearer synthetic-token"
        calls.append("bearer")
        if mode != "closed":
            payload = (
                b"\x0a\xff"
                if mode == "malformed"
                else frame(
                    {CURRENT[0]: 1500}, b"other" if mode == "wrong_stream" else b"smart-meter"
                )
            )
            await socket.send_bytes(payload)
        await socket.close()
        return socket

    app = web.Application()
    app.router.add_post("/api/web-login/token", login)
    app.router.add_get(WS_PATH, websocket)
    async with TestServer(app) as server, ClientSession() as session:
        client = KsemClient(session, "localhost", "test-only-password")
        client.host = server.make_url("/").host + ":" + str(server.port)
        if mode == "ok":
            assert (await client.validate())["current_l1"] == 1.5
            await client.validate()
            assert calls == ["login", "bearer", "login", "bearer"]
        else:
            with pytest.raises(
                InvalidAuth if mode in ("bad_password", "invalid_grant") else CannotConnect
            ):
                await client.validate()


async def test_stale_socket_timeout(monkeypatch):
    import custom_components.ksem_ws.ksem as module

    original = asyncio.timeout
    monkeypatch.setattr(module.asyncio, "timeout", lambda seconds: original(0.01))

    class Silent:
        async def receive(self):
            await asyncio.Future()

    with pytest.raises(TimeoutError):
        await KsemClient(None, "localhost", "test-only").receive(Silent())
