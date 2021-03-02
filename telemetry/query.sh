aws dynamodb query --table-name openremote-cli-telemetry --key-condition-expression "#d=:d" --profile developers --expression-attribute-values "{\":d\":{\"S\":\"$1\"}}" --expression-attribute-names '{"#d":"date"}' --index-name date-index
