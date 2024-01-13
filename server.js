"use strict";

import parseAss from "ass-parser";
import bcrypt from "bcrypt";
import bodyParser from "body-parser";
import * as child from "child_process";
import { create } from "domain";
import dotenv from "dotenv";
import express from "express";
import expressRateLimit from "express-rate-limit";
import fs from "fs";
import ini from "ini";
import jwt from "jsonwebtoken";
import * as mongodb from "mongodb";
import { dirname } from "path";
import srtParser2 from "srt-parser-2";
import { fileURLToPath } from "url";
import cors from "cors";

// Define a list of error codes the server can close with
const ErrorCodes = {
  SUCCESS: 0,
  UNKNOWN: -1,
  CONFIG_ERROR: -2,
  ENV_ERROR: -3,
};

// Load the .secrets.env data
dotenv.config({
  path: ".secrets.env",
});

// Load in config data
// Ensure config has all required parameters,
// including those needed by sub scripts
const config = ini.parse(fs.readFileSync("./config.ini", "utf-8"));
if (!validateConfig()) {
  shutdown(ErrorCodes.CONFIG_ERROR);
}

// Overload the console log to log with timestamps
var log = console.log;
console.log = function () {
  var first_parameter = arguments[0];
  var other_parameters = Array.prototype.slice.call(arguments, 1);

  function formatConsoleDate(date) {
    var hour = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();
    var milliseconds = date.getMilliseconds();

    return (
      "[" +
      (hour < 10 ? "0" + hour : hour) +
      ":" +
      (minutes < 10 ? "0" + minutes : minutes) +
      ":" +
      (seconds < 10 ? "0" + seconds : seconds) +
      "." +
      ("00" + milliseconds).slice(-3) +
      "] "
    );
  }

  log.apply(
    console,
    [formatConsoleDate(new Date()) + first_parameter].concat(other_parameters)
  );
};
var error = console.error;
console.error = function () {
  var first_parameter = arguments[0];
  var other_parameters = Array.prototype.slice.call(arguments, 1);

  function formatConsoleDate(date) {
    var hour = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();
    var milliseconds = date.getMilliseconds();

    return (
      "[" +
      (hour < 10 ? "0" + hour : hour) +
      ":" +
      (minutes < 10 ? "0" + minutes : minutes) +
      ":" +
      (seconds < 10 ? "0" + seconds : seconds) +
      "." +
      ("00" + milliseconds).slice(-3) +
      "] "
    );
  }

  log.apply(
    error,
    [formatConsoleDate(new Date()) + first_parameter].concat(other_parameters)
  );
};

/*
 * Express Configurations
 */
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
var app = express();
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
// CORS config for react
app.use(
  cors({
    origin: "http://localhost:3000",
    credentials: true,
    optionsSuccessStatus: 200,
  })
);
// Blacklist IPs that are in the blacklist.tsv file
app.use(function (req, res, next) {
  fs.readFile("./blacklist.tsv", function (err, data) {
    if (err) {
      console.error(err);
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

// Start listening
var server = app.listen(config.server.ServerPort, async function () {
  let address = server.address();
  let { stdout } = await sh("curl ifconfig.me");
  console.log(`App listening at http://${stdout}:${address.port}`);

  // Start the server
  init();
});

/**
 * Schema as follows:
 * ```
 * {
 *     manga: {
 *         title0: {
 *             chapters: {
 *                 ch1: ["pg1", "pg2", ...],
 *                 ...
 *             },
 *             titlePath: "path/to/title0",
 *             isGood: false/true,
 *         },
 *         ...
 *     }
 *     video: {
 *         title0: {
 *             episodes: ["ep0", "ep1", ...],
 *             titlePath: "path/to/title0",
 *             isGood: false/true,
 *         }
 *     subtitles: {
 *         title0: {
 *             subtitleMap: {
 *                 ep0: ["ep0.Eng.srt", ...],
 *                 ep1: ["ep1.Eng.srt", ...],
 *                 ...
 *             },
 *             titlePath: "path/to/title0",
 *             isGood: false/true,
 *         }
 *     }
 *     ...
 * }
 * ```
 */
var _mediaFSIndex = {
  manga: {},
  video: {},
  music: {},
  subtitles: {},
};

var _mediaCollectionIndex = {
  manga: { index: {}, isGood: false },
  video: { index: {}, isGood: false },
  music: { index: {}, isGood: false },
};

// Record of IPs that have made requests to the server
// Used to prevent spamming the server with requests
// Record includes:
//  - Timestamp of last request
//  - count of failures since last successful request
//  - flag for if the IP has sent us a successful request
var _ipHistory = {};

var db_client;

/*
 * Helper Functions
 */

/**
 * @brief  Helper function for converting a jwt token into a folder name.
 * @param {String} token jwt token of the client.
 * @returns {String} An OS friendly name based on the JWT.
 */
function convertTokenToFolderName(token) {
  if (token.length < 25) return token;
  return token.substring(token.length - 25);
}

/**
 * @brief  Helper function for checking if the media path is set for the client.
 * @param {String} token jwt token of the client.
 */
function isMediaPathSet(token) {
  let tokenShort = convertTokenToFolderName(token);

  return fs.existsSync(`./public/${tokenShort}`);
}

/**
 * @brief  Helper function for creating the media path for the client.
 * @param {String} token jwt token of the client.
 */
function createMediaPath(token) {
  let tokenShort = convertTokenToFolderName(token);

  // Make the obscured folder
  fs.mkdirSync(`./public/${tokenShort}`);

  let folderList = [
    ["manga", config.folders.FolderManga],
    ["video", config.folders.FolderVideo],
    ["music", config.folders.FolderMusic],
    ["image", config.folders.FolderImage],
    ["subtitles", config.folders.FolderSubtitles],
    ["lux-assets", config.folders.FolderLuxAssets],
  ];

  // Crete symbolic links to the media folders
  for (let folder of folderList) {
    fs.symlinkSync(
      folder[1],
      `./public/${tokenShort}/${folder[0]}`,
      "junction"
    );
  }
}

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
    console.log(`Blocking IP after ${threshold} failed requests: ${ip}`);

    // Add the IP to the blacklist.tsv
    blacklistIP(ip, userAgent);

    // Remove the IP from the history
    delete _ipHistory[ip];
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
  fs.appendFile(
    "./blacklist.tsv",
    `${Date()}\t${userAgent}\t${ip}\n`,
    function (err) {
      if (err) console.error(`Failed to add ${ip} to blacklist.tsv`);
    }
  );
}

/**
 *  @brief  Handle the shutdown of the server.
 */
function shutdown(statusCode = ErrorCodes.SUCCESS) {
  console.log("Shutting down the server...");
  server.close(() => {
    console.log("Server has been gracefully closed.");
    process.exit(statusCode);
  });
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
  console.log("Updating Manga Metadata...");
  sh(`python3 ${__dirname}/scripts/metadata_dl_manga.py`)
    .then(function (data) {
      if (data.stdout.length) console.log(data.stdout);
      if (data.stderr.length) console.error(data.stderr);
    })
    .catch(function (err) {
      console.error(err);
    });

  console.log("Updating Video Metadata...");
  sh(`python3 ${__dirname}/scripts/metadata_dl_video.py`)
    .then(function (data) {
      if (data.stdout.length) console.log(data.stdout);
      if (data.stderr.length) console.error(data.stderr);
    })
    .catch(function (err) {
      console.error(err);
    });

  updateMediaCollectionIndex();

  updateMediaFilesystemIndex();
}

/*
 * Database Functions
 */

async function getDBConnection() {
  try {
    await db_client.connect();
    console.log("Connected to MongoDB");
    return db_client;
  } catch (error) {
    console.error("Error connecting to MongoDB", error);
    return null;
  }
}

async function dbDisconnect() {
  try {
    await db_client.close();
    console.log("Closed MongoDB connection");
    return true;
  } catch (error) {
    console.error("Error closing MongoDB connection", error);
    return false;
  }
}

/*
 * Initialization Functions
 */

/**
 *  @brief Helper method for making sure that the required configuration
 *         fields are present in the config file.
 *  @returns True if all required fields are present, false otherwise.
 */
function validateConfig() {
  let missing_header = false;
  let missing_params = false;

  ////////////////////////////////////////////////////////////////
  // Server paramaters
  ////////////////////////////////////////////////////////////////
  if (config.server == undefined) {
    console.error("config.ini Is missing the server header.");
    missing_header = true;
  } else {
    let required_params = [
      "PollingRateMetadataUpdatesSeconds",
      "DbAddress",
      "ServerPort",
      "LimitFailedLoginAttempts",
      "LimitUnauthorizedRequestsWindowMs",
      "LimitUnauthorizedRequestsCount",
    ];
    for (let param of required_params) {
      if (config.server[param] == undefined) {
        console.error(`config.ini [server] Is missing the ${param} parameter.`);
        missing_params = true;
      }
    }
  }

  ////////////////////////////////////////////////////////////////
  // Folders paramaters
  ////////////////////////////////////////////////////////////////
  if (config.folders == undefined) {
    console.error("config.ini Is missing the folders header.");
    missing_header = true;
  } else {
    let required_params = [
      "FolderManga",
      "FolderVideo",
      "FolderMusic",
      "FolderImage",
      "FolderSubtitles",
      "FolderLuxAssets",
      "ThumbnailCacheVideo",
      "ThumbnailCacheMusic",
      "ThumbnailCacheManga",
      "CoverArtCacheVideo",
      "CoverArtCacheMusic",
      "CoverArtCacheManga",
    ];
    for (let param of required_params) {
      if (config.folders[param] == undefined) {
        console.error(
          `config.ini [folders] Is missing the ${param} parameter.`
        );
        missing_params = true;
      }
    }
  }

  ////////////////////////////////////////////////////////////////
  // WebScraping parameters
  ////////////////////////////////////////////////////////////////
  if (config.webscraping == undefined) {
    console.error("config.ini Is missing the webscraping header.");
    missing_header = true;
  } else {
    let required_params = [
      "RequiredMetadataVideo",
      "RequiredMetadataManga",
      "UserAgent",
    ];
    for (let param of required_params) {
      if (config.webscraping[param] == undefined) {
        console.error(
          `config.ini [webscraping] Is missing the ${param} parameter.`
        );
        missing_params = true;
      }
    }
  }

  return !missing_header && !missing_params;
}

/**
 *  @brief Helper method for making sure that the required environment
 *        variables are present.
 *        Randomly generate tokens and save them for later.
 */
function setupEnv() {
  if (
    process.env.JWT_SECRET == undefined ||
    process.env.PASSWORD_PEPPER == undefined
  ) {
    console.log("Generating new secrets...");
    const str_out =
      `JWT_SECRET=${bcrypt.genSaltSync(10)}\n` +
      `PASSWORD_PEPPER=${bcrypt.genSaltSync(10)}`;
    fs.writeFileSync(".secrets.env", str_out);

    // Reload the .env file
    dotenv.config();
  }
}

/**
 *  @brief  Callback for the timer that checks for updates to the metadata.
 */
function polling() {
  updateMetaInfo();

  setTimeout(polling, config.server.PollingRateMetadataUpdatesSeconds * 1000);
}

/**
 *  @brief  Initialize the server.
 */
async function init() {
  // Ensure environment variables are set
  // If they are already set, then this does nothing.
  setupEnv();

  // Remove any old signed folders in the public directory
  var folders = fs.readdirSync("./public");
  for (let folder of folders) {
    if (folder == "assets") continue;
    var files = fs.readdirSync(`./public/${folder}`);
    for (let file of files) {
      fs.rmSync(`./public/${folder}/${file}`);
    }
    fs.rmdirSync(`./public/${folder}`);
  }

  // Check to see if a password is on file
  // If not, then prompt the user to set one.
  // Use create_password.py to do this.
  if (!fs.existsSync("./.pwd_hash")) {
    console.log("No password hash found, creating one now.");
    await sh(`python3 ${__dirname}/scripts/create_password.py`);
  }

  // Connect to DB
  // (Must go second!)
  try {
    db_client = new mongodb.MongoClient(config.server.DbAddress, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });

    console.log("DB is online.");
  } catch (err) {
    console.error("Failed to connect to DB.");
  }

  // Begin MetaData Udpates Polling
  polling();
}

/**
 *  @brief  Initialize the server index of available media.
 */
async function updateMediaCollectionIndex() {
  console.log("Updating Collection Index...");

  const db = await getDBConnection();

  const db_media = db.db("mediaMetadata");

  // Manga Index
  try {
    const docs_manga = await db_media.collection("manga").find({}).toArray();

    var index = {};
    for (let doc of docs_manga) {
      var data = {
        title: doc["title"],
        nsfw: doc["nsfw"],
        author: doc["author"],
        dateAdded: doc["dateAdded"],
      };

      // If the title is not on file, discard this record
      if (!fs.existsSync(`${config.folders.FolderManga}/${data["title"]}`)) {
        continue;
      }

      // If the cover_addr is still empty, then store the icon_addr
      if (!fs.existsSync(data["cover_addr"])) {
        data["cover_addr"] = data["icon_addr"];
      }

      index[doc["title"]] = data;
    }
    _mediaCollectionIndex["manga"] = { index: index, isGood: true };
  } catch (err) {
    console.error(err);
    console.error("Failed to update the Manga index.");

    // Flag the data as invalid.
    _mediaCollectionIndex["manga"]["isGood"] = false;
  }

  // Video Index
  try {
    const docs_video = await db_media.collection("video").find({}).toArray();

    var index = {};
    for (let doc of docs_video) {
      var data = {
        title: doc["title"],
        nsfw: doc["nsfw"],
        dateAdded: doc["dateAdded"],
        yearstart: doc["yearstart"],
      };

      // If the title is not on file, discard this record
      if (!fs.existsSync(`${config.folders.FolderVideo}/${data["title"]}`)) {
        continue;
      }

      // If the cover_addr is still empty, then store the icon_addr
      if (!fs.existsSync(data["cover_addr"])) {
        data["cover_addr"] = data["icon_addr"];
      }

      index[doc["title"]] = data;
    }
    _mediaCollectionIndex["video"] = { index: index, isGood: true };
  } catch (err) {
    console.error(err);
    console.error("Failed to update the Video index.");

    // Flag the data as invalid.
    _mediaCollectionIndex["video"]["isGood"] = false;
  }

  // Close the DB
  dbDisconnect();

  // Music Index
  /// NOTE: This is still done using File location, music is not in DB yet
  fs.readdir(config.folders.FolderMusic, function (err, files) {
    if (err) {
      console.error(err);
      console.error("Failed to update media index.");

      // Flag the data as invalid.
      _mediaCollectionIndex["music"]["isGood"] = false;
      return;
    }

    var index = {};
    for (let title of files) {
      index[title] = {
        title: title,
      };
    }
    _mediaCollectionIndex["music"] = { index: index, isGood: true };
  });
}

/**
 * Utility method for interperting the encoded information
 * in the subtitle file names.
 * @param {String} subtitle_file Filename of the subtitles file.
 * @returns The filename broken into it's 3 components:
 * ```
 * "Show X Episode 1.Eng.srt" -> {
 *      episodeName: "Show X Episode 1",
 *      trackKey: "Eng",
 *      encoding: "srt",
 *  }
 *  ```
 */
function splitSubtitleFile(subtitle_file) {
  let eles = subtitle_file.split(".");
  if (eles.length < 3) return "";
  return {
    episodeName: eles.slice(0, eles.length - 2).join("."),
    trackKey: eles[eles.length - 2],
    encoding: eles[eles.length - 1],
  };
}

/**
 *  @brief  Initialize the server index of available media.
 */
function updateMediaFilesystemIndex() {
  console.log("Updating Filesystem Index...");

  // MANGA INDEX
  // Loop through all titles in the manga directory
  fs.readdir(config.folders.FolderManga, function (err_title, titles) {
    if (err_title) {
      console.error(err_title);
      return;
    }
    for (let title of titles) {
      const titleDir = config.folders.FolderManga + title;

      // For each title get the list of chapters,
      // and for each of those chapters get a list of pages.
      // That completes an index for this title,
      // store that index and continue to the next title
      var titleData = { chapters: {}, isGood: true };
      try {
        var chapters = {};
        for (let chapter of fs.readdirSync(titleDir)) {
          const pages = fs.readdirSync(`${titleDir}/${chapter}`);
          chapters[chapter] = pages;
        }
        titleData["chapters"] = chapters;
      } catch (err) {
        console.error(err);
        titleData["isGood"] = false;
      }

      _mediaFSIndex["manga"][title] = titleData;
    }
  });

  // VIDEO INDEX
  // Loop through all titles in the video directory
  fs.readdir(config.folders.FolderVideo, function (err_title, titles) {
    if (err_title) {
      console.error(err_title);
      return;
    }
    for (let title of titles) {
      const titleDir = config.folders.FolderVideo + title;

      // For each title get the list of episodes,
      // That list is the index
      // Store that index and continue to the next title
      var titleData = { episodes: [], isGood: true };
      try {
        const episodes = fs.readdirSync(titleDir);
        titleData["episodes"] = episodes;
      } catch (err) {
        console.error(err);
        titleData["isGood"] = false;
      }

      _mediaFSIndex["video"][title] = titleData;
    }
  });

  // SUBTITLES INDEX
  // Loop through all subtitles and build a map that can be referenced by
  // [title][episode] -> Subtitle file
  fs.readdir(config.folders.FolderSubtitles, function (err_title, titles) {
    if (err_title) {
      console.error(err_title);
      return;
    }
    for (let title of titles) {
      const titleDir = config.folders.FolderSubtitles + title;

      // For each title loop through each subtitle file in the folder
      // Collect all subtitles for each episode in a subtitleMap,
      // keyed by episode. Store said map by title.
      var titleData = { subtitleMap: {}, titlePath: titleDir, isGood: true };
      try {
        for (let subtitle_file of fs.readdirSync(titleDir)) {
          let { episodeName } = splitSubtitleFile(subtitle_file);

          //
          if (!titleData["subtitleMap"][episodeName]) {
            titleData["subtitleMap"][episodeName] = [];
          }
          titleData["subtitleMap"][episodeName].push(subtitle_file);
        }
      } catch (err) {
        console.error(err);
        titleData["isGood"] = false;
      }

      _mediaFSIndex["subtitles"][title] = titleData;
    }
  });

  // Music Index
  // TODO:
}

async function queryDbByTitle(titles_str, dbname, filter_db_privates, res) {
  const titles_req = new Set(titles_str.split(","));

  // Get DB connection
  const db = await getDBConnection();
  const db_media = db.db("mediaMetadata");

  // Query the DB
  // If just quering a single title, find with query filter
  // If many, then findall -> filter
  // NOTE: DB collection is on the order of <1MB
  // Single Document Query
  if (titles_req.size == 1) {
    const title = titles_str;
    try {
      const docs = await db_media
        .collection(dbname)
        .find({ title: title })
        .toArray();

      // Error Handling
      if (docs.length < 1) {
        dbDisconnect();
        res.status(404).send(`No such media on file: ${title}.`);
        return;
      }

      // Remove any private db info before returning the document.
      let metadata = docs[0];
      filter_db_privates(metadata);
      try {
        metadata["cover_addr"] =
          _mediaCollectionIndex[dbname]["index"][title]["cover_addr"];
      } catch (err) {
        console.error(err);
      }

      dbDisconnect();
      res.status(207).send([{ data: metadata, status: 200 }]);
      return;
    } catch (error) {
      dbDisconnect();
      console.error(error);
      res.status(500).send("Failure to query database.");
      return;
    }
  }
  // Many title query
  else {
    try {
      const docs = await db_media.collection(dbname).find({}).toArray();

      var metadata_list = [];

      // Loop through all docs in DB and extract the ones who's
      // title match one of the titles requested
      var titles_found = new Set();
      for (let doc of docs) {
        const title = doc["title"];
        if (titles_req.has(title)) {
          titles_found.add(title);

          // Filter private DB info and add to list
          filter_db_privates(doc);
          try {
            doc["cover_addr"] =
              _mediaCollectionIndex[dbname]["index"][title]["cover_addr"];
          } catch (err) {
            console.error(err);
          }
          metadata_list.push({ data: doc, status: 200 });
        }
      }

      // Error checking
      // If ALL titles are missing return a 404
      if (titles_found.size == 0) {
        dbDisconnect();
        res
          .status(404)
          .send(`None of the requested ${dbname}s could be found.`);
        return;
      }

      // If some titles are missing throw them in the list as failures
      if (titles_found.size != titles_req.size) {
        const missing_titles = new Set(
          [...titles_req].filter((element) => !titles_found.has(element))
        );
        for (let missing_title of missing_titles) {
          metadata_list.push({
            data: { title: missing_title },
            status: 404,
            message: `\"${missing_title}\" not found in ${dbname} database.`,
          });
        }
      }

      dbDisconnect();

      // Return all metadata acquired
      res.status(207).send(metadata_list);
      return;
    } catch (error) {
      dbDisconnect();
      console.error(error);
      res.status(500).send("Failure to query database.");
      return;
    }
  }
}

function parseSubtitlesFileToChewie(filePath) {
  // Remove {...} blocks, and \\N they are not filtered by some ASS parsers
  function cleanAssText(text) {
    return text.replace(/{[^}]+}/g, "").replace(/\\N/g, "\n");
  }

  // '0:00:02.08' -> 2080ms
  function convertAssTime(text) {
    let bits = text.split(":");
    let lilbits = bits[2].split(".");
    let totalMS =
      Number(bits[0]) * 3600000 +
      Number(bits[1]) * 60000 +
      Number(lilbits[0]) * 1000 +
      Number(lilbits[1]) * 10;
    return totalMS;
  }

  if (filePath.toLowerCase().endsWith(".srt")) {
    let subtitles = [];

    try {
      // Loop through items in the SRTParser
      // Build a list that fits the Dart Chewie Subtitles format.
      let parser = new srtParser2();
      let buffer = fs.readFileSync(filePath).toString();
      for (let subtitle of parser.fromSrt(buffer)) {
        subtitles.push({
          index: subtitle.id,
          start_ms: subtitle.startSeconds * 1000,
          end_ms: subtitle.endSeconds * 1000,
          text: subtitle.text,
        });
      }
    } catch (error) {
      console.error(error);
      console.error(`Failed to parse subtitles from ${filePath}`);
      return { subtitles: [], status: false };
    }

    return { subtitles: subtitles, status: true };
  } else if (filePath.toLowerCase().endsWith(".ass")) {
    let subtitles = [];

    try {
      // Loop through items in the ASSParser
      // Build a list that fits the Dart Chewie Subtitles format.
      let buffer = fs.readFileSync(filePath).toString();
      let assObj = parseAss(buffer);
      let events = assObj.find((ele) => ele.section == "Events");

      let i = 0;
      for (let { key, value } of events.body) {
        if (key != "Dialogue") continue;
        subtitles.push({
          index: i,
          start_ms: convertAssTime(value.Start),
          end_ms: convertAssTime(value.End),
          text: cleanAssText(value.Text),
        });
        i++;
      }
    } catch (error) {
      console.error(error);
      console.error(`Failed to parse subtitles from ${filePath}`);
      return { subtitles: [], status: false };
    }

    return { subtitles: subtitles, status: true };
  } else {
    console.warn(
      `Request made for subtitles format we don't support on episode ${filePath}`
    );
    return { subtitles: [], status: false };
  }
}

/***************************************
 * Authentication
 **************************************/

/**
 * Utility for extracting the JWT from the request.
 * @param {HttpRequest} req
 * @returns JWT from the request, or empty string if none was found.
 */
function getJWTFromReq(req) {
  if (!req.headers || !req.headers.authorization) {
    return "";
  }
  const token_eles = req.headers.authorization.split(" ");
  if (token_eles.length != 2) {
    return "";
  }
  return token_eles[1];
}

/**
 * Check the request for a valid JWT in the header.
 * @param {HttpRequest} req
 * @returns Error string if there was a problem, otherwise empty string.
 */
function isReqJWTValid(req) {
  // Check the jwt in the authorization header
  // If it is valid, then allow the request to continue
  // If it is not valid, then return a 401
  const token = getJWTFromReq(req);
  if (token.length == 0) {
    return "No authorization header.";
  }

  // NOTE: We don't care about the decoded token,
  //       we just want to make sure that it is valid.
  try {
    jwt.verify(token, process.env.JWT_SECRET);
  } catch (err) {
    return "Invalid token.";
  }

  return "";
}

app.get("/GetPepper", function (req, res) {
  var ip = req.headers.host ?? req.ip;
  console.log(`${ip} requested the pepper.`);

  const secretKey = process.env.PASSWORD_PEPPER;
  if (secretKey == undefined) {
    res.status(500).send("Server is missing JWT secret key.");
    return;
  }
  res.status(200).send(secretKey);
});

app.post("/GetAuthToken", function (req, res) {
  var ip = req.headers.host ?? req.ip;
  console.log(`${ip} requested an auth token.`);

  // Parse request string
  if (!req.body.hasOwnProperty("pwdHash")) {
    recordIPFailedAttempt(ip, req.get("User-Agent"));
    res
      .status(400)
      .send(
        'Password Hash must be specified under "pwdHash", please see documentation.'
      );
    return;
  }

  // Check that the server has a password on file
  if (!fs.existsSync("./.pwd_hash")) {
    // Leave a trace that someone tried to auth
    // even though there is no password hash.
    console.log(
      "No password hash found, one must be created. " +
        "Please run create_password.py"
    );

    res.status(500).send("Server has no password configured.");
    return;
  }

  // Get the password hash
  const pwdHash = req.body.pwdHash;

  // Load the password hash
  fs.readFile("./.pwd_hash", function (err, pwdHashOnFile) {
    if (err) {
      console.error(err);
      res.status(500).send("Server failed to read password hash.");
      return;
    }

    // Check the password hash
    if (pwdHash == pwdHashOnFile) {
      // Create a new token
      const token = jwt.sign({ authenticated: true }, process.env.JWT_SECRET, {
        expiresIn: "1y",
      });

      // Caller was successful, record the IP
      recordIPSuccessfulAttempt(ip);

      // Send the token
      res.status(200).send(token);
    } else {
      recordIPFailedAttempt(ip, req.get("User-Agent"));
      res.status(401).send("Invalid password hash.");
    }
  });
});

/***************************************
 * Manga Data Interface
 **************************************/

app.get("/GetMangaCollectionIndex", function (req, res) {
  var ip = req.headers.host ?? req.ip;
  console.log(`${ip} requested manga collection index.`);

  // Check the jwt in the authorization header
  const err = isReqJWTValid(req);
  if (err.length) {
    res.status(401).send(err);
    return;
  }
  recordIPSuccessfulAttempt(ip);

  // Ensure that the jwt path is set up
  const token = getJWTFromReq(req);
  if (!isMediaPathSet(token)) {
    createMediaPath(token);
  }

  // Return the index
  var { index, isGood } = _mediaCollectionIndex["manga"];
  if (isGood) res.status(200).send(Object.values(index));
  else res.status(500).send("Server index is stale.");
});

app.get("/GetMangaMetaDataByTitle", function (req, res) {
  var ip = req.headers.host ?? req.ip;

  // Extract the title from the request
  if (!req.query.hasOwnProperty("titles")) {
    console.log(`${ip} made a bad request for manga metadata.`);
    res
      .status(400)
      .send(
        'Title must be specified under "titles", please see documentation.'
      );
    return;
  }
  const titles_str = req.query.titles;

  // Logging
  console.log(`${ip} requested manga(s) \"${titles_str}\" metadata.`);

  // Check the jwt in the authorization header
  const err = isReqJWTValid(req);
  if (err.length) {
    res.status(401).send(err);
    return;
  }
  recordIPSuccessfulAttempt(ip);

  // Filter function for fields we don't want to send to the client
  function filter_db_privates(doc) {
    delete doc._id;
  }

  // NOTE: Response to client is all is handled in here
  queryDbByTitle(titles_str, "manga", filter_db_privates, res);
});

app.get("/GetMangaChaptersByTitle", function (req, res) {
  var ip = req.headers.host ?? req.ip;

  // Parse request
  if (!req.query.hasOwnProperty("titles")) {
    console.log(`${ip} made a bad request for chapter index.`);
    res
      .status(400)
      .send(
        'Title must be specified under "titles", please see documentation.'
      );
    return;
  }
  const titles_str = req.query.titles;

  // Logging
  console.log(`${ip} requested manga "${titles_str}" chapter index.`);

  // Check the jwt in the authorization header
  const err = isReqJWTValid(req);
  if (err.length) {
    res.status(401).send(err);
    return;
  }
  recordIPSuccessfulAttempt(ip);

  // Build a list containing the chapter index for each requested title
  // Data is in the FS index
  // Include with each index a status flag
  let chapterIndex = [];
  for (let title of titles_str.split(",")) {
    if (_mediaFSIndex["manga"].hasOwnProperty(title)) {
      var { chapters, isGood } = _mediaFSIndex["manga"][title];
      chapterIndex.push({
        data: chapters,
        status: isGood ? 200 : 500,
        message: isGood ? "" : `Server data for title "${title}" is bad.`,
      });
    } else {
      chapterIndex.push({
        data: {},
        status: 404,
        message: `Server does not recognize title "${title}".`,
      });
    }
  }

  res.status(207).send(chapterIndex);
});

/***************************************
 * Video Data Interface
 **************************************/

app.get("/GetVideoCollectionIndex", function (req, res) {
  var ip = req.headers.host ?? req.ip;
  console.log(`${ip} requested video collection index.`);

  // Check the jwt in the authorization header
  const err = isReqJWTValid(req);
  if (err.length) {
    res.status(401).send(err);
    return;
  }
  recordIPSuccessfulAttempt(ip);

  // Ensure that the jwt path is set up
  const token = getJWTFromReq(req);
  if (!isMediaPathSet(token)) {
    createMediaPath(token);
  }

  var { index, isGood } = _mediaCollectionIndex["video"];
  if (isGood) res.status(200).send(Object.values(index));
  else res.status(500).send("Server index is stale.");
});

app.get("/GetVideoMetaDataByTitle", function (req, res) {
  var ip = req.headers.host ?? req.ip;

  // Parse request
  if (!req.query.hasOwnProperty("titles")) {
    res
      .status(400)
      .send(
        'Title must be specified under "titles", please see documentation.'
      );
    return;
  }
  const titles_str = req.query.titles;

  // Logging
  console.log(`${ip} requested video(s) \"${titles_str}\" metadata.`);

  // Check the jwt in the authorization header
  const err = isReqJWTValid(req);
  if (err.length) {
    res.status(401).send(err);
    return;
  }
  recordIPSuccessfulAttempt(ip);

  // Filter function for fields we don't want to send to the client
  function filter_db_privates(doc) {
    delete doc._id;
  }

  // NOTE: Response to client is all is handled in here
  queryDbByTitle(titles_str, "video", filter_db_privates, res);
});

app.get("/GetVideoEpisodesByTitle", function (req, res) {
  var ip = req.headers.host ?? req.ip;

  // Parse request
  if (!req.query.hasOwnProperty("titles")) {
    res
      .status(400)
      .send(
        'Title must be specified under "titles", please see documentation.'
      );
    return;
  }
  const titles_str = req.query.titles;

  // Logging
  console.log(`${ip} requested videos "${titles_str}" episode index.`);

  // Check the jwt in the authorization header
  const err = isReqJWTValid(req);
  if (err.length) {
    res.status(401).send(err);
    return;
  }
  recordIPSuccessfulAttempt(ip);

  // Build a list containing the chapter index for each requested title
  // Data is in the FS index
  // Include with each index a status flag
  let episodeIndex = [];
  for (let title of titles_str.split(",")) {
    if (_mediaFSIndex["video"].hasOwnProperty(title)) {
      var { episodes, isGood } = _mediaFSIndex["video"][title];
      episodeIndex.push({
        data: episodes,
        status: isGood ? 200 : 500,
        message: isGood ? "" : `Server data for title "${title}" is bad.`,
      });
    } else {
      episodeIndex.push({
        data: [],
        status: 404,
        message: `Server does not recognize title "${title}".`,
      });
    }
  }

  res.status(207).send(episodeIndex);
});

app.get("/GetSubtitleSelectionsForEpisode", function (req, res) {
  var ip = req.headers.host ?? req.ip;

  // Parse request
  if (!req.query.hasOwnProperty("title")) {
    res
      .status(400)
      .send('Title must be specified under "title", please see documentation.');
    return;
  }
  if (!req.query.hasOwnProperty("episode")) {
    res
      .status(400)
      .send(
        'Episode must be specified under "episode", please see documentation.'
      );
    return;
  }
  const title_str = req.query.title;
  const episode_str = req.query.episode;

  // Logging
  console.log(
    `${ip} requested "${title_str}" - "${episode_str}" Subtitles Selections.`
  );

  // Check the jwt in the authorization header
  const err = isReqJWTValid(req);
  if (err.length) {
    res.status(401).send(err);
    return;
  }
  recordIPSuccessfulAttempt(ip);

  // Get the subtitles options for the provided episode of the given title.
  if (_mediaFSIndex["subtitles"].hasOwnProperty(title_str)) {
    var { subtitleMap, isGood } = _mediaFSIndex["subtitles"][title_str];

    // Case where our subtitle data is not good
    /// TODO: do something about this when we encounter this scenario
    if (!isGood) {
      res
        .status(500)
        .send(`Server subtitles data for title "${title_str}" is bad.`);
      return;
    }

    // Case where we just don't have any subtitles for this title
    if (!subtitleMap.hasOwnProperty(episode_str)) {
      res
        .status(204)
        .send(
          `Server has no subtitles for episode "${episode_str}" of title "${title_str}".`
        );
      return;
    }

    let tracks = [];
    for (let subtitleFile of subtitleMap[episode_str]) {
      let { trackKey } = splitSubtitleFile(subtitleFile);
      tracks.push(trackKey);
    }

    res.status(200).send(tracks);
    return;
  } else {
    res.status(204).send(`Server has no subtitles for "${title_str}".`);
    return;
  }
});

app.get("/GetSubtitlesChewieFmt", function (req, res) {
  var ip = req.headers.host ?? req.ip;

  // Parse request
  if (!req.query.hasOwnProperty("title")) {
    res
      .status(400)
      .send('Title must be specified under "title", please see documentation.');
    return;
  }
  if (!req.query.hasOwnProperty("episode")) {
    res
      .status(400)
      .send(
        'Episode must be specified under "episode", please see documentation.'
      );
    return;
  }
  if (!req.query.hasOwnProperty("track")) {
    res
      .status(400)
      .send(
        'Subtitle track must be specified under "track", please see documentation.'
      );
    return;
  }
  const title_str = req.query.title;
  const episode_str = req.query.episode;
  const track_str = req.query.track;

  // Logging
  console.log(
    `${ip} requested "${track_str}" subtitles for "${title_str}" - "${episode_str}".`
  );

  // Check the jwt in the authorization header
  const err = isReqJWTValid(req);
  if (err.length) {
    res.status(401).send(err);
    return;
  }
  recordIPSuccessfulAttempt(ip);

  // Get the subtitles options for the provided episode of the given title.
  if (_mediaFSIndex["subtitles"].hasOwnProperty(title_str)) {
    var { subtitleMap, isGood } = _mediaFSIndex["subtitles"][title_str];

    // Error handling
    if (!isGood) {
      res
        .status(500)
        .send(`Server subtitles data for title "${title_str}" is bad.`);
      return;
    }

    // This is an client error, as they should have a list of valid subtitles.
    if (!subtitleMap.hasOwnProperty(episode_str)) {
      res
        .status(404)
        .send(
          `Server has no subtitles for episode "${episode_str}" of title "${title_str}".`
        );
      return;
    }

    // Find the requested filename
    let subtitleFile = subtitleMap[episode_str].find(function (fileName) {
      let { trackKey } = splitSubtitleFile(fileName);
      return trackKey == track_str;
    });
    if (!subtitleFile) {
      res
        .status(404)
        .send(
          `Server has no track ${track_str} for episode "${episode_str}" of title "${title_str}".`
        );
      return;
    }

    // Parse the file with our helper.
    let pathSubtitles = config.folders.FolderSubtitles;
    let pathSubtitle = `${pathSubtitles}/${title_str}/${subtitleFile}`;
    let { subtitles, status } = parseSubtitlesFileToChewie(pathSubtitle);
    if (!status) {
      res
        .status(500)
        .send(
          `Server has track ${track_str} for episode "${episode_str}" of title "${title_str}", but failed to read it.`
        );
      return;
    }

    // If all has gone well, then we can return the data.
    res.status(200).send(subtitles);
    return;
  } else {
    // This is an client error, as they should have a list of valid tracks.
    res.status(404).send(`Server has no subtitles for "${title_str}".`);
    return;
  }
});
