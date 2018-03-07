Installation
============

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


Clone the app
-------------

Clone the [django-daiquiri-app](https://github.com/aipescience/django-daiquiri-app) to a directory of your choice:

```
git clone https://github.com/aipescience/django-daiquiri-app app
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

Install the requirements:

```
pip install django-daiquiri
pip install mysqlclient      # for MySQL
pip install psycopg2-binary  # for PostgreSQL
```

Setup the app
-------------

Create a `log` and a `download` directory:

```
mkdir log download
```

Copy the `local.py` settings file:

```
cp config/settings/sample.local.py config/settings/local.py
```

Edit config/settings/local.py for database settings, `ASYNC = True` and `DEBUG = True`.

Create the front end library vendor bundles:

```
./manage.py download_vendor_files
```

Next, the differenet users and permissions need to be created on the database. For this purpose, the `sqlcreate` can be used to see what needs to be executed on the database:

```
./manage.py sqlcreate                             # databases, users and permissions to run daiquiri
./manage.py sqlcreate --test                      # databases, users and permissions to run tests
./manage.py sqlcreate --schema=daiquiri_data_obs  # databases, users and permissions to use a particular schema with scientific data
```

Copy the output line by line to a database shell, or use a pipe.

Run the database migrations:

```
./manage.py migrate
./manage.py migrate --database=data
```

Create a superuser

```
./manage.py createsuperuser
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
