all: lint test

test:
	behave

lint:
	pre-commit run --all-files

bump:
	poetry version patch
