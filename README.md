# Daiquiri

[![pytest Workflow Status](https://github.com/django-daiquiri/daiquiri/actions/workflows/pytest.yml/badge.svg)](https://github.com/django-daiquiri/daiquiri/actions/workflows/pytest.yml)
[![Coverage Status](https://coveralls.io/repos/django-daiquiri/daiquiri/badge.svg?branch=main&service=github)](https://coveralls.io/github/django-daiquiri/daiquiri?branch=main)
[![Latest Version](https://img.shields.io/pypi/v/django-daiquiri.svg?style=flat)](https://pypi.org/project/django-daiquiri/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-daiquiri.svg)](https://pypi.org/project/django-daiquiri/)
[![Documentation](https://img.shields.io/badge/docs-online-blue)](https://django-daiquiri.github.io/)
[![License](https://img.shields.io/github/license/django-daiquiri/daiquiri)](https://github.com/django-daiquiri/daiquiri/blob/main/LICENSE)

Daiquiri is a Django framework and Python package for building scientific
data-publication web applications. It provides database query interfaces and
APIs, metadata management, file downloads, asynchronous jobs, and
standards-based endpoints such as TAP, Cone Search, and OAI-PMH.

## Quick start

### Try the default app with the PyPI package

The simplest way to try Daiquiri is through [`dq-dev`](https://github.com/django-daiquiri/dq-dev).
You need Git, Docker Engine, Docker Compose v2, and Python 3.11 or newer.

Clone the default application and the container workflow. You do not need to
clone the Daiquiri source repository for this setup:

```bash
git clone https://github.com/django-daiquiri/app.git
git clone https://github.com/django-daiquiri/dq-dev.git

cd dq-dev
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
python manage.py -c quickstart
python manage.py -s quickstart
```

Edit `usr/profiles/quickstart/conf.toml` and set the absolute path to the
default application. Comment out both `dq_source` entries so that `dq-dev`
installs the released `django-daiquiri` package from PyPI:

```toml
[folders_on_host]
dq_app = "/absolute/path/to/app"
# dq_source = "/path/to/daiquiri"

[docker_volume_mountpoints]
dq_app = "/home/dq/app"
# dq_source = "/home/dq/source"
```

Keep the default development settings:

```toml
[env.daiquiri]
debug = true
enable_gunicorn = false
```

Start the profile:

```bash
python manage.py -r
```

Open <http://localhost:9280> in a browser. The default profile starts the
Daiquiri application and PostgreSQL containers. Asynchronous workers are
disabled by default.

### Develop Daiquiri with a local source checkout

If you are developing Daiquiri itself, also clone the source repository:

```bash
git clone https://github.com/django-daiquiri/daiquiri.git
```

Set `dq_source` in the host-side folder configuration to the absolute path of
that checkout. Keep the container mount point unchanged:

```toml
[folders_on_host]
dq_app = "/absolute/path/to/app"
dq_source = "/absolute/path/to/daiquiri"

[docker_volume_mountpoints]
dq_source = "/home/dq/source"
```

Run the same `dq-dev` profile and edit the Daiquiri source on the host. With
`debug = true` and `enable_gunicorn = false`, the development server reloads
Python changes and they can be viewed at <http://localhost:9280>.

See [`CONTRIBUTING.rst`](CONTRIBUTING.rst) for the development and pull-request
workflow.

## Documentation

- [Full installation](https://django-daiquiri.github.io/docs/installation/)
- [Deployment](https://django-daiquiri.github.io/docs/deployment/)
- [Configuration and settings](https://django-daiquiri.github.io/docs/settings/)
- [Administration](https://django-daiquiri.github.io/docs/administration/)
- [Daiquiri documentation](https://django-daiquiri.github.io/)

For issues and feature requests, use the [GitHub issue tracker](https://github.com/django-daiquiri/daiquiri/issues).

## License

Daiquiri is released under the [Apache License 2.0](LICENSE).
