# PPTC Keyence Vision System for Miseq Tray Inspection

Program is hosted on a local webserver, powered by [Flask](https://palletsprojects.com/p/flask/), a lightweight WSGI web application framework.

## Setting up the environment

### Python

Check if python is installed with

`python --version` or `py --version`

If not, install [python 3](https://www.python.org/downloads/).

### Pip

Pip framework should be installed if you are using Python 2 >=2.7.9 or Python 3 >=3.4. Check if pip is installed using

`pip --version`

If not, follow this [installation guide](https://pip.pypa.io/en/stable/installing/).

### Python virtual environment

Choice of virtual environment is up to you. [venv](https://docs.python.org/3/library/venv.html) is default in Python 3.3 or later.

For windows, it is recommended to install [virtualenvwrapper-win](https://pypi.org/project/virtualenvwrapper-win/). To install using pip, run

`pip install virtualenvwrapper-win`

The next few steps assumes you are using virtualenvwrapper.

Create a virtual environment. `env-name` can be replaced with anything.

`mkvirtualenv env-name`

To view the list of virtual environments, run

`workon`

Access the virtual environment you created with

`workon env-name`

Open the project directory in your terminal. Set the project directory for the virtual environment with

`setprojectdir .`

Install all the dependencies for the project with

`pip install -r requirements.txt`

Set up is now complete.

### Deactivating

To deactivate the virtual environment, simply close the terminal, or use

`deactivate`

## Updating dependencies and requirements.txt

To update dependencies, pull the updated requirements.txt and run

`pip install -r requirements.txt`

To update requirements.txt, enter the virtual environment for the project and run

`pip freeze > requirements.txt`

Commit and push when done.

## Accessing database

Database can be accessed through a query using SQLAlchemy.

In the root folder, enter the python interpreter. Then, run

```python
from app.models import User
```

to obtain User database instance, which can be queried.

To query a table, e.g. User:

```python
User.query.all()
```

Further information can be obtained at the SQLAlchemy [documentation (v1.3)](https://docs.sqlalchemy.org/en/13/).

## Account type information

*Root* - Cannot be deleted normally. Has all admin rights.

*Administrator* - Has permission to manage user database. No restrictions.

*Operator* - Only has permission to operate the program.
