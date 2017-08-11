# -*- coding: utf-8 -*-
import sys

from setuptools import setup, find_packages

version = '0.1.0'

python_version = sys.version_info.major

requirements = (
    'wheel',
    'Django==1.11',
    'djangorestframework==3.6.2',
    'drf-extensions==0.3.1',
    'django-extensions==1.8.1',
    'django-allauth==0.32.0',
    'django-filter==1.0.4',
    'django-widget-tweaks==1.4.1',
    'django-compressor==2.1.1',
    'django-libsass==0.7',
    'django-bower==5.2.0',
    'django-settings-export==1.2.1',
    'django-sendfile==0.3.11',
    'django-ipware==1.1.6',
    'celery==4.0.2',
    'redis==2.10.5',
    'rules==1.2',
    'jsonfield==1.0.0',
    'Markdown==2.6.8',
    'iso8601==0.1.11',
    'lxml==3.7.3',
    'bitstring==3.1.5',
    'ipaddress==1.0.18',
    'queryparser_python%d' % python_version,
    'mysqlclient==1.3.10',
)

setup(
    name='django-daiquiri',
    version=version,
    description=u'Daiquiri is a framework for the publication of scientific databases.',
    long_description=open('README.rst').read(),
    url='https://github.com/aipescience/django-daiquiri',
    author=u'Anastasia Galkin, Jochen Klar, Gal Matijevic, Kristin Riebe',
    author_email='escience@aip.de',
    maintainer=u'Jochen Klar',
    maintainer_email=u'jklar@aip.de',
    license=u'Apache License (2.0)',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Astronomy'
    ]
)
