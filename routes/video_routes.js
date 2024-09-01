import parseAss from "ass-parser";
import express from "express";
import fs from "fs";
import srtParser2 from "srt-parser-2";

import config from "../utilities/config.js";
import logger from "../utilities/logger.js";
import { ExitCodes, shutdown } from "../utilities/shutdown.js";
import {
  getCollectionHomepageMetadata,
  queryDbByTitle,
} from "../utilities/db_interface.js";

const router = express.Router();

/**
 * Schema as follows:
 * ```
 * {
 *     isGood: false|true,
 *     index: {
 *       title0: {
 *         episodes: ["ep1", "ep2", ...],
 *         subtitlesMap: {
 *            "ep1": ["en-1", "es-1"], "ep2": [...], ...
 *         },
 *         isGood: false|true,
 *        },
 *       ...
 *      },
 *     ...
 * }
 * ```
 */
var _fsIndex = {
  isGood: false,
  index: {},
};

/**
 *  Filter function for fields we don't want to send to the client
 */
function filterDbPrivates(doc) {
  delete doc._id;
}

/**
 * Utility method for interpreting the encoded information
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
  let elements = subtitle_file.split(".");
  if (elements.length < 3) return "";
  return {
    episodeName: elements.slice(0, elements.length - 2).join("."),
    trackKey: elements[elements.length - 2],
    encoding: elements[elements.length - 1],
  };
}

/**
 *  Set up the FS index. Blocking, so that the server will not start
 *  until the index is ready.
 */
function initFSIndex() {
  try {
    // Loop through all titles in the manga directory
    const titles = fs.readdirSync(config.folders.FolderVideo);

    for (let title of titles) {
      const titleDir = config.folders.FolderVideo + title;

      // For each title get the list of episodes and any subtitles we have on
      // file.
      var titleData = { episodes: [], subtitles: [], isGood: true };
      try {
        titleData["episodes"] = fs.readdirSync(titleDir);
      } catch (err) {
        logger.warn(`Failed to read episodes for ${title} in ${titleDir}`);
        logger.warn(err.toString());
        titleData["isGood"] = false;
      }
      try {
        const pathSubtitles = config.folders.FolderSubtitles + title;
        const subtitles = fs.readdirSync(pathSubtitles);

        var subtitlesMap = {};
        for (let subtitleFile of subtitles) {
          let { episodeKey } = splitSubtitleFile(subtitleFile);
          if (!subtitlesMap.hasOwnProperty(episodeKey)) {
            subtitlesMap[episodeKey] = [];
          }
          subtitlesMap[episodeKey].push(subtitleFile);
        }

        titleData["subtitlesMap"] = subtitlesMap;
      } catch (_) {
        titleData["subtitlesMap"] = {};
      }

      _fsIndex["index"][title] = titleData;
    }
  } catch (err) {
    logger.error(err);
    shutdown(null, ExitCodes.ADMIN_ERROR);
  }
}

/**
 *  Update the FS index. Non-blocking, so this can be done while the
 *  server is running.
 */
function updateFSIndex() {
  // Loop through all titles in the manga directory
  fs.readdir(config.folders.FolderVideo, (err, titles) => {
    if (err) {
      logger.error(err);
      _fsIndex["isGood"] = false;
      return;
    }

    for (let title of titles) {
      const titleDir = config.folders.FolderVideo + title;

      // For each title get the list of chapters,
      // and for each of those chapters get a list of pages.
      // Add that list of pages to the chapter index for this title.
      // If anything goes wrong, mark this title's index as bad.
      fs.readdir(titleDir, (err, episodes) => {
        if (err) {
          logger.error(err);
          _fsIndex["index"][title] = {
            episodes: [],
            isGood: false,
          };
          return;
        }

        _fsIndex["index"][title] = {
          episodes: episodes,
          isGood: true,
        };

        // Get the subtitlesMap for this title
        const pathSubtitles = config.folders.FolderSubtitles + title;
        fs.readdir(pathSubtitles, (err, subtitles) => {
          if (err) {
            _fsIndex["index"][title] = {
              episodes: episodes,
              subtitlesMap: null,
              isGood: true,
            };
            return;
          }

          var subtitlesMap = {};
          for (let subtitleFile of subtitles) {
            let { episodeKey } = splitSubtitleFile(subtitleFile);
            if (!subtitlesMap.hasOwnProperty(episodeKey)) {
              subtitlesMap[episodeKey] = [];
            }
            subtitlesMap[episodeKey].push(subtitleFile);
          }

          _fsIndex["index"][title] = {
            episodes: episodes,
            subtitlesMap: subtitlesMap,
            isGood: true,
          };
        });
      });
    }
  });

  setInterval(updateFSIndex, config.server.MediaUpdateIntervalMs);
}

/**
 *  Parse a subtitles file into the format that Chewie expects.
 *  @param {String} filePath Path to the subtitles file.
 *  @returns {{subtitles : Object[], status : bool}}
 *          Object containing the `subtitles` and a `status` flag.
 */
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
      logger.error(
        `Failed to parse subtitles from ${filePath} due to ${error}`
      );
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
      logger.error(
        `Failed to parse subtitles from ${filePath} due to ${error}`
      );
      return { subtitles: [], status: false };
    }

    return { subtitles: subtitles, status: true };
  } else {
    logger.error(
      `Request made for subtitles format we don't support on episode ${filePath}`
    );
    return { subtitles: [], status: false };
  }
}

/**
 * @api {get} /collection-index Request video collection index.
 * @apiName GetVideoCollectionIndex
 * @apiGroup Video
 *
 * @apiSuccess {Object[]} 200 List of video titles.
 *
 * @apiError {String} 500 Server unable to get metadata on video.
 */
router.get("/collection-index", function (req, res) {
  getCollectionHomepageMetadata("video")
    .then((metadata) => {
      if (metadata) {
        res.status(200).send(metadata);
      } else {
        logger.error("Metadata was null");
        res.status(500).send("Server unable to get metadata.");
      }
    })
    .catch((err) => {
      logger.error(err);
      res.status(500).send("Server unable to get metadata.");
    });
});

/**
 * @api {get} /metadata Request video metadata.
 * @apiName GetVideoMetadata
 * @apiGroup Video
 *
 * @apiSuccess {Object[]} 200 List of video titles.
 *
 * @apiError {String} 400 Caller did not provide any titles.
 * @apiError {String} 500 Database issues.
 */
router.get("/metadata", function (req, res) {
  // Extract the title from the request
  if (
    !req.query ||
    !req.query.hasOwnProperty("titles") ||
    req.query.titles == ""
  ) {
    res
      .status(400)
      .send(
        'Title must be specified under "titles", please see documentation.'
      );
    return;
  }
  const titles_str = req.query.titles;
  const titles = titles_str.split(",");

  // Query the DB for the titles
  queryDbByTitle(titles, "video")
    .then((metaDataList) => {
      if (!metaDataList) {
        res.status(500).send("Server failed to query database.");
        return;
      }

      // Filter out the private fields
      metaDataList.forEach(filterDbPrivates);

      // Package the data as an array of {data, status}
      // where data is the metadata, and status is the status code
      const responseData = metaDataList.map((data) => {
        return { data: data, status: data ? 200 : 404 };
      });

      // Send the metadata
      res.status(207).send(responseData);
    })
    .catch((err) => {
      logger.error(err);
      res.status(500).send("Server failed to query database.");
    });
});

/**
 * @api {get} /episodes Request video episodes.
 * @apiName GetVideoEpisodes
 * @apiGroup Video
 *
 * @apiParam {String} titles Comma separated list of titles.
 *
 * @apiSuccess {List<Obj>} 207 Episode list for each title.
 *                          Status code for each title is present in the
 *                          object.
 *                          If status is 200, then the episode list is
 *                          present in the object.
 *                          If status is 500, then we return an error message.
 *                          e.g.:
 *                         ```
 *                         [
 *                           {
 *                             data: ["ep1", "ep2", ...],
 *                             status: 200,
 *                           },
 *                           {
 *                             data: "Server data for title 'MyShow' is bad.",
 *                             status: 500,
 *                           },
 *                           ...
 *                          ]
 *                        ```
 *
 * @apiError {String} 400 Caller did not provide a title.
 * @apiError {String} 404 Server does not recognize title.
 * @apiError {String} 500 Server index is stale.
 */
router.get("/episodes", function (req, res) {
  // Parse request
  if (
    !req.query ||
    !req.query.hasOwnProperty("titles") ||
    req.query.titles == ""
  ) {
    res
      .status(400)
      .send(
        'Title must be specified under "titles", please see documentation.'
      );
    return;
  }
  const titles_str = req.query.titles;
  const titles = titles_str.split(",");

  // Build a list containing the episode index for each requested title
  // Data is in the FS index
  // Include with each index a status flag
  let episodeIndex = [];
  for (let title of titles) {
    if (_fsIndex["index"].hasOwnProperty(title)) {
      var { episodes, isGood } = _fsIndex["index"][title];
      episodeIndex.push({
        data: isGood ? episodes : `Server data for title "${title}" is bad.`,
        status: isGood ? 200 : 500,
      });
    } else {
      episodeIndex.push({
        data: `Server does not recognize title "${title}".`,
        status: 404,
      });
    }
  }

  res.status(207).send(episodeIndex);
});

/**
 * @api {get} /subtitle-selections Request video episodes.
 * @apiName GetSubtitleSelections
 * @apiGroup Video
 *
 * @apiParam {String} title Title Requested.
 *
 * @apiSuccess {String[]} 200 List of subtitle tracks available for this title.
 * @apiSuccess {String}   204 Server has no subtitles for this title.
 *
 * @apiError {String} 400 Caller did not provide a title.
 * @apiError {String} 404 Server does not recognize title.
 * @apiError {String} 500 Server index is stale.
 */
router.get("/subtitle-selections", function (req, res) {
  // Parse request
  if (!req.query || !req.query.hasOwnProperty("title")) {
    res
      .status(400)
      .send('Title must be specified under "title", please see documentation.');
    return;
  }
  if (!req.query || !req.query.hasOwnProperty("episode")) {
    res
      .status(400)
      .send(
        'Episode must be specified under "episode", please see documentation.'
      );
    return;
  }
  const title_str = req.query.title;
  const episode_str = req.query.episode;

  // Get the subtitles options for the provided episode of the given title.
  if (!_fsIndex["index"].hasOwnProperty(title_str)) {
    res.status(404).send(`Server does not recognize title "${title_str}".`);
    return;
  }

  var { subtitleMap, isGood } = _fsIndex["index"][title_str];

  // Case where our subtitle data is not good
  /// TODO: do something about this when we encounter this scenario
  if (!isGood) {
    res.status(500).send(`Server data for title "${title_str}" is bad.`);
    return;
  }

  // Case where we just don't have any subtitles for this title
  if (!subtitleMap || !subtitleMap.hasOwnProperty(episode_str)) {
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
});

/**
 * @api {get} /subtitles Request video episodes.
 * @apiName GetSubtitles
 * @apiGroup Video
 *
 * @apiParam {String} title Title Requested.
 * @apiParam {String} episode Episode Requested.
 * @apiParam {String} track Subtitle track Requested.
 *
 * @apiSuccess {Object[]} 200 List of subtitles Packaged for Chewie.
 *
 * @apiError {String} 400 Caller did not provide a title.
 * @apiError {String} 404 Server does not recognize title, or does not have
 *                        subtitles for this title/episode/track.
 * @apiError {String} 500 Server index is stale.
 */
router.get("/subtitles-chewie", function (req, res) {
  // Parse request
  if (!req.query || !req.query.hasOwnProperty("title")) {
    res
      .status(400)
      .send('Title must be specified under "title", please see documentation.');
    return;
  }
  if (!req.query || !req.query.hasOwnProperty("episode")) {
    res
      .status(400)
      .send(
        'Episode must be specified under "episode", please see documentation.'
      );
    return;
  }
  if (!req.query || !req.query.hasOwnProperty("track")) {
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

  // Get the subtitles for the provided episode of the given title.
  // Then grab the specified track.
  if (!_fsIndex["index"].hasOwnProperty(title_str)) {
    res.status(404).send(`Server does not recognize title "${title_str}".`);
    return;
  }
  var { subtitleMap, isGood } = _fsIndex["index"][title_str];
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
});

// Initialize the FS index
// then start a timer to update it periodically.
initFSIndex();
setInterval(updateFSIndex, config.server.MediaUpdateIntervalMs);

export default router;
