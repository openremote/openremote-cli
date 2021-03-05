all: lint test

test:
	poetry run behave

lint:
	poetry run pre-commit run --all-files

image:
	docker build -t openremote/openremote-cli --no-cache .
	docker push openremote/openremote-cli

multi-image:
	docker buildx build --push --platform linux/arm64,linux/amd64,linux/arm/v7 -t openremote/openremote-cli --no-cache .

bump:
	poetry version patch
