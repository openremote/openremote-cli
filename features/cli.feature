Feature: cli

  Scenario: run -v without command
    When calling openremote-cli -v
    Then should be the same as openremote-cli
