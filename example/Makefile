.PHONY: up down secrets register-client

.env:
	cp .env.example .env
	sed -i "s|HYDRA_SYSTEM_SECRET=.*|HYDRA_SYSTEM_SECRET=$(shell openssl rand -hex 32)|" .env
	sed -i "s|HYDRA_COOKIE_SECRET=.*|HYDRA_COOKIE_SECRET=$(shell openssl rand -hex 32)|" .env
	sed -i "s|OAUTH2_PROXY_CLIENT_SECRET=.*|OAUTH2_PROXY_CLIENT_SECRET=$(shell openssl rand -hex 16)|" .env
	sed -i "s|OAUTH2_PROXY_COOKIE_SECRET=.*|OAUTH2_PROXY_COOKIE_SECRET=$(shell openssl rand -hex 16)|" .env

secrets: .env

up: secrets
	docker compose up --build -d

register-client:
	@. ./.env && curl -sf -X POST http://localhost:4445/admin/clients \
	  -H "Content-Type: application/json" \
	  -d "{\"client_id\":\"$$OAUTH2_PROXY_CLIENT_ID\",\"client_secret\":\"$$OAUTH2_PROXY_CLIENT_SECRET\",\"grant_types\":[\"authorization_code\"],\"response_types\":[\"code\"],\"scope\":\"openid profile email\",\"redirect_uris\":[\"http://localhost:4180/oauth2/callback\"],\"token_endpoint_auth_method\":\"client_secret_basic\"}"

down:
	docker compose down
