import * as child from "child_process";

import projectDir from "./project_dir.js";
import logger from "./logger.js";

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
  sh(`python3 ${projectDir}/scripts/metadata_dl_manga.py`)
    .then(function (data) {
      if (data.stdout.length) logger.info(data.stdout);
      if (data.stderr.length) logger.error(data.stderr);
    })
    .catch(function (err) {
      logger.error(err.toString());
    });

  logger.info("Updating Video Metadata...");
  sh(`python3 ${projectDir}/scripts/metadata_dl_video.py`)
    .then(function (data) {
      if (data.stdout.length) logger.info(data.stdout);
      if (data.stderr.length) logger.error(data.stderr);
    })
    .catch(function (err) {
      logger.error(err.toString());
    });
}

export { updateMetaInfo };
