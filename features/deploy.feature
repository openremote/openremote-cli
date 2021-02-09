Feature: deploy

  Scenario: deploy to localhost
    Given we have docker and docker-compose installed
    When we call or-cli
    Then show what will be done
    And deploy OpenRemote stack accordingly