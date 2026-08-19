import asyncio
import struct
from dataclasses import dataclass


def _pack_field(value: str) -> bytes:
    encoded = value.encode()
    return struct.pack("!H", len(encoded)) + encoded


@dataclass(frozen=True)
class Saslauthd:
    socket_path: str
    service: str

    async def authenticate(self, username: str, password: str) -> bool:
        payload = (
            _pack_field(username)
            + _pack_field(password)
            + _pack_field(self.service)
            + _pack_field("")
        )

        async with await asyncio.open_unix_connection(self.socket_path) as (reader, writer):
            writer.write(payload)
            await writer.drain()

            length_bytes = await reader.readexactly(2)
            (length,) = struct.unpack("!H", length_bytes)
            response = await reader.readexactly(length)

        return response.startswith(b"OK")
