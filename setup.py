import sys

from setuptools import setup, find_packages

from daiquiri import __title__, __email__, __version__, __author__, __license__

setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__email__,
    maintainer=__author__,
    maintainer_email=__email__,
    license=__license__,
    url='https://github.com/aipescience/django-daiquiri',
    description=u'Daiquiri is a framework for the publication of scientific databases.',
    long_description=open('README.rst').read(),
    install_requires=[
        'Django>=1.11',
        'djangorestframework>=3.6.2',
        'drf-extensions>=0.3.1',
        'django-extensions>=1.8.1',
        'django-allauth>=0.32.0',
        'django-filter>=1.0.4',
        'django-widget-tweaks>=1.4.1',
        'django-compressor>=2.1.1',
        'django-libsass>=0.7',
        'django-settings-export>=1.2.1',
        'django-sendfile>=0.3.11',
        'django-ipware>=1.1.6',
        'celery>=4.1.0',
        'redis>=2.10.5',
        'rules>=1.2',
        'jsonfield==1.0.0',
        'Markdown>=2.6.8',
        'iso8601>=0.1.11',
        'lxml>=3.7.3',
        'bitstring>=3.1.5',
        'ipaddress>=1.0.18',
        'django-test-generator>=0.3.3',
        'mock',
        'coverage',
        'queryparser_python%d>=0.2.3' % sys.version_info.major
    ],
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
    ],
    packages=find_packages(),
    include_package_data=True
)
