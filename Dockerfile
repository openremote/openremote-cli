FROM python:3.9-slim

RUN apt update && apt install curl unzip wget -y
RUN    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN    unzip awscliv2.zip
RUN    ./aws/install

RUN pip install openremote-cli

ENTRYPOINT [ "/usr/local/bin/openremote-cli" ]
