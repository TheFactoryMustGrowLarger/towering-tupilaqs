serve:
	poetry run uvicorn main:app --reload & (cd site/;npm start)

lint:
	poetry run pre-commit run --all-files

test:
	poetry run python -m db.api
	poetry run python -m doctest example/equal.py

install:
	(cd site;npm install)
	poetry install
	poetry run pre-commit install

install_local:
	cp db/db_config/database_local.ini db/db_config/database.ini

install_remote:
	cp db/db_config/database_remote.ini db/db_config/database.ini

install_docker:
	cp db/db_config/database_docker.ini db/db_config/database.ini
