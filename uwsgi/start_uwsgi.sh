#!/bin/sh

cd /app

python ./manage.py migrate
python ./manage.py collectstatic --noinput

rm -Rf tmp/tmp*

uwsgi --ini /app/uwsgi.ini