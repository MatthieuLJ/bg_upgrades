To setup an environment, use virtualenv and install the packages listed in requirements.txt

$ virtualenv --python=/your/path/to/python2 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ brew install imagemagick

To find packages that need to be updated
$ pip list --outdated
Then update:
$ pip install <package_name> --upgrade
Record the packages:
$ pip freeze > requirements.txt

When the data needs to change for the tests:
(top project folder) $ python -m tuckbox.tests_box

$ webdrivermanager chrome --linkpath ~/.bin

To run the tests:
$ ./manage.py test