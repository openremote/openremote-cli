FROM python:3.9-slim
#FROM python

RUN apt update && apt install curl unzip -y && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

RUN pip install openremote-cli

ENTRYPOINT [ "/usr/local/bin/openremote-cli" ]
