import re

from setuptools import setup, find_packages

# get metadata from mudule using a regexp
with open('daiquiri/__init__.py') as f:
    metadata = dict(re.findall(r'__(.*)__ = [\']([^\']*)[\']', f.read()))

# get install_requires from requirements.txt
with open('requirements.txt') as f:
    install_requires = f.readlines()

setup(
    name=metadata['title'],
    version=metadata['version'],
    author=metadata['author'],
    author_email=metadata['email'],
    maintainer=metadata['author'],
    maintainer_email=metadata['email'],
    license=metadata['license'],
    url='https://github.com/django-daiquiri/daiquiri',
    description=u'Daiquiri is a framework for the publication of scientific databases.',
    long_description=open('README.md').read(),
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django :: 4.2',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Astronomy'
    ],
    packages=find_packages(),
    include_package_data=True
)
