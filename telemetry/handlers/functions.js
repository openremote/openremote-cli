const status = require('http-status');
const { BAD_REQUEST, OK, MOVED_PERMANENTLY } = require('http-status');

module.exports.errCatching = function (err) {
  console.error("Catching ERROR: ", err);
  let statusCode = BAD_REQUEST;
  if (typeof (err) === 'number') {
    statusCode = err;
    err = undefined
  }
  return {
    statusCode: statusCode,
    body: JSON.stringify(
      {
        status: status[statusCode],
        body: err,
      },
      null,
      2
    ),
  };
}

module.exports.okResponse = function (body) {
  return {
    statusCode: OK,
    body: JSON.stringify(
      {
        status: status[OK],
        body: body
      },
      null,
      2
    ),
  }
}

module.exports.redirectResponse = function (location) {
  return {
    statusCode: MOVED_PERMANENTLY,
    headers: {
      "Location": location
    },
    body: JSON.stringify(
      {
        status: status[MOVED_PERMANENTLY]
      },
      null,
      2
    ),
  };
}

module.exports.isEmpty = function (obj) {

  // null and undefined are "empty"
  if (obj == null) return true;

  // Assume if it has a length property with a non-zero value
  // that that property is correct.
  if (obj.length > 0) return false;
  if (obj.length === 0) return true;

  // If it isn't an object at this point
  // it is empty, but it can't be anything *but* empty
  // Is it empty?  Depends on your application.
  if (typeof obj !== "object") return true;

  // Otherwise, does it have any properties of its own?
  // Note that this doesn't handle
  // toString and valueOf enumeration bugs in IE < 9
  for (var key in obj) {
    if (hasOwnProperty.call(obj, key)) return false;
  }

  return true;
}
