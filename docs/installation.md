Installation
============

Set up Daiquiri
---------------

Clone the repositories and call them `daiquiri`, `app`, and `queryparser`:

```
git clone https://github.com/aipescience/django-daiquiri daiquiri
git clone https://github.com/aipescience/django-daiquiri-app app
git clone https://github.com/aipescience/queryparser queryparser
```

Change to the queryparser directory, fetch `antlr` and run `make`:

```
cd queryparser
wget http://www.antlr.org/download/antlr-4.7-complete.jar
make
```

Change to the `app` directory and create a virtualenv:

```
cd ../app
virtualenv env
source env/bin/activate
```

or for `python3`:

```
cd app
python3 -m venv env3
source env3/bin/activate
```

Install the requirements in editable mode:

```
pip install -I -e ../daiquiri
pip install -I -e ../queryparser
pip install mysqlclient
```

Create a `log` and a `download` directory:

```
mkdir log download
```

Create the test databases from `/data`:

```
mysql -e 'CREATE DATABASE daiquiri_data_obs'
mysql -e 'CREATE DATABASE daiquiri_data_sim'

mysql daiquiri_data_obs < data/daiquiri_data_obs.sql
mysql daiquiri_data_sim < data/daiquiri_data_sim.sql
```

Copy the `local.py` settings file:

```
cp config/settings/sample.local.py config/settings/local.py
```

Edit config/settings/local.py for database settings, `ASYNC = True` and `DEBUG = True`.

Create the front end library vendor bundles:

```
npm install
npm run webpack
```

Run `sqlcreate` to see what needs to be created on the database

```
./manage.py sqlcreate daiquiri_data_obs daiquiri_data_sim
```

Create users, permissions, and databases on `mysql`.

Run the tests:

```
 ./manage.py test daiquiri --keepdb
```

Run the database migrations:

```
./manage.py migrate
./manage.py migrate --database=tap
```

Import the fixtures:

```
./manage.py loaddata fixtures/*
```

Run the development server:

```
./manage.py runserver
```

Go to `http://localhost:8000` in your web browser.


Open three other terminals, got to the `app` directory, activate the virtual environment, and run:

```
./manage.py runworker default
```

```
./manage.py runworker query
```

```
./manage.py runworker download
```

to start the different workers.


Additioal information
---------------------

MariaDB
~~~~~~~

The default character set in MariaDB 10.0.27 is utf8b4. This causes a django-error for the migration:

```
django.db.utils.OperationalError: (1071, 'Specified key was too long; max key length is 767 bytes')
```

Solution 1: set the django DB settings: [https://docs.djangoproject.com/el/1.10/ref/settings/#charset]

Solution 2: create your database with the utf8 character set.

```
create database <DBname> CHARACTER SET utf8;
```
