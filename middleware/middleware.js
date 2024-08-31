import bodyParser from "body-parser";
import cors from "cors";
import dotenv from "dotenv";
import expressRateLimit from "express-rate-limit";
import fs from "fs";

import { createMediaPath, getJWTFromReq, isJWTValid } from "../auth/auth.js";
import config from "../utilities/config.js";
import logger from "../utilities/logger.js";
import { ExitCodes, shutdown } from "../utilities/shutdown.js";

// Load the .secrets.env data
// They can now be accessed from `process.env.${...}`
dotenv.config({
  path: ".env",
});

/** Record of IPs that have made requests to the server
 *   Used to prevent spamming the server with requests
 *   Record includes:
 *    - Timestamp of last request
 *    - count of failures since last successful request
 *    - flag for if the IP has sent us a successful request
 */
var _ipHistory = {};
var _blacklist = new Set();
var _ipv4 = process.env.REACT_APP_SERVER_IP;

/**
 * @brief  Helper function for recording failed login attempts.
 * @param  {String} ip IP address of the request.
 * @note   This function will block the IP if it has failed too many times.
 *         The IP will be blocked by adding it to the blacklist.tsv file.
 *         The blacklist.tsv file is read by the firewall and used to block
 *         incoming connections.
 */
function recordIPFailedAttempt(ip, userAgent = "Unknown") {
  if (!_ipHistory.hasOwnProperty(ip)) {
    _ipHistory[ip] = {
      lastRequest: new Date(),
      failedAttempts: 0,
    };
  }
  _ipHistory[ip] = {
    lastRequest: new Date(),
    failedAttempts: (_ipHistory[ip]["failedAttempts"] ?? 0) + 1,
  };

  // If we have hit the threshold, then block the IP
  // TODO: Make this a config parameter
  const threshold = config.server.LimitFailedLoginAttempts;
  if (threshold <= _ipHistory[ip]["failedAttempts"]) {
    logger.info(`Blocking IP after ${threshold} failed requests: ${ip}`);

    // Add the IP to the blacklist.tsv
    blacklistIP(ip, userAgent);
  }
}

/**
 * @brief  Helper function for recording successful login attempts.
 * @param  {String} ip IP address of the request.
 * @note   If the IP is in the history of recent failures,
 *         then it will be removed from that history.
 */
function recordIPSuccessfulAttempt(ip) {
  _ipHistory[ip] = {
    hasSentValidToken: true,
    lastRequest: new Date(),
    failedAttempts: 0,
  };
}

/**
 * @brief Add a new IP to the blacklist.tsv file.
 * @param {String} ip IP address to add to the blacklist.
 * @param {String} userAgent User agent of the request.
 */
function blacklistIP(ip, userAgent = "Unknown") {
  if (_blacklist.has(ip)) return;
  logger.info(`Blacklisting: ${ip}`);

  // Remove the IP from the history
  delete _ipHistory[ip];

  // Add the IP to the blacklist in memory and write it to the blacklist.tsv
  _blacklist.add(ip);
  fs.appendFile(
    "./blacklist.tsv",
    `${Date()}\t${userAgent}\t${ip}\n`,
    function (err) {
      if (err) logger.error(`Failed to add ${ip} to blacklist.tsv`);
    }
  );
}

/**
 *  Set up the blacklist in a blocking manner so that we don't start the server
 *  until the blacklist is ready.
 */
function initBlacklist() {
  try {
    const data = fs.readFileSync("./blacklist.tsv").toString();

    data.split("\n").forEach((ipRecord) => {
      const cols = ipRecord.split("\t");
      if (cols.length < 3) return;
      const ip = cols[2];
      _blacklist.add(ip);
    });
  } catch (err) {
    logger.error(err);
    shutdown(null, ExitCodes.ADMIN_ERROR);
  }
}

/**
 *  Update the blacklist to the latest version, and continue to do so
 *  on a timer.
 */
function updateBlacklist() {
  fs.readFile("./blacklist.tsv", function (err, data) {
    if (err) {
      logger.error(err);
      shutdown(null, ExitCodes.ADMIN_ERROR);
    }

    const lines = data.toString().split("\n");

    lines.forEach((ipRecord) => {
      const cols = ipRecord.split("\t");
      if (cols.length < 3) return;
      const ip = cols[2];
      _blacklist.add(ip);
    });
  });

  setInterval(updateBlacklist, config.server.BlacklistUpdateIntervalMs);
}

/**
 *  CORS configuration (for react).
 */
const crossOriginRequests = cors({
  origin: `http://${_ipv4}:3000`,
  credentials: true,
  optionsSuccessStatus: 200,
});

/**
 *  Body parser configuration. -- url encoded
 */
const bodyParserUrlEncoded = bodyParser.urlencoded({
  extended: true,
  limit: config.server.MaxRequestSize,
});

/**
 *  Body parser configuration. -- json
 */
const bodyParserJson = bodyParser.json({
  limit: config.server.MaxRequestSize,
});

/**
 * Log all traffic
 */
function trafficLogger(req, res, next) {
  // Break up the request into it's components
  const ip = req.headers.host ?? req.ip;
  const method = req.method;
  const url = req.url;
  const endpoint = (url ?? "").split("?")[0];
  const query = JSON.stringify(req.query);
  const header = req.headers;
  const auth =
    header && header.authorization && header.authorization.length > 25
      ? header.authorization.substring(header.authorization.length - 25)
      : "";

  // Log the request
  logger.info(`${ip} ${method} ${endpoint} ${auth} ${query}`);

  next();
}

/**
 *  Record the IP in the _ipHistory as either a successful or failed attempt.
 *  This is used to detect suspicious behavior.
 */
function logIP(req, res, next) {
  res.on("finish", () => {
    const ip = req.headers.host ?? req.ip;

    if (_ipHistory[ip]?.hasSentValidToken) return;

    // Check to see if the path they are going to is a keyed path
    // If it is, then we will record it as a successful attempt
    const pathElems = req.path ? req.path.split("/") : [];
    if (2 <= pathElems.length && pathElems[1] === "public") {
      const pathKey = pathElems[2];
      if (
        pathKey &&
        0 < pathKey.length &&
        fs.existsSync("./public/" + pathKey)
      ) {
        recordIPSuccessfulAttempt(ip);
        return;
      }
    }

    if (400 <= res.statusCode && res.statusCode < 500) {
      recordIPFailedAttempt(ip, req.get("User-Agent"));
    } else {
      recordIPSuccessfulAttempt(ip);
    }
  });
  next();
}

/**
 *  Blacklist IPs that are in the blacklist.tsv file
 */
function blacklist(req, res, next) {
  // If the IP is in the blacklist, then block the request
  const ip = req.headers.host ?? req.ip;
  if (_blacklist.has(ip)) {
    res.status(403).send("This IP has been blacklisted.");
    return;
  }

  next();
}

/**
 * Prevent callers from spamming the server with requests.
 * This limit specifically applies to IPs that have never sent a valid token.
 */
const rateLimit = expressRateLimit({
  windowMs: config.server.LimitUnauthorizedRequestsWindowMs,
  max: config.server.LimitUnauthorizedRequestsCount,
  handler: function (req, res) {
    const ip = req.headers.host ?? req.ip;

    // If the IP has been recognized as a valid user, then let them through
    if (_ipHistory[ip]?.hasSentValidToken) {
      return;
    }

    // If the user has not sent a valid token, then classify this
    // as suspicious behavior and block the IP.
    // Add the IP to the blacklist.tsv
    blacklistIP(ip, req.get("User-Agent"));

    res
      .status(429)
      .send("Too many requests from this IP. IP has been blacklisted.");
  },
});

/**
 * Filter out unauthorized requests
 * Ensure a media path is present if the request is authorized
 */
function verifyAuth(req, res, next) {
  // There are only two endpoints where we allow unauthorized requests
  // 1. The auth endpoint -- Cuz that's how they get authorized
  // 2. The public endpoint -- It's in the name
  var path = req.path;
  if (path && !path.startsWith("/auth") && !path.startsWith("/public")) {
    // Check the jwt in the authorization header
    const token = getJWTFromReq(req);
    const err = isJWTValid(token);
    if (err.length) {
      res.status(401).send(err);
      return;
    }

    // Ensure that the jwt path is set up
    createMediaPath(token);
  }

  next();
}

initBlacklist();
setInterval(updateBlacklist, config.server.BlacklistUpdateIntervalMs);

export default {
  crossOriginRequests,
  bodyParserUrlEncoded,
  bodyParserJson,
  trafficLogger,
  logIP,
  blacklist,
  rateLimit,
  verifyAuth,
};
