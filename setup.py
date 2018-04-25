import re
import sys

from setuptools import setup, find_packages

with open('daiquiri/__init__.py') as f:
    metadata = dict(re.findall(r'__(.*)__ = [\']([^\']*)[\']', f.read()))

setup(
    name=metadata['title'],
    version=metadata['version'],
    author=metadata['author'],
    author_email=metadata['email'],
    maintainer=metadata['author'],
    maintainer_email=metadata['email'],
    license=metadata['license'],
    url='https://github.com/aipescience/django-daiquiri',
    description=u'Daiquiri is a framework for the publication of scientific databases.',
    long_description=open('README.rst').read(),
    install_requires=[
        'Django>=1.11,<2.0',
        'djangorestframework==3.8.0',
        'drf-extensions>=0.3.1',
        'django-extensions>=1.8.1',
        'wheel>=0.30.0',
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
        'bitstring>=3.1.5',
        'ipaddress>=1.0.18',
        'django-test-generator>=0.3.3',
        'typing',
        'mock',
        'coverage',
        'queryparser_python%d>=0.3' % sys.version_info.major
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
