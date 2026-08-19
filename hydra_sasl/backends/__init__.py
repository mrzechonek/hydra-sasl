from typing import Callable, Protocol

from hydra_sasl.backends.dovecot import Dovecot
from hydra_sasl.backends.saslauthd import Saslauthd
from hydra_sasl.settings import Settings


class Backend(Protocol):
    async def authenticate(self, username: str, password: str) -> bool: ...


def create(settings: Settings) -> Backend:
    # Annotated because mypy otherwise joins the two constructors to
    # Callable[[str, str], object].
    backends: dict[str, Callable[[str, str], Backend]] = {
        "saslauthd": Saslauthd,
        "dovecot": Dovecot,
    }
    try:
        backend = backends[settings.auth_backend]
    except KeyError:
        raise ValueError(
            f"unknown auth backend {settings.auth_backend!r}, "
            f"expected one of {', '.join(sorted(backends))}"
        ) from None
    return backend(settings.auth_socket, settings.auth_service)
