Feature: deploy

  Scenario: deploy to localhost
    Given we have docker and docker-compose and wget installed
    When we call openremote-cli --dry-run deploy --action create
    Then show what will be done

  Scenario: default should deploy to localhost
    When we call or --dry-run deploy
    Then show what will be done
