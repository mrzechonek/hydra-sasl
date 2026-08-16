import asyncio
import struct


def _pack_field(value: str) -> bytes:
    encoded = value.encode()
    return struct.pack("!H", len(encoded)) + encoded


async def authenticate(
    socket_path: str, username: str, password: str, service: str = "login"
) -> bool:
    payload = (
        _pack_field(username)
        + _pack_field(password)
        + _pack_field(service)
        + _pack_field("")
    )

    reader, writer = await asyncio.open_unix_connection(socket_path)
    try:
        writer.write(payload)
        await writer.drain()

        length_bytes = await reader.readexactly(2)
        (length,) = struct.unpack("!H", length_bytes)
        response = await reader.readexactly(length)
    finally:
        writer.close()
        await writer.wait_closed()

    return response.startswith(b"OK")
