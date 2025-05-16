#!/bin/sh

cd /app

python ./manage.py migrate
python ./manage.py collectstatic --noinput

rm -Rf tmp/tmp*

chown -R app:app /sock

uwsgi --ini /app/uwsgi.ini