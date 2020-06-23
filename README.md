
Architecture
============

BG upgrades is using the **django** framework at its core.

The overall architecture should be pretty standard with one central form generated from `tuckbox/templates/pattern_form.html.j2`

It uses Redis and Celery to process the requests asynchronously (and report on progress).

Requirements
============

* Python 3
* pip packages listed in requirements.txt
* `imagemagick`
* `nginx` (for full deployment)

Development
===========

To setup an environment, use virtualenv and install the packages listed in requirements.txt

    $ virtualenv [--python=/your/path/to/python3] venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    $ webdrivermanager chrome --linkpath [folder in your PATH]

To run the tests:

    $ ./manage.py test

Startup / Deploy
================

Start all those different services:

    $ redis-server
    $ celery =A bg_upgrades worker -l info

    $ ./manage.py migrate
    $ ./manage.py collectstatic

Optionally:

    $ flower -A bg_upgrades

To deploy, you need to setup those environment variables `DJANGO_DEBUG` to 'False' and `DJANGO_SECRET_KEY`. This latter one can be generated:

    $ python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

The overall deployment framework is using nginx and uWSGI as documented (here)[https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html].



Maintenance
===========

To find packages that need to be updated, you can check [this link](https://requires.io/github/MatthieuLJ/bg_upgrades/requirements/?branch=master) or run `$ pip list --outdated`

Then update:

    $ pip install <package_name> --upgrade

Whenever the packages change, record the packages:

    $ pip freeze > requirements.txt

When the data needs to change for the tests, run:

    $ python -m tuckbox.tests_box


