# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '0.0.0'

github_url = 'https://github.com/aipescience/django-daiquiri/'

install_requires = [
    'Django==1.8',
    'django-widget-tweaks==1.4.1',
    'djangorestframework==3.3.2',
]

setup(
    name='django-daiquiri',
    version=version,
    url=github_url,
    download_url='%s/archive/%s.tar.gz' % (github_url, version),
    packages=find_packages(),
    license=u'Apache License Version 2.0',
    author=u'Anastasia Galkin, Jochen Klar, Gal Matijevic, Kristin Riebe',
    author_email='escience@aip.de',
    maintainer=u'Jochen Klar',
    maintainer_email=u'jklar@aip.de',
    description=u'Daiquiri is a framework for the publication of scientific databases.',
    long_description='',
    include_package_data=True,
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Astronomy'
    ]
)
