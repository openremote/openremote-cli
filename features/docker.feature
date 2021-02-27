Feature: docker

Scenario:
  Given we have docker installed
  When docker run --rm -ti openremote/openremote-cli -V
  Then there should be openremote-cli version response
