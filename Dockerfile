FROM python:3.9-slim

RUN apt update && apt install curl unzip -y --no-install-recommends && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

# Install Docker client for deploy
RUN curl -sSL https://get.docker.com/ | sh

RUN pip install openremote-cli

USER 1000

ENTRYPOINT [ "/usr/local/bin/openremote-cli" ]
