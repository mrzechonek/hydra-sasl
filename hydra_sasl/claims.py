import pwd


def build(username: str, email_domain: str) -> dict:
    name = username
    try:
        gecos = pwd.getpwnam(username).pw_gecos.split(",")[0].strip()
        if gecos:
            name = gecos
    except KeyError:
        pass

    return {
        "sub": username,
        "preferred_username": username,
        "name": name,
        "email": f"{username}@{email_domain}",
    }
