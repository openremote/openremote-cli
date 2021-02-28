all: lint test

test:
	poetry run behave

lint:
	poetry run pre-commit run --all-files

image:
	docker build -t openremote/openremote-cli --no-cache .
	docker push openremote/openremote-cli

bump:
	poetry version patch
