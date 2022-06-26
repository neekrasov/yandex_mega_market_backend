python manage.py makemigrations --noinput
python manage.py migrate --noinput
gunicorn --bind 0.0.0.0:8000 config.wsgi