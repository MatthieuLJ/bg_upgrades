
Architecture
============

BG upgrades is using the **django** framework at its core.

The overall architecture should be pretty standard with one central form generated from `tuckbox/templates/pattern_form.html.j2`

It uses Redis and Celery to process the requests asynchronously (and report on progress).

Requirements
============

* Python 3 (possibly also python3.X-dev on ubuntu)
* pip packages listed in requirements.txt
* `imagemagick`
* `nginx` (for full deployment)
* `redis`

Development
===========

To setup an environment, use virtualenv and install the packages listed in requirements.txt

    $ virtualenv [--python=/your/path/to/python3] venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    $ webdrivermanager chrome --linkpath [folder in your PATH]

To run the tests:

    $ ./manage.py test

Run only Django's test server:

    $ redis-server
    $ watchmedo auto-restart --directory=./ --pattern="*.py" --recursive -- celery -A bg_upgrades worker -l info

    $ ./manage.poy migrate
    $ ./manage.py runserver

Run uwsgi with the CLI options

    $ uwsgi -H venv --socket mysite.sock --module bg_upgrades.wsgi --chmod-socket=664

Startup / Deploy
================


To deploy, you need to setup those environment variables:

* `DJANGO_DEBUG` to 'False'
* `DJANGO_SECRET_KEY`. This can be generated:

    $ python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

* `DJANGO_PROJECT_PATH` to the folder with the project

Configuration for nginx should be updated with the right paths and placed in the right folder
* `/usr/local/etc/nginx/servers/` on mac
* `/etc/nginx/servers/` on linux


Start all those different services:

    $ redis-server
    $ celery -A bg_upgrades worker -l info

    $ ./manage.py migrate
    $ ./manage.py collectstatic

    $ uwsgi --ini uwsgi.ini

Start the nginx server
    $ brew services restart nginx

    $ sudo /etc/init.d/nginx restart

Optionally:

    $ flower -A bg_upgrades

The overall deployment framework is using nginx and uWSGI as documented (here)[https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html].

SSL / TLS
=========

Set the environment variables: `DOMAIN` to bg-upgrades.net and `WILDCARD` to `*.$DOMAIN`

    $ sudo add-apt-repository ppa:certbot/certbot
    $ sudo apt install python-certbot-nginx
    $ sudo certbot -d $DOMAIN -d $WILDCARD --nginx --preferred-challenges dns certonly

Instructions also (here)[https://www.nginx.com/blog/using-free-ssltls-certificates-from-lets-encrypt-with-nginx/]

Maintenance
===========

To find packages that need to be updated, you can check [this link](https://requires.io/github/MatthieuLJ/bg_upgrades/requirements/?branch=master) or run `$ pip list --outdated`

Then update:

    $ pip install <package_name> --upgrade

Whenever the packages change, record the packages:

    $ pip freeze > requirements.txt

When the data needs to change for the tests, run:

    $ python -m tuckbox.test.tests_box


