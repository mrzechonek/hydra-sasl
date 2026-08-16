# hydra-sasl

Login provider for [Ory Hydra](https://github.com/ory/hydra) that authenticates
users via [saslauthd](https://www.cyrusimap.org/sasl/sasl/components.html#saslauthd),
backed by Linux system accounts.

Self-hosted services that support OIDC (Immich, Jellyfin, Nextcloud, …) can use this
to authenticate against the Linux users already on your server, with no separate user
database.

## How it fits in

```
Client (Immich, Jellyfin, ...)
  │
  ▼
Ory Hydra  (OAuth2/OIDC, ports 4444/4445)
  │  login/consent challenge redirect
  ▼
hydra-sasl  (FastAPI, port 8000)
  │  username + password
  ▼
saslauthd  (unix socket)
  │
  ▼
/etc/shadow
```

Hydra handles the OAuth2/OIDC protocol and never sees credentials. It redirects the
browser to hydra-sasl with a signed challenge. hydra-sasl shows a login form,
authenticates via saslauthd, then accepts or rejects the challenge through Hydra's
admin API. Consent is granted automatically for all requested scopes.

## Requirements

- Ory Hydra v2.2+ with its admin API reachable from this service
- `saslauthd` running and its socket accessible to this process (see below)

## Configuration

All configuration is via environment variables.

| Variable | Required | Default | Description |
|---|---|---|---|
| `HYDRA_ADMIN_URL` | yes | — | Hydra admin API base URL, e.g. `http://hydra:4445` |
| `EMAIL_DOMAIN` | yes | — | Domain for derived email claims, e.g. `example.com` |
| `SASLAUTHD_SOCKET` | no | `/var/run/saslauthd/mux` | Path to the saslauthd socket |
| `SASLAUTHD_SERVICE` | no | `login` | PAM service name passed to saslauthd |
| `LOGIN_TITLE` | yes | — | Site name shown on the login page |
| `LOGIN_BG_URL` | no | — | Background image URL for the login page |

## Running

```sh
pip install hydra-sasl
uvicorn hydra_sasl.main:app --host 0.0.0.0 --port 8000
```

Or with Docker:

```sh
docker build -t hydra-sasl .
docker run -p 8000:8000 \
  -e HYDRA_ADMIN_URL=http://hydra:4445 \
  -e EMAIL_DOMAIN=example.com \
  -v /var/run/saslauthd:/var/run/saslauthd \
  hydra-sasl
```

Point Hydra at this service:

```
URLS_LOGIN=http://hydra-sasl:8000/login
URLS_CONSENT=http://hydra-sasl:8000/consent
```

## saslauthd socket access

The process must be able to connect to the saslauthd socket. The socket is owned by
the `sasl` group (`srwxrwx---`), so the process user needs to be in that group.

When running in a container with the socket mounted from the host, the `sasl` GID
inside the container must match the host's `sasl` GID.

## OIDC claims

| Claim | Source |
|---|---|
| `sub` | username |
| `preferred_username` | username |
| `name` | GECOS field from `/etc/passwd` (first comma-separated token), falls back to username |
| `email` | `{username}@{EMAIL_DOMAIN}` |

## Local development

See [example/](example/) for a self-contained Docker Compose stack that wires up
Hydra, a test saslauthd container, and an oauth2-proxy demo.
