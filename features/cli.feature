Feature: cli

  Scenario: CLI basic usage
    When calling openremote-cli without arguments
    Then it should show help
  #Scenario: run -v without command
    When calling openremote-cli -V
    Then should show version

  #Scenario: use common argument after command
    When calling openremote-cil deploy -d
    Then should be the same as openremote-cli --dry-run deploy
