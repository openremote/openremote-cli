Feature: cli

  Scenario: CLI basic usage
    When calling openremote-cli without arguments
    Then it should show help
    When calling openremote-cli -V
    Then should show version

  Scenario: configure AWS access keys
    Given we have aws installed
    When we call openremote-cli configure-aws --id <id> --secret <secret> -d -v
    Then aws configure set profile.openremote-cli.aws_access_key_id <id>
    Then aws configure set profile.openremote-cli.aws_secret_access_key <secret>
    Then aws configure set profile.openremote-cli.region eu-west-1
    # And ssh-keygen -f openremote -t rsa -b 4096  -C "me@privacy.net"
    # And aws ec2 import-key-pair --key-name openremote --public-key-material fileb://openremote.pub
    # And aws ec2 create-default-vpc --profile mvp

    Scenario: check and install missing tools
      When or perquisites -v --dry-run
      Then check if all required tools are installed
      When or perquisites --install -v --dry-run
      Then install all missing tools
