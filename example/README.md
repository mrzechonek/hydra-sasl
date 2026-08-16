# example

Self-contained Docker Compose stack for local testing. Runs Ory Hydra, a saslauthd
container with a test user, oauth2-proxy, and the login provider.

## Prerequisites

- Docker Compose v2
- `auth.moneo.lh` and `login.moneo.lh` resolving to `127.0.0.1`

If you use dnsmasq or a wildcard `/etc/hosts` entry for `*.moneo.lh` this works
out of the box. Otherwise add to `/etc/hosts`:

```
127.0.0.1  auth.moneo.lh  login.moneo.lh
```

## Starting

```sh
make up
make register-client
```

`make up` generates secrets into `.env` (only on first run) and starts all services.
`make register-client` registers the oauth2-proxy OAuth2 client with Hydra — run
this once after the stack is up.

## Testing

Open `http://localhost:4180`. You will be redirected through the Hydra/login flow.

Test credentials: `testuser` / `testpass`

After login you land on the whoami page, which shows the request headers forwarded
by oauth2-proxy — including `X-Forwarded-User`, `X-Forwarded-Email`, and
`X-Forwarded-Preferred-Username`.

To log out: `http://localhost:4180/oauth2/sign_out`

## Tearing down

```sh
make down
```

To also wipe the Hydra database (needed if you change `URLS_SELF_ISSUER`):

```sh
docker compose down -v
```
