Daiquiri (Django version)
=========================

**A framework for the publication of scientific databases**

.. image:: https://travis-ci.org/aipescience/django-daiquiri.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/aipescience/django-daiquiri

.. image:: https://coveralls.io/repos/github/aipescience/django-daiquiri/badge.svg?branch=master
   :alt: Coverage Status
   :target: https://coveralls.io/github/aipescience/django-daiquiri?branch=master

.. image:: https://img.shields.io/pypi/v/django-daiquiri.svg?style=flat
   :alt: Latest Version
   :target: https://pypi.python.org/pypi/django-daiquiri/

.. image:: http://img.shields.io/badge/license-APACHE-blue.svg?style=flat
    :target: https://github.com/aipescience/django-daiquiri/blob/master/LICENSE

This project is currently in an early alpha stage of development and not production ready.

The legacy version of Daiquiri written in PHP can be found `here <https://github.com/aipescience/daiquiri>`_.


Quick start
-----------

Install prerequisites
~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    apt-get install -y git build-essential libxml2-dev libxslt-dev zlib1g-dev libssl-dev
    apt-get install -y mariadb-client mariadb-server libmariadb-dev libmariadbclient-dev

More about Daiquiri's prerequisites including different Linux distributions can be found `here <https://github.com/aipescience/django-daiquiri/tree/master/docs/prerequisites.md>`_.

Fork the daiquiri-app
~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    git clone https://github.com/aipescience/django-daiquiri-app app

Set up the virtual enviroment and install dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    cd app
    python3 -m venv env
    source env/bin/activate
    pip install django-daiquiri mysqlclient

Setup Daiquiri
~~~~~~~~~~~~~~

.. code:: bash

    cp config/settings/sample.local.py config/settings/local.py
    mkdir log download

    ./manage.py sqlcreate               # shows the commands to be executed on MariaDB
    ./manage.py migrate                 # creates database and tables
    ./manage.py migrate --database=tap  # creates TAP_SCHEMA
    ./manage.py createsuperuser         # creates admin user
    ./manage.py runserver               # runs a development server

Navigate to http://localhost:8000 in your browser.

More detailed installation instructions can be found `here <https://github.com/aipescience/django-daiquiri/tree/master/docs/installation.md>`_.

Our development setup is documented `here <https://github.com/aipescience/django-daiquiri/tree/master/docs/development.md>`_.

More documentation will be added soon.
