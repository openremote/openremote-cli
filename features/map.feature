Feature: map

  Scenario: start working with map storage
    Given we have aws installed
    When we call openremote-cli map -a configure --id <id> --secret <secret> -d -v
    Then aws configure set profile.mvp-map-manager.aws_access_key_id <id>
    Then aws configure set profile.mvp-map-manager.aws_secret_access_key <secret>
    Then aws configure set profile.mvp-map-manager.region eu-west-1

  Scenario: manage maps
    Given we have aws profile mvp-map-manager
    When we call openremote-cli map -a upload -f file
    Then we see s3 cp command
    When we call openremote-cli map -a list
    Then we see s3 ls command
    When we call openremote-cli map -a download -f file
    Then we see s3 cp command
    When we call openremote-cli map -a delete -f file
    Then we see s3 rm command
