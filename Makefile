all: lint test

test:
	poetry run behave

lint:
	poetry run pre-commit run --all-files

image:
	docker build -t openremote/openremote-cli --no-cache .

multi-image:
	docker buildx build --push --platform linux/arm64,linux/amd64 -t openremote/openremote-cli --no-cache .

bump:
	poetry version patch
