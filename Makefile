install:
	uv sync

collectstatic:
	uv run python manage.py collectstatic --no-input

migrate:
	uv run python manage.py migrate

setup: install collectstatic migrate

build:
	./build.sh

render-start:
	uv run gunicorn task_manager.wsgi

start:
	uv run python manage.py runserver

lint:
	uv run ruff check

.PHONY: install collectstatic migrate setup build render-start start lint
