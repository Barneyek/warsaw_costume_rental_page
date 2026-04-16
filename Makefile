DC      := docker compose
DC_RUN  := $(DC) run --rm
M       := $(MAKE) --no-print-directory
DRY_RUN ?=

help: ## Pokaż dostępne komendy
	@echo 'Użycie:'
	@echo ''
	@echo '  make <target>'
	@echo ''
	@grep -E '^([a-zA-Z_-]+):.*?## .*$$' Makefile \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ————————————————————————————————————————
# Docker
# ————————————————————————————————————————

docker-build: ## Zbuduj obrazy Dockera
	$(DC) build --progress=plain


docker-shell: ## Wejdź do shella kontenera API
	$(DC) exec -it api bash

up: ## Uruchom projekt
	$(DC) up

up-build: ## Uruchom projekt z przebudowaniem obrazów
	$(DC) up --build

down: ## Zatrzymaj projekt
	$(DC) down

# ————————————————————————————————————————
# Django (użycie: make django ARGS="migrate")
# ————————————————————————————————————————

django: ## Uruchom komendę Django np. make django ARGS="migrate"
	$(DC_RUN) api python manage.py $(ARGS)

migrate: ## Wykonaj migracje
	@$(M) django ARGS="migrate $(DRY_RUN)"

makemigrations: ## Utwórz pliki migracji
	@$(M) django ARGS="makemigrations"

createsuperuser: ## Utwórz superusera
	@$(M) django ARGS="createsuperuser"

# ————————————————————————————————————————
# Dane
# ————————————————————————————————————————

seed: ## Wypełnij bazę danymi testowymi
	@$(M) django ARGS="seed"

init-data: ## Migracje + seed (pełny setup bazy)
	@$(M) migrate && \
	$(M) seed

# ————————————————————————————————————————
# Testy
# ————————————————————————————————————————

test: ## Uruchom testy
	$(DC_RUN) -T -e DJANGO_SETTINGS_MODULE=web_app.settings.test api pytest

test-verbose: ## Uruchom testy z detalami
	$(DC_RUN) -T -e DJANGO_SETTINGS_MODULE=web_app.settings.test api pytest -v