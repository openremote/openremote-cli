![CI/CD](https://github.com/openremote/openremote-cli/workflows/CI/CD/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub license](https://img.shields.io/github/license/openremote/openremote-cli.svg)](https://github.com/openremote/openremote-cli/blob/main/LICENSE.txt)
[![Open Source? Yes!](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)](https://github.com/Naereen/badges/)


# OpenRemote CLI

## Intro

This is Command Line Interface to OpenRemote IoT platform. It's purpose is to reduce friction of using OpenRemote by Do It Yourself users.

## About OR

OpenRemote is a great real OpenSource IoT platform.

## Usage

To install/upgrade the CLI:
```bash
python3 -m pip install --upgrade openremote-cli
or --version
```

### Deploy local OpenRemote stack

```bash
or deploy --action create
```

### Remove local OpenRemote stack

```bash
or deploy --action remove
```

### Deploy OpenRemote stack on AWS with DNS entry (TODO)

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
- make

### Adding feature

In this project we use Behavior-driven development (or BDD). BDD is an agile
software development technique that encourages collaboration between developers,
QA and non-technical or business participants in a software project.

This project uses Gherkin to define what features which should be covered. Features
files can be generated by people on manager level or even higher. An example
of file defining a feature:

```gherkin
Feature: deploy

  Scenario: deploy to localhost
    Given we have docker and docker-compose installed
    When we call openremote-cli --dry-run deploy --action create
    Then show what will be done
```

When the feature is implemented it can be checked with behave:

```bash
> behave
Feature: deploy # features/deploy.feature:1

  Scenario: deploy to localhost                                  # features/deploy.feature:3
    Given we have docker and docker-compose installed            # features/steps/deploy_steps.py:8
Docker version 19.03.13, build 4484c46d9d
    Given we have docker and docker-compose installed            # features/steps/deploy_steps.py:8 0.499s
    When we call openremote-cli --dry-run deploy --action create # features/steps/deploy_steps.py:14 0.593s
    Then show what will be done                                  # features/steps/deploy_steps.py:22 0.000s

1 feature passed, 0 failed, 0 skipped
1 scenario passed, 0 failed, 0 skipped
3 steps passed, 0 failed, 0 skipped, 0 undefined
Took 0m1.092s
```
