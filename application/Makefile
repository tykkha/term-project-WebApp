PY=python3

.PHONY: setup dev api-dev web-dev build-web build-api migrate test lint deploy server-api server-web

setup:
	cd api/app && $(PY) -m venv .venv && . .venv/bin/activate && pip install -U pip wheel && pip install -r requirements.txt || true
	cd web && npm ci

api-dev:
	cd api/app && . .venv/bin/activate && uvicorn main:app --reload --port 8001

web-dev:
	cd web && npm run dev -- --open

dev:
	make api-dev & make web-dev

build-web:
	cd web && npm run build && zip -r build.zip build 

build-api:
	cd api/app && . .venv/bin/activate && pip install -r requirements.txt

server-api:
	git pull origin main
	rm -rf /var/www/api/app && cp -r api/app /var/www/api/app && cd /var/www/api/app && $(PY) -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	sudo systemctl restart api.service

server-web:
	git pull origin main
	rm -rf /var/www/svelte/* && cd ../.. && unzip build.zip && cd build && cp -r * /var/www/svelte/
	sudo systemctl restart svelte.service

server-db:
	sudo systemctl stop api.service && cd api/app/db && mysql -u guides -pgatorguides < Schema.sql && mysql -u guides -pgatorguides < Inserts.sql && sudo systemctl start api