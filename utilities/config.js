import fs from "fs";
import ini from "ini";

/**
 *  Config data from the config.ini file.
 */

// HACK
// We create a cyclical dependency if we import shutdown here.
// so we just copy the relevant exit code here.
const CONFIG_ERROR = -2;

var config;
try {
  config = ini.parse(fs.readFileSync("./config.ini", "utf-8"));
} catch (err) {
  console.error(err);
  process.exit(CONFIG_ERROR);
}

/**
 *  @brief Helper method for making sure that the required configuration
 *         fields are present in the config file.
 *  @returns True if all required fields are present, false otherwise.
 */
function validateConfig() {
  let missing_header = false;
  let missing_params = false;

  ////////////////////////////////////////////////////////////////
  // Server parameters
  ////////////////////////////////////////////////////////////////
  if (config.server == undefined) {
    console.error("config.ini Is missing the server header.");
    missing_header = true;
  } else {
    let required_params = [
      "MediaUpdateIntervalMs",
      "BlacklistUpdateIntervalMs",
      "MaxRequestSize",
      "DbAddress",
      "LimitFailedLoginAttempts",
      "LimitUnauthorizedRequestsWindowMs",
      "LimitUnauthorizedRequestsCount",
      "PeriodJWTExpiration",
    ];
    for (let param of required_params) {
      if (config.server[param] == undefined) {
        console.error(`config.ini [server] Is missing the ${param} parameter.`);
        missing_params = true;
      }
    }
  }

  ////////////////////////////////////////////////////////////////
  // Logging parameters
  ////////////////////////////////////////////////////////////////
  if (config.logging == undefined) {
    console.error("config.ini Is missing the logging header.");
    missing_header = true;
  } else {
    let required_params = [
      "ArchiveLogs",
      "FolderLogging",
      "LogFileSizeMax",
      "PeriodPurgeLogs",
    ];
    for (let param of required_params) {
      if (config.logging[param] == undefined) {
        console.error(
          `config.ini [logging] Is missing the ${param} parameter.`
        );
        missing_params = true;
      }
    }
  }

  ////////////////////////////////////////////////////////////////
  // Folders parameters
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

// Before we do anything else, validate the config file.
if (!validateConfig()) {
  console.error("Cannot run without a valid config.");
  process.exit(CONFIG_ERROR);
}

export default config;
