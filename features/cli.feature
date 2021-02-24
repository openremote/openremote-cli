Feature: cli

  Scenario: CLI basic usage
    When calling openremote-cli without arguments
    Then it should show help
  #Scenario: run -v without command
    When calling openremote-cli -V
    Then should show version
