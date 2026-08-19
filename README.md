# hydra-sasl

Login provider for [Ory Hydra](https://github.com/ory/hydra) that authenticates
users against an existing authentication daemon — either
[saslauthd](https://www.cyrusimap.org/sasl/sasl/components.html#saslauthd) or
[Dovecot](https://www.dovecot.org/) — typically backed by Linux system accounts.

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
saslauthd or Dovecot auth  (unix socket)
  │
  ▼
/etc/shadow
```

Hydra handles the OAuth2/OIDC protocol and never sees credentials. It redirects the
browser to hydra-sasl with a signed challenge. hydra-sasl shows a login form,
authenticates against the configured backend, then accepts or rejects the challenge
through Hydra's admin API. Consent is granted automatically for all requested scopes.

## Requirements

- Ory Hydra v2.2+ with its admin API reachable from this service
- one authentication backend, with its socket accessible to this process (see below):
  - `saslauthd` (default), or
  - `dovecot`, talking the Dovecot auth protocol with the PLAIN mechanism

## Configuration

All configuration is via environment variables.

| Variable | Required | Default | Description |
|---|---|---|---|
| `HYDRA_ADMIN_URL` | yes | — | Hydra admin API base URL, e.g. `http://hydra:4445` |
| `EMAIL_DOMAIN` | yes | — | Domain for derived email claims, e.g. `example.com` |
| `AUTH_BACKEND` | no | `saslauthd` | Authentication backend: `saslauthd` or `dovecot` |
| `AUTH_SOCKET` | no | `/var/run/saslauthd/mux` | Path to the backend socket |
| `AUTH_SERVICE` | no | `login` | Service name passed to the backend (a PAM service name for saslauthd) |
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

## Backend socket access

The process must be able to connect to the backend socket. When running in a
container with the socket mounted from the host, the owning GID inside the container
must match the host's.

### saslauthd

The socket is owned by the `sasl` group (`srwxrwx---`), so the process user needs to
be in that group.

### Dovecot

The Dovecot backend expects a **login socket** by default (e.g., `/var/run/dovecot/login`).
This is the standard socket for authentication and requires no additional configuration.

If you need to use a non-standard socket (e.g., `auth-client`), add a listener in Dovecot:

```
service auth {
  unix_listener auth-client {
    mode = 0660
    group = <group of this process>
  }
}
```

The listener name matters. Dovecot derives the socket type from the suffix after the
last `-`, and the names `master`, `userdb`, and `token` select sockets speaking a
different protocol. These are **not supported** by this backend. The socket must also
be accessible to the process.

`PLAIN` must be among the enabled `auth_mechanisms` (it is by default). Dovecot's
`disable_plaintext_auth` does not apply: it is enforced by the login services, not by
the auth process.

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
