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
        # in alphabetical order
        'astropy>=3.1',
        'celery>=4.3',
        'coverage>=4.5',
        'Django>=2.2',
        'django-allauth>=0.39',
        'django-compressor>=2.2',
        'django-extensions>=2.1',
        'django-filter>=2.1',
        'django-ipware>=2.1',
        'django-libsass>=0.7',
        'django-sendfile>=0.3',
        'django-settings-export>=1.2',
        'django-test-generator>=0.6',
        'django-vendor-files>=0.1',
        'django-widget-tweaks>=1.4',
        'djangorestframework>=3.9',
        'drf-extensions>=0.4.0',
        'ipaddress>=1.0',
        'iso8601>=0.1',
        'jsonfield>=2.0',
        'Markdown>=3.1',
        'queryparser_python3>=0.4.2',
        'rules>=2.0',
        'XlsxWriter>=1.1',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Astronomy'
    ],
    packages=find_packages(),
    include_package_data=True
)
