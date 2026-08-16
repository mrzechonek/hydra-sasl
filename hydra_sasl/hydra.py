import httpx


async def _get(admin_url: str, path: str, challenge_param: str, challenge: str) -> dict:  # type: ignore[return]
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{admin_url}{path}",
            params={challenge_param: challenge},
        )
        r.raise_for_status()
        return r.json()


async def _put(admin_url: str, path: str, challenge_param: str, challenge: str, body: dict) -> str:  # type: ignore[return]
    async with httpx.AsyncClient() as client:
        r = await client.put(
            f"{admin_url}{path}",
            params={challenge_param: challenge},
            json=body,
        )
        r.raise_for_status()
        return r.json()["redirect_to"]


async def get_login_request(admin_url: str, challenge: str) -> dict:
    return await _get(admin_url, "/admin/oauth2/auth/requests/login", "login_challenge", challenge)


async def accept_login(admin_url: str, challenge: str, subject: str) -> str:
    return await _put(admin_url, "/admin/oauth2/auth/requests/login/accept", "login_challenge", challenge, {"subject": subject})


async def reject_login(admin_url: str, challenge: str) -> str:
    return await _put(
        admin_url,
        "/admin/oauth2/auth/requests/login/reject",
        "login_challenge",
        challenge,
        {"error": "access_denied", "error_description": "Invalid credentials"},
    )


async def get_consent_request(admin_url: str, challenge: str) -> dict:
    return await _get(admin_url, "/admin/oauth2/auth/requests/consent", "consent_challenge", challenge)


async def accept_consent(admin_url: str, challenge: str, scopes: list[str], id_token_claims: dict) -> str:
    return await _put(
        admin_url,
        "/admin/oauth2/auth/requests/consent/accept",
        "consent_challenge",
        challenge,
        {
            "grant_scope": scopes,
            "session": {"id_token": id_token_claims},
        },
    )
