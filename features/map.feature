Feature: map

  Scenario: manage maps
    Given we have aws profile openremote-cli
    When we call openremote-cli map -a upload -f file
    Then we see s3 cp command
    When we call openremote-cli map -a list
    Then we see s3 ls command
    When we call openremote-cli map -a download -f file
    Then we see s3 cp command
    When we call openremote-cli map -a delete -f file
    Then we see s3 rm command
