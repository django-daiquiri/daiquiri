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

Create a `django-daiquiri` directory at a convenient place:

```
mkdir django-daiquiri
cd django-daiquiri
mkdir log
```

Set up a virtualenv in this directory:

```
virtualenv env
source env/bin/activate
```

Clone the repositories and call the `daiquiri` and `app`:

```
git clone https://github.com/aipescience/django-daiquiri daiquiri
git clone https://github.com/aipescience/django-daiquiri-app app
```

Install the requirements:

```
cd app
pip install -r requirements/base.txt
pip install -r requirements/mysql.txt
```

Copy the `local.py` settings file:

```
cp daiquiri_app/settings/sample.local.py daiquiri_app/settings/local.py
```

Edit daiquiri_app/settings/local.py for database settings and 'DEBUG = True' and add

```
import sys; sys.path.append('../daiquiri/')
```

at the top of the file.

Run:

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
