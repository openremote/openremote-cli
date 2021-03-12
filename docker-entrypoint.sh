#!/bin/bash
set -eou pipefail

exec /usr/local/bin/openremote-cli $@
exit $?
