serve:
	poetry run uvicorn main:app --reload & (cd site/;npm start)

lint:
	poetry run pre-commit run --all-files

test:
	poetry run python -m tests.test_database
	poetry run python -m db.api
	poetry run python -m doctest problems/scripts/problem_11_are_equal.py
	poetry run python -m doctest problems/scripts/problem_12_equal_except_integers.py

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

# Note: needs to run as sudo user
docker_up:
	docker-compose up

docker_up_build:
	docker-compose up --build

docker_cleanup_all:
	docker system prune -a --volumes

postgresql_linux_stop:
	systemctl stop postgresql.service

postgresql_linux_start:
	systemctl start postgresql.service
