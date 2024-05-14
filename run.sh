pip install poetry
poetry install
cd app
gunicorn geodjango.wsgi