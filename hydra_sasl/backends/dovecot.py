import asyncio
import base64
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Dovecot:
    socket_path: str
    service: str

    def __post_init__(self) -> None:
        self._check_socket_name(self.socket_path)

    @staticmethod
    def _check_socket_name(socket_path: str) -> None:
        # Dovecot types a socket by the '-<suffix>' - these speak a
        # different protocol
        suffix = os.path.basename(socket_path).rpartition("-")[2]
        if suffix in {"master", "userdb", "token"}:
            raise ValueError(
                f"auth socket {socket_path!r} names a {suffix!r} socket, which "
                f"speaks a different protocol (not PLAIN auth); "
                f"use a login socket or plain auth listener such as auth-client"
            )

    async def authenticate(self, username: str, password: str) -> bool:
        # PLAIN initial response: authzid \0 authcid \0 password.
        resp = base64.b64encode(
            b"\0" + username.encode() + b"\0" + password.encode()
        ).decode()

        async with await asyncio.open_unix_connection(self.socket_path) as (
            reader,
            writer,
        ):
            # Dovecot 2.3 sends its handshake on connect, 2.4 only after ours,
            # so send ours unprompted. CPID is mandatory but ignored on a
            # non-login socket, hence no need to keep it unique.
            # Note: CPID is hardcoded as it is ignored by Dovecot for non-login sockets.
            writer.write(f"VERSION\t1\t2\nCPID\t{os.getpid()}\n".encode())

            # Read handshake lines until "DONE"
            while True:
                line = await reader.readline()
                if not line:
                    raise ConnectionError(
                        "dovecot closed the connection during handshake"
                    )
                if line.rstrip(b"\r\n") == b"DONE":
                    break

            # service= rather than protocol=: the only form 2.3 accepts and
            # still honoured by 2.4. secured (bare, rather than 2.4's
            # secured=tls) marks the request as coming over a trusted channel,
            # without which the auth process refuses PLAIN under
            # disable_plaintext_auth=yes. The username travels inside resp=, so
            # no field on this line is user-controlled and needs tab-escaping.
            writer.write(
                f"AUTH\t1\tPLAIN\tservice={self.service}\tsecured\tresp={resp}\n".encode()
            )
            reply = await reader.readline()
            return reply.startswith(b"OK\t")
