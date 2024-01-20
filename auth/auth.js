import fs from "fs";
import jwt from "jsonwebtoken";

import env from "../utilities/env.js";
import config from "../utilities/config.js";

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
    jwt.verify(token, env.JWT_SECRET);
  } catch (err) {
    return "Invalid token.";
  }

  return "";
}

/**
 *  Generate a new JWT token.
 *  @returns {string} New token.
 */
function generateNewToken() {
  return jwt.sign({ authenticated: true }, process.env.JWT_SECRET, {
    expiresIn: config.server.PeriodJWTExpiration,
  });
}

/**
 * @brief  Helper function for creating the media path for the client.
 * @param {String} token jwt token of the client.
 */
function createMediaPath(token) {
  const tokenShort = convertTokenToFolderName(token);

  // If the folder already exists, then we don't need to do anything
  const exists = fs.existsSync(`./public/${tokenShort}`);
  if (exists) return;

  // Otherwise create the folder,
  // and then create symbolic links to the media folders
  fs.mkdir(`./public/${tokenShort}`, () => {
    const folderList = [
      ["manga", config.folders.FolderManga],
      ["video", config.folders.FolderVideo],
      ["music", config.folders.FolderMusic],
      ["image", config.folders.FolderImage],
      ["subtitles", config.folders.FolderSubtitles],
      ["lux-assets", config.folders.FolderLuxAssets],
    ];

    // Crete symbolic links to the media folders
    for (const folder of folderList) {
      fs.symlinkSync(
        folder[1],
        `./public/${tokenShort}/${folder[0]}`,
        "junction"
      );
    }
  });
}

/**
 *  Remove any signed paths from the public folder, synchronously.
 */
function removeMediaPathSync() {
  var folders = fs.readdirSync("./public");
  for (let folder of folders) {
    if (folder == "assets") continue;
    var files = fs.readdirSync(`./public/${folder}`);
    for (let file of files) {
      fs.rmSync(`./public/${folder}/${file}`);
    }
    fs.rmdirSync(`./public/${folder}`);
  }
}

export {
  getJWTFromReq,
  isReqJWTValid,
  generateNewToken,
  createMediaPath,
  removeMediaPathSync,
};
