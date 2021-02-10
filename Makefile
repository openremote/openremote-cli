all: lint test versionbump

test:
	behave

lint:
	pre-commit run --all-files

versionbump:
	poetry version patch
