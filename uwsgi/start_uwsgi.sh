#!/bin/sh

cd /app

python ./manage.py migrate
python ./manage.py collectstatic --noinput

rm -Rf tmp/tmp*

chown -R app:app /sock
chown -R app:app /app/tmp

uwsgi --ini /app/uwsgi.ini