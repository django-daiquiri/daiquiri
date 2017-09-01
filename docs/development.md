Development setup
=================

Install prerequisites
---------------------

Install the prerequisites for your Linux distribution as described [here](prerequisites).


Create user
-----------

Either run Daiquiri as your regular Desktop user or create a dedicated user:

```
useradd -m -d /srv/daiquiri daiquiri -s /bin/bash
su - daiquiri
```

Don't run Daiquiri as root!


Obtain repositories
-------------------

Clone the repositories and call them `daiquiri`, `app`, and `queryparser`:

```
git clone https://github.com/aipescience/django-daiquiri daiquiri
git clone https://github.com/aipescience/django-daiquiri-app app
git clone https://github.com/aipescience/queryparser queryparser
```

Build the queryparser
---------------------

Change to the queryparser directory, fetch `antlr` and run `make`:

```
cd queryparser
wget http://www.antlr.org/download/antlr-4.7-complete.jar
make
```

Install python dependencies
---------------------------

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

Setup the app
-------------

Create a `log` and a `download` directory:

```
mkdir log download
```

Create the test databases from `../daiquiri/testing/data`:

```
mysql < ../daiquiri/testing/sql/daiquiri_data_obs.sql
mysql < ../daiquiri/testing/sql/daiquiri_data_sim.sql
mysql < ../daiquiri/testing/sql/daiquiri_user_user.sql
```

Copy the `local.py` settings file:

```
cp config/settings/sample.local.py config/settings/local.py
```

Edit config/settings/local.py for database settings, `ASYNC = True` and `DEBUG = True` and add

```
import os
from . import BASE_DIR
FIXTURE_DIRS = (
    os.path.join(BASE_DIR, '../daiquiri/testing/fixtures'),
)
```

at the end of the file.

Create the front end library vendor bundles:

```
npm install
npm run webpack
```

Next, the differenet users and permissions need to be created on `mysql`. For this purpose, the `sqlcreate` can be used to see what needs to be executed on the database:

```
./manage.py sqlcreate daiquiri_data_obs daiquiri_data_sim
```

Either copy the output line by line to a mysql shell, or use a pipe:

```
./manage.py sqlcreate daiquiri_data_obs daiquiri_data_sim | mysql
```

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
./manage.py loaddata ../daiquiri/testing/fixtures/*
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
