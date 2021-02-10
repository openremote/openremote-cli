Feature: deploy

  Scenario: deploy to localhost
    Given we have docker and docker-compose installed
    When we call openremote-cli --dry-run deploy --action create
    Then show what will be done
