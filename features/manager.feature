Feature: manager

  Scenario: login into manager and list basic information
  Given we have SETUP_ADMIN_PASSWORD variable set
  When login into demo.openremote.io as admin
  Then a token is fetched stored in config
  And we can list realms
  And we can list users of master realm
  And we can list public assets from master realm

  Scenario: use 'sso' or 'm' alias for manager feature
  When using alias sso for staging.demo.openremote.io
  Then there should be no errors
  When login into demo realm smartcity as user smartcity
  Then there should be no errors

  # Scenario: test http rest
  # When running manager --test-http-test
  # Then there should be no errors
