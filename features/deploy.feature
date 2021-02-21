Feature: deploy

  Scenario: deploy to localhost
    Given we have docker and docker-compose and wget installed
    When we call openremote-cli --dry-run deploy --action create
    Then show what will be done
    When we call or --dry-run deploy
    Then show what will be done

  Scenario: remove and clean deployment
    Given we have docker and docker-compose and wget installed
    When call openremote-cli deploy --action remove --dry-run
    Then see that the stack is removed
    When call openremote-cli deploy --action clean --dry-run
    Then remove volumes images and prune docker system
