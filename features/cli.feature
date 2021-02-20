Feature: cli

  Scenario: run -v without command
    When calling openremote-cli -v
    Then should be the same as openremote-cli

  Scenario: use common argument after command
    When calling openremote-cil deploy -d
    Then should be the same as openremote-cli --dry-run deploy
