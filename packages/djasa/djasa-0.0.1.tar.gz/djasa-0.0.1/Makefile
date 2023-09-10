.PHONY: help makemigrations migrate createsuperuser shell test lint format

DOCKER_SERVICE_NAME=backend
DOCKER_COMPOSE_EXEC=docker-compose exec $(DOCKER_SERVICE_NAME)
PROJECT_NAME=example_project
PYTHONPATH=$(PWD):$(PROJECT_NAME)

.DEFAULT: help
help:
	@echo "make makemigrations"
	@echo "       make Django migrations"
	@echo "make migrate"
	@echo "       apply Django migrations"
	@echo "make createsuperuser"
	@echo "       create Django super user"
	@echo "make shell"
	@echo "       open Django shell"
	@echo "make test"
	@echo "       run tests"
	@echo "make lint"
	@echo "       run linter"
	@echo "make format"
	@echo "       run formatter"

test:
	@bash ./scripts/test.sh

lint:
	@bash ./scripts/lint.sh

format:
	@bash ./scripts/format.sh


# Dev project commands

run:
	@export PYTHONPATH=$(PYTHONPATH) && uvicorn $(PROJECT_NAME).conf.asgi:application --reload --host 0.0.0.0 --port 8000 --log-level debug

runserver:
	@export PYTHONPATH=$(PYTHONPATH) && python $(PROJECT_NAME)/manage.py runserver

makemigrations:
	@export PYTHONPATH=$(PYTHONPATH) && python $(PROJECT_NAME)/manage.py makemigrations

migrate:
	@export PYTHONPATH=$(PYTHONPATH) && python $(PROJECT_NAME)/manage.py migrate

createsuperuser:
	@export PYTHONPATH=$(PYTHONPATH) && python $(PROJECT_NAME)/manage.py createsuperuser --username admin --email admin@localhost.com

add_initial_data:
	@export PYTHONPATH=$(PYTHONPATH) && python $(PROJECT_NAME)/manage.py add_initial_data