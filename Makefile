
lint:
	poetry run flake8

test:
	poetry run python -m doctest example/equal.py
