serve:
	poetry run uvicorn main:app --reload & (cd site/;npm start)

lint:
	poetry run pre-commit run --all-files

test:
	poetry run python -m db.api
	poetry run python -m doctest example/equal.py

install:
	poetry install
	poetry run pre-commit install
