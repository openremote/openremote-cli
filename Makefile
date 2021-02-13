all: lint test

test:
	poetry run behave

lint:
	poetry run pre-commit run --all-files

bump:
	poetry version patch
