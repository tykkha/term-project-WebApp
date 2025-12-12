PY=python3
VENV=.venv
VENV_BIN=$(VENV)/bin

.PHONY: setup dev api-dev web-dev build-web build-api migrate test lint deploy server-api server-web

setup:
	$(PY) -m venv $(VENV) && . $(VENV_BIN)/activate && pip install -U pip wheel && pip install -r api/app/requirements.txt || true
	cd web && npm ci

api-dev:
	. $(VENV_BIN)/activate && cd api/app && uvicorn main:app --reload --port 8001

web-dev:
	cd web && npm run dev -- --open

dev:
	make api-dev & make web-dev

build-web:
	cd web && npm run build && zip -r build.zip build 

build-api:
	. $(VENV_BIN)/activate && pip install -r api/app/requirements.txt

server-api:
	git pull origin main
	sudo systemctl stop api.service
	sudo systemctl stop mysql.service
	rm -rf /var/www/api/app && cp -r api/app /var/www/api/app && cd /var/www/api/app && $(PY) -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	sudo systemctl start mysql.service
	sudo systemctl start api.service

server-web:
	git pull origin main
	rm -rf /var/www/svelte/* && cd ../.. && unzip build.zip && cd build && cp -r * /var/www/svelte/
	sudo systemctl restart svelte.service

server-db:
	sudo systemctl stop svelte.service
	sudo systemctl stop api.service
	cd api/app/db
	mysql -u guides -pgatorguides < api/app/db/Schema.sql 
	mysql -u guides -pgatorguides < api/app/db/Inserts.sql 
	sudo systemctl start api.service
	sudo systemctl start svelte.service
