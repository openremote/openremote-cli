all: lint test bump

test:
	behave

lint:
	pre-commit run --all-files

bump:
	poetry version patch
