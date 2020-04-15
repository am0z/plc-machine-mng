release: python manage.py makemigrations
release: python manage.py migrate
web: gunicorn home.wsgi.dev_local --log-file -
