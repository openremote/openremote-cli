Feature: deploy

  Scenario: check health of running stack
    Given we have running openremote stack on a dnsname
    When or deploy -a health --dnsname demo.openremote.io
    Then we get 0/1 health status
    When or deploy -a health --dnsname demo.openremote.io -v
    Then we get more info
    When or deploy -a health --dnsname demo.openremote.io -vv
    Then we get full health response

  Scenario: deploy to AWS
    Given we have aws profile openremote-cli
    When call or deploy --provider aws -d -v --no-telemetry
    Then download CloudFormation template from github
    And  execute AWS CloudFormation
    When call or deploy -a remove aws -d -v --no-telemetry
    Then delete the proper cloudformation stack

  Scenario: deploy to localhost
    Given we have docker and docker-compose installed
    When we call openremote-cli --dry-run deploy --action create
    Then show what will be done
    When we call or --dry-run deploy
    Then show what will be done

  Scenario: deploy with e-mail
    When we call or deploy --with-email
    Then generate SMTP credentials

  Scenario: remove and clean deployment
    Given we have docker and docker-compose installed
    When call openremote-cli deploy --action remove --dry-run
    Then see that the stack is removed
    When call openremote-cli deploy --action clean --dry-run
    Then remove volumes images and prune docker system
