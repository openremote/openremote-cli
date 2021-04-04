all: lint test

test:
	poetry run behave

lint:
	poetry run pre-commit run --all-files

image:
	docker build -t openremote/openremote-cli --no-cache .

lambda:
	aws ecr get-login-password | docker login --username AWS --password-stdin $(AWS_REPOSITORY_URL)
	docker tag openremote/openremote-cli:latest $(AWS_REPOSITORY_URL)
	docker push $(AWS_REPOSITORY_URL)

multi-image:
	docker buildx build --push --platform linux/arm64,linux/amd64 -t openremote/openremote-cli --no-cache .

bump:
	poetry version patch
