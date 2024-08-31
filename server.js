"use strict";

import dotenv from "dotenv";
import express from "express";
import fs from "fs";

import { removeMediaPathSync } from "./auth/auth.js";
import config from "./utilities/config.js";
import logger from "./utilities/logger.js";
import { updateMetaInfo } from "./utilities/metadata.js";
import projectDir from "./utilities/project_dir.js";
import { ExitCodes, shutdown } from "./utilities/shutdown.js";
import { publicIpv4 } from "public-ip";

import middleware from "./middleware/middleware.js";

import authRoutes from "./routes/auth_routes.js";
import mangaRoutes from "./routes/manga_routes.js";
import videoRoutes from "./routes/video_routes.js";

/*******************************************************************************
 * Initialize any server variables.
 ******************************************************************************/

// Load the .secrets.env data
// They can now be accessed from `process.env.${...}`
dotenv.config({
  path: ".env",
});
dotenv.config({
  path: ".secrets.env",
});

/*******************************************************************************
 * Middleware
 ******************************************************************************/
var app = express();
app.use(middleware.crossOriginRequests);
app.use(middleware.bodyParserUrlEncoded);
app.use(middleware.bodyParserJson);
app.use(middleware.logIP);
app.use(middleware.trafficLogger);
app.use(middleware.verifyAuth);
app.use("/public", express.static(`${projectDir}/public`));
app.use(middleware.blacklist);
app.use(middleware.rateLimit);

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
// REMOVED because this causes issues if the client is in the middle of
// accessing media when we restart. Consider a better way to manage this
// removeMediaPathSync();

// Check to see if a password is on file
// If not, then we can not operate, shutdown.
if (!fs.existsSync("./.pwd_hash")) {
  console.error(
    "No password hash found, please create one with scripts/create_password.py."
  );
  shutdown(null, ExitCodes.ADMIN_ERROR);
}

/**
 *  @brief  Callback for the timer that checks for updates to the media.
 */
function checkForMediaUpdates() {
  updateMetaInfo();
  setTimeout(checkForMediaUpdates, config.server.MediaUpdateIntervalMs);
}

// Begin MetaData Updates Polling
checkForMediaUpdates();

/*******************************************************************************
 * Start Application
 ******************************************************************************/

// Start listening
var server = app.listen(process.env.REACT_APP_SERVER_PORT, async function () {
  // Log the server start, using the public IP address
  publicIpv4().then((ip) => {
    logger.info(`App listening at http://${ip}:${server.address().port}`);
  });
});
