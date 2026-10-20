"""HTTP authentication and read-only local WebSocket transport."""

from __future__ import annotations

import asyncio
import ipaddress
import re
from contextlib import asynccontextmanager

import aiohttp

from .const import WS_PATH
from .protocol import decode_ksem_message, measurements


class CannotConnect(Exception):
    """Connection or protocol could not be validated."""


class InvalidAuth(Exception):
    """KSEM rejected credentials."""


def normalize_host(host):
    host = host.strip().lower().rstrip(".")
    try:
        address = ipaddress.ip_address(host.strip("[]"))
        return f"[{address}]" if address.version == 6 else str(address)
    except ValueError:
        if len(host) > 253 or not all(
            re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", part) for part in host.split(".")
        ):
            raise ValueError(
                "Enter an IP address or hostname without scheme, port or path"
            ) from None
        return host


class KsemClient:
    def __init__(self, session, host, password):
        self.session = session
        self.host = normalize_host(host)
        self.password = password

    async def authenticate(self):
        try:
            async with self.session.post(
                f"http://{self.host}/api/web-login/token",
                data={
                    "grant_type": "password",
                    "client_id": "emos",
                    "client_secret": "56951025",
                    "username": "admin",
                    "password": self.password,
                },
                allow_redirects=False,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status in (401, 403):
                    raise InvalidAuth from None
                if response.status != 200:
                    if response.status == 400:
                        try:
                            payload = await response.json(content_type=None)
                        except ValueError:
                            raise CannotConnect from None
                        if payload.get("error") == "invalid_grant":
                            raise InvalidAuth from None
                    raise CannotConnect from None
                payload = await response.json(content_type=None)
                token = payload.get("access_token")
                if not isinstance(token, str) or not token:
                    raise CannotConnect
                return token
        except (aiohttp.ClientError, TimeoutError, ValueError, AttributeError):
            raise CannotConnect from None

    @asynccontextmanager
    async def connect(self):
        token = await self.authenticate()
        try:
            async with asyncio.timeout(15):
                socket = await self.session.ws_connect(
                    f"ws://{self.host}{WS_PATH}",
                    heartbeat=30,
                    max_msg_size=1024 * 1024,
                )
            try:
                await socket.send_str(f"Bearer {token}")
                yield socket
            finally:
                await socket.close()
        except aiohttp.WSServerHandshakeError as err:
            if err.status in (401, 403):
                raise InvalidAuth from None
            raise CannotConnect from None
        except (aiohttp.ClientError, TimeoutError):
            raise CannotConnect from None

    async def receive(self, socket):
        # A silent socket must not leave old readings available indefinitely.
        async with asyncio.timeout(30):
            while True:
                message = await socket.receive()
                if message.type == aiohttp.WSMsgType.BINARY:
                    try:
                        data = measurements(decode_ksem_message(message.data))
                    except ValueError:
                        raise CannotConnect from None
                    if any(value is not None for value in data.values()):
                        return data
                elif message.type in (
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSING,
                    aiohttp.WSMsgType.ERROR,
                ):
                    raise CannotConnect

    async def validate(self):
        try:
            async with asyncio.timeout(20):
                async with self.connect() as socket:
                    return await self.receive(socket)
        except TimeoutError:
            raise CannotConnect from None
