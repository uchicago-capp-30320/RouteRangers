pip install poetry
poetry install
cd app
poetry run gunicorn geodjango.wsgi