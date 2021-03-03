'use strict';

const { OK, NOT_FOUND } = require('http-status')
const AWSXRay = require('aws-xray-sdk-core')
const AWS = AWSXRay.captureAWS(require('aws-sdk'))
const docClient = new AWS.DynamoDB.DocumentClient({ apiVersion: '2012-08-10' })
const { errCatching, okResponse, redirectResponse, isEmpty } = require('./functions.js')
const fetch = require("node-fetch");
const { RemoteCredentials } = require('aws-sdk');

module.exports.metrics = async event => {
  console.log(JSON.stringify(event))
  try {
    var body = JSON.parse(event.body);
    // TODO validate body

    let record = {}
    record.ip = event.requestContext.identity.sourceIp
    record.user_id = body.metrics[0].userId
    record.timestamp = new Date().toISOString()
      .replace(/T/, ' ')       // replace T with a space
      .replace(/\..+/, '')     // delete the dot and everything after
    record.command = body.metrics[0].command.input
    record.exit_code = body.metrics[0].command.exitCode
    record.os_platform = body.metrics[0].osPlatform
    record.os_version = body.metrics[0].osVersion
    record.metric = body.metrics[0]
    record.date = record.timestamp.substr(0, 10) // get only date for partitioning

    const params = {
      TableName: process.env.DDB_TELEMETRY,
      Item: record
    }
    await docClient.put(params)
      .promise()
      .then(d => console.log(process.env.DDB_TELEMETRY, " inserted ", JSON.stringify(record)))
      .catch(e => { throw (e) });
    return okResponse()
  }
  catch (err) {
    return errCatching(body);
  }
}

module.exports.geoip = async event => {
  console.log(JSON.stringify(event))

  for (let val of event.Records) {

    let record = val.dynamodb.NewImage

    if (record) { // Because we don't want react to REMOVE
      let tableName = val.eventSourceARN.match(/table\/(.+)\/stream/i)[1]
      console.log("table:", tableName)
      let keys = AWS.DynamoDB.Converter.unmarshall(val.dynamodb.Keys)
      console.log(keys)

      if (record.ip.S) {
        console.log("pure IP", record.ip.S)
        let jsonIp = {}
        // Decode IP through freegeoip API
        await fetch("https://freegeoip.app/json/" + record.ip.S)
          .then(response => {
            return response.json()
          })
          .then(json => {
            console.log(JSON.stringify(json))
            jsonIp = json
          })
          .catch(error => {
            console.error("Error: " + error);
            throw error
          });

        await docClient.update({
          TableName: tableName,
          Key: keys,
          UpdateExpression: 'set ip = :val, market = :country',
          ExpressionAttributeValues: {
            ':val': jsonIp,
            ':country': jsonIp.country_code
          }
        })
          .promise()
          .then(console.log("IP record updated to", jsonIp))
          .catch(console.error)
      } else {
        console.log("rich IP", record.ip)
      }
    }
  }
}
