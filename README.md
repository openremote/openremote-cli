# OpenRemote CLI

## Intro

This is Command Line Interface to OpenRemote IoT platform. It's purpose is to reduce friction of using OpenRemote by Do It Yourself users.

## About OR

OpenRemote is a great real OpenSource IoT platform.

## Usage

To install the CLI
```bash
pip install openremote-cli
or --version
```

To update the CLI:
 ```bash
pip install openremote-cli --upgrade
 ```

### Deploy local OpenRemote stack

```bash
or deploy
```

### Deploy OpenRemote stack on AWS with DNS entry

```bash
or deploy --platform aws --hostname myiot.mydomain.com
```

### Install shell completion extension

#### zsh

```bash
TODO
```

#### bash

```
TODO
```

## Configure existing OpenRemote instance

### Add users

### Add assets

### Add customization

## Develop openremote-cli

Following tools are used:
- python
- poetry
- black
- git
- pre-commit
