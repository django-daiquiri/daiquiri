import re

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
    long_description=open('README.md').read(),
    install_requires=[
        'Django>=2.1.3',
        'djangorestframework>=3.9.0 ',
        'drf-extensions>=0.4.0',
        'django-extensions>=2.1.3',
        'django-allauth>=0.38.0',
        'django-filter==2.0.0',
        'django-widget-tweaks>=1.4.3',
        'django-libsass>=0.7',
        'django-settings-export>=1.2.1',
        'django-sendfile>=0.3.11',
        'django-ipware>=2.1.0',
        'django-vendor-files>=0.1.1',
        'django-test-generator>=0.5.1',
        'celery>=4.2.1',
        'rules>=2.0',
        'jsonfield==2.0.2',
        'Markdown>=3.0.1',
        'iso8601>=0.1.12',
        'ipaddress>=1.0.22',
        'XlsxWriter>=1.1.2',
        'coverage>=4.5.1',
        'queryparser_python3>=0.4.2'
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
