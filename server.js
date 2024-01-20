"use strict";

import bodyParser from "body-parser";
import * as child from "child_process";
import cors from "cors";
import dotenv from "dotenv";
import express from "express";
import expressRateLimit from "express-rate-limit";
import fs from "fs";
import { dirname } from "path";
import { fileURLToPath } from "url";

import config from "./utilities/config.js";
import logger from "./utilities/logger.js";
import {
  createMediaPath,
  getJWTFromReq,
  isReqJWTValid,
  removeMediaPathSync,
} from "./auth/auth.js";
import { ExitCodes, shutdown } from "./utilities/shutdown.js";
import { publicIpv4 } from "public-ip";

import authRoutes from "./routes/auth_routes.js";
import mangaRoutes from "./routes/manga_routes.js";
import videoRoutes from "./routes/video_routes.js";

/*******************************************************************************
 * Initialize any server variables.
 ******************************************************************************/

/**
 *  Full path to the server.js file.
 */
const __filename = fileURLToPath(import.meta.url);

/**
 * Full path to the current working directory.
 */
const __dirname = dirname(__filename);

// Load the .secrets.env data
// They can now be accessed from `process.env.${...}`
dotenv.config({
  path: ".secrets.env",
});

/*******************************************************************************
 * Middleware (TODO: Move to separate folder)
 ******************************************************************************/
var app = express();
// CORS config for react
app.use(
  cors({
    origin: "http://localhost:3000",
    credentials: true,
    optionsSuccessStatus: 200,
  })
);
// Create a static path to the public folder
app.use("/public", express.static(`${__dirname}/public`));
// Extend bandwidth from the server
app.use(
  bodyParser.json({
    limit: "500mb",
  })
);
app.use(
  bodyParser.urlencoded({
    // NOTE order matters .json() -> .urlencoded()
    limit: "5mb", // Use this to extend bandwidth to the server
    extended: true,
  })
);
// Log all traffic
app.use(function (req, res, next) {
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
});
// Log requests in the _ipHistory
app.use((req, res, next) => {
  res.on("finish", () => {
    const ip = req.headers.host ?? req.ip;
    if (res.statusCode >= 400) {
      recordIPFailedAttempt(ip, req.get("User-Agent"));
    } else {
      recordIPSuccessfulAttempt(ip);
    }
  });
  next();
});
// Blacklist IPs that are in the blacklist.tsv file
app.use(function (req, res, next) {
  fs.readFile("./blacklist.tsv", function (err, data) {
    if (err) {
      logger.error(err);
      return;
    }

    const blacklist = data.toString().split("\n");
    for (let ipRecord of blacklist) {
      const cols = ipRecord.split("\t");
      if (cols.length < 3) continue;
      const ip = cols[2];
      if (ip === req.headers.host || ip == req.ip) {
        res.status(403).send("This IP has been blacklisted.");
        return;
      }
    }

    next();
  });
});
// This limit specifically applies to IPs that have not sent a valid token.
app.use(
  expressRateLimit({
    //        30 minutes in milliseconds
    windowMs: config.server.LimitUnauthorizedRequestsWindowMs,
    max: config.server.LimitUnauthorizedRequestsCount,
    handler: function (req, res) {
      var ip = req.headers.host ?? req.ip;
      // If the IP has been recognized as a valid user,
      // then let them through
      if (_ipHistory.hasOwnProperty(ip)) {
        if (_ipHistory[ip]["hasSentValidToken"]) {
          return;
        }
      }

      // If the user has not sent a valid token, then classify this
      // as suspicious behavior and block the IP.
      // Add the IP to the blacklist.tsv
      blacklistIP(ip, req.get("User-Agent"));

      res
        .status(429)
        .send("Too many requests from this IP. IP has been blacklisted.");
    },
  })
);
// Filter out unauthorized requests
// Ensure a media path is present if the request is authorized
app.use(function (req, res, next) {
  // There are only two endpoints where we allow unauthorized requests
  // 1. The auth endpoint -- Cuz that's how they get authorized
  // 2. The public endpoint -- It's in the name
  if (req.path.startsWith("/auth") || req.path.startsWith("/public")) {
    next();
    return;
  }

  // Check the jwt in the authorization header
  const err = isReqJWTValid(req);
  if (err.length) {
    res.status(401).send(err);
    return;
  }

  // Ensure that the jwt path is set up
  const token = getJWTFromReq(req);
  createMediaPath(token);

  next();
});

/*******************************************************************************
 * Routes
 ******************************************************************************/
app.use("/auth", authRoutes);
app.use("/manga", mangaRoutes);
app.use("/video", videoRoutes);

/*******************************************************************************
 * Things to do before we start listening.
 ******************************************************************************/

// Remove any old signed folders in the public directory
removeMediaPathSync();

// Check to see if a password is on file
// If not, then we can not operate, shutdown.
if (!fs.existsSync("./.pwd_hash")) {
  logger.error(
    "No password hash found, please create one with scripts/create_password.py."
  );
  shutdown(null, ExitCodes.ADMIN_ERROR);
}

/**
 *  @brief  Callback for the timer that checks for updates to the media.
 */
function checkForMediaUpdates() {
  updateMetaInfo();
  setTimeout(
    checkForMediaUpdates,
    config.server.PollingRateMediaSeconds * 1000
  );
}

// Begin MetaData Updates Polling
checkForMediaUpdates();

/*******************************************************************************
 * Start Application
 ******************************************************************************/

// Start listening
var server = app.listen(config.server.ServerPort, async function () {
  // Log the server start, using the public IP address
  publicIpv4().then((ip) => {
    logger.info(`App listening at http://${ip}:${server.address().port}`);
  });
});

/*******************************************************************************
 * TODO: Organize the following code into modules or sections.
 ******************************************************************************/

// Record of IPs that have made requests to the server
// Used to prevent spamming the server with requests
// Record includes:
//  - Timestamp of last request
//  - count of failures since last successful request
//  - flag for if the IP has sent us a successful request
var _ipHistory = {};

/*
 * Helper Functions
 */

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
  } else {
    _ipHistory[ip]["failedAttempts"]++;
  }

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
  logger.info(`Blacklisting: ${ip}`);

  // Remove the IP from the history
  delete _ipHistory[ip];

  fs.appendFile(
    "./blacklist.tsv",
    `${Date()}\t${userAgent}\t${ip}\n`,
    function (err) {
      if (err) logger.error(`Failed to add ${ip} to blacklist.tsv`);
    }
  );
}

/**
 * Execute simple shell command (async wrapper).
 * @param {String} cmd
 * @return {Object} { stdout: String, stderr: String }
 */
async function sh(cmd) {
  return new Promise(function (resolve, reject) {
    child.exec(cmd, (err, stdout, stderr) => {
      if (err) {
        reject(err);
      } else {
        resolve({ stdout, stderr });
      }
    });
  });
}

/*
 * External Scripts
 */

function updateMetaInfo() {
  logger.info("Updating Manga Metadata...");
  sh(`python3 ${__dirname}/scripts/metadata_dl_manga.py`)
    .then(function (data) {
      if (data.stdout.length) logger.info(data.stdout);
      if (data.stderr.length) logger.error(data.stderr);
    })
    .catch(function (err) {
      logger.error(err);
    });

  logger.info("Updating Video Metadata...");
  sh(`python3 ${__dirname}/scripts/metadata_dl_video.py`)
    .then(function (data) {
      if (data.stdout.length) logger.info(data.stdout);
      if (data.stderr.length) logger.error(data.stderr);
    })
    .catch(function (err) {
      logger.error(err);
    });
}
