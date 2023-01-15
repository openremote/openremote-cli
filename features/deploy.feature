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
    When or deploy --provider aws with default password
    Then generate password and email it to support

  #@skip
  Scenario: deploy to localhost
    Given we have docker and docker-compose installed
    When we call openremote-cli --dry-run deploy --action create
    Then show what will be done
    When we call or --dry-run deploy
    Then show what will be done

  Scenario: deploy to localhost with custom dns name
    Given we have docker and docker-compose installed
    When we call openremote-cli -n deploy --dnsname xxx.yyy.com
    Then show what will be done with dns

  Scenario: deploy with e-mail
    When we call or deploy --with-email
    Then generate SMTP credentials

  Scenario: remove and clean deployment
    Given we have docker and docker-compose installed
    When call openremote-cli deploy --action remove --dry-run
    Then see that the stack is removed
    When call openremote-cli deploy --action clean --dry-run
    Then remove volumes images and prune docker system

  Scenario: deploy using deployments repo and S3
    Given we have AWS profile openremote-cli
    When call or deploy --provider rich --dnsname rich -v -n -t
    Then fetch data from S3 (map is optional)
    And deploy with on localhost with DNS rich.openremote.io

  Scenario: on successful deployment store password in config.ini
    When or deploy --dnsname xxx.yyy.com --password xyz --dry-run -t
    Then or sso --show --dnsname xxx.yyy.com -t contains password xyz
