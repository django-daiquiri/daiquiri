Daiquiri (Django version)
=========================

**A framework for the publication of scientific databases**

[![Build Status](https://travis-ci.org/aipescience/django-daiquiri.svg?branch=master)](https://travis-ci.org/aipescience/django-daiquiri)
[![Coverage Status](https://coveralls.io/repos/github/aipescience/django-daiquiri/badge.svg?branch=master)](https://coveralls.io/github/aipescience/django-daiquiri?branch=master)

This project is currently in an early stage of development and by no means production ready.

The PHP version of Daiquiri can be found [here](https://github.com/aipescience/daiquiri).

Development setup
-----------------

Install `npm`:

```
sudo apt-get install npm
```

Install `bower`:

```
sudo npm -g install bower
```

Clone the repositories to a convenient place:

```
git clone https://github.com/aipescience/django-daiquiri
git clone https://github.com/aipescience/django-daiquiri-app
```

If needed checkout a non master branch.

Set up a virtualenv:

```
virtualenv env
source env/bin/activate
pip install -r django-daiquiri-app/requirements/base.txt
pip install -r django-daiquiri-app/requirements/mysql.txt
```

Copy the `local.py` settings file:

```
cd django-daiquiri-app
cp django-daiquiri-app/daiquiri_app/settings/sample.local.py django-daiquiri-app/daiquiri_app/settings/local.py
```

Edit django-daiquiri-app/daiquiri_app/settings/local.py for database settings and 'DEBUG = True' and add

```
import sys; sys.path.append('../django-daiquiri/')
```

at the top of the file.

Change to the `django-daiquiri-app` directory and run:

```
./manage.py migrate
./manage.py bower install
./manage.py createsuperuser
```

Run the development server:

```
./manage.py runserver
```

Go to `http://localhost:8000` in your web browser.
