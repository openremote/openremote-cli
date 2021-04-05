FROM python:3.6-slim

RUN apt update && apt install curl unzip -y --no-install-recommends && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm awscliv2.zip

# Install Docker client for deploy
RUN curl -sSL https://get.docker.com/ | sh

# Instal docker-compose
RUN curl -L "https://github.com/docker/compose/releases/download/1.28.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Install Chrome for Selenium and chromedriver for Selenium
RUN curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /chrome.deb && \
    dpkg -i /chrome.deb || apt-get install -yf && \
    rm /chrome.deb && \
    curl https://chromedriver.storage.googleapis.com/2.31/chromedriver_linux64.zip -o /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver

RUN pip install openremote-cli
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT [ "/docker-entrypoint.sh" ]
