# Tower Tupilaqs
![Tupilaqs in Paris](images/tower-tupilaqs-paris.jpg)

Image credit: Adapted from

- Ansgar Walk, CC BY-SA 3.0 <https://creativecommons.org/licenses/by-sa/3.0>, via Wikimedia Commons
- Wladyslaw (Taxiarchos228), CC BY 3.0 <https://creativecommons.org/licenses/by/3.0>, via Wikimedia Commons

## Introduction
Quiz game to determine if a piece of code is a bug or a feature for Python Discord Code Jam 2022

# Requirements
[poetry](https://python-poetry.org/) is used for dependency management. Follow the install guide for your system:
[https://python-poetry.org/docs/master/#installing-with-the-official-installer](https://python-poetry.org/docs/master/#installing-with-the-official-installe)

## Add poetry to Windows Path
If poetry does not get added to your path ("poetry is not recognized as an internal or external command..."), click the windows start menu and search for "environment", you should get a hit for
"edit environment variables for your account" and a dialog similar to this: [win10-env](https://www.computerhope.com/issues/pictures/win10-envirvariables.jpg). In the top dialog, select (or create if it does not exists) the Path variable and add the directory where poetry was installed (i.e. "c:\Users\xx\AppData\Roaming\Python\Scripts"). Restart the command line-shell for the changes to take effect

## Poetry install
In the towering-tupilaqs directory, use a terminal to:
```
poetry install
poetry run pre-commit install
```
also available as `make install` if you have make.

If problems with the requirements not solving, delete the `poetry.lock` file and try again (the `pyproject.toml` will be used instead and a new `poetry.lock` will be created).

## Local database
Linux only, follow: [https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart) with username, password and db name "quiz". To configure password, use the `\password` command:
```
$sudo -u quiz psql
quiz=# \password
```
Windows only, follow: [https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql/](https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql/) when you have a PSQL shell open and logged into the postgres SUPERUSER, do the following:
```
postgres=# CREATE USER quiz WITH PASSWORD 'quiz';
CREATE ROLE
postgres=# CREATE DATABASE quiz WITH ENCODING 'UTF8' LC_COLLATE='English_United States' LC_CTYPE='English_United States';
CREATE DATABASE
```
## Remote database
To use the remote database, change the `db/api.py` line:
```
conn = connect(**config(section='local'))
```
to `'remote'`. FIXME: better way to switch.

## Run
To serve the initial webpage, use
```
poetry run uvicorn main:app --reload
```
also available as `make serve` if you have make.

This should serve two preliminary webpages:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/solve_quiz?

Python code will log to `tupilaqs.log`.
