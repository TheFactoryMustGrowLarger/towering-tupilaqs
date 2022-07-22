serve:
	poetry run uvicorn main:app --reload

lint:
	poetry run pre-commit run --all-files

test:
	poetry run python -m doctest example/equal.py
