PY=python3

.PHONY: setup dev api-dev web-dev build-web build-api migrate test lint deploy

setup:
	cd api/app && $(PY) -m venv .venv && . .venv/bin/activate && pip install -U pip wheel && pip install -r requirements.txt || true
	cd web && npm ci

api-dev:
	cd api/app && . .venv/bin/activate && uvicorn main:app --reload --port 8001

web-dev:
	cd web && npm run dev -- --open

build-web:
	cd web && npm run build

deploy-web:
	cd web && npm run build && mv build /var/www/sveltekit && sudo systemctl reload nginx

build-api:
	cd api/app && . .venv/bin/activate && pip install -r requirements.txt

deploy:
	bash infra/scripts/deploy.sh