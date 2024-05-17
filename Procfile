release: django-admin migrate --noinput
web: gunicorn marmut.wsgi:application --bind 0.0.0.0:$PORT
