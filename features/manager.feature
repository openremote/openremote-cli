Feature: manager

  Scenario: login into manager
  When we login into demo.openremote.io with user and password
  Then we can list public assets from master realm
