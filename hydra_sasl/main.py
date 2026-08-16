from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from hydra_sasl import auth, claims, hydra
from hydra_sasl.settings import settings

app = FastAPI(title="hydra-sasl")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/login")
async def login_get(request: Request, login_challenge: str):
    login_req = await hydra.get_login_request(settings.hydra_admin_url, login_challenge)

    if login_req.get("skip"):
        redirect_to = await hydra.accept_login(settings.hydra_admin_url, login_challenge, login_req["subject"])
        return RedirectResponse(redirect_to)

    return templates.TemplateResponse(
        request,
        "login.html",
        {"challenge": login_challenge, "error": None, "title": settings.login_title, "bg_url": settings.login_bg_url},
    )


@app.post("/login")
async def login_post(
    request: Request,
    challenge: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
):
    ok = await auth.authenticate(settings.saslauthd_socket, username, password, settings.saslauthd_service)

    if not ok:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"challenge": challenge, "error": "Invalid username or password", "title": settings.login_title, "bg_url": settings.login_bg_url},
            status_code=401,
        )

    redirect_to = await hydra.accept_login(settings.hydra_admin_url, challenge, username)
    return RedirectResponse(redirect_to, status_code=303)


@app.get("/consent")
async def consent_get(consent_challenge: str):
    consent_req = await hydra.get_consent_request(settings.hydra_admin_url, consent_challenge)
    subject = consent_req["subject"]
    scopes = consent_req.get("requested_scope", [])

    redirect_to = await hydra.accept_consent(
        settings.hydra_admin_url,
        consent_challenge,
        scopes,
        claims.build(subject, settings.email_domain),
    )
    return RedirectResponse(redirect_to)
