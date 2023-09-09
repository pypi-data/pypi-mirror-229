# huscy.users

![PyPi Version](https://img.shields.io/pypi/v/huscy-users.svg)
![PyPi Status](https://img.shields.io/pypi/status/huscy-users)
![PyPI Downloads](https://img.shields.io/pypi/dm/huscy-users)
![PyPI License](https://img.shields.io/pypi/l/huscy-users?color=yellow)
![Python Versions](https://img.shields.io/pypi/pyversions/huscy-users.svg)
![Django Versions](https://img.shields.io/pypi/djversions/huscy-users)



## Requirements

- Python 3.8+
- A supported version of Django

Tox tests on Django versions 3.2, 4.1 and 4.2.



## Installation

To install `husy.users` simply run:

	pip install huscy.users



## Configuration

The `huscy.users` application has to be hooked into the project.

Add `huscy.users` to `INSTALLED_APPS` in settings module:

```python
INSTALLED_APPS = (
	...

	'huscy.users',
)
```



## Development

After checking out the repository you should activate any virtual environment.
Install all development and test dependencies:

	make install

Create database tables:

	python manage.py migrate

We assume you're having a running postgres database with a user `huscy` and a database also called `huscy`.
You can easily create them by running

	sudo -u postgres createdb huscy
	sudo -u postgres createuser -d huscy
	sudo -u postgres psql -c "ALTER USER huscy WITH PASSWORD '123';"
	sudo -u postgres psql -c "ALTER DATABASE huscy OWNER TO huscy;"
