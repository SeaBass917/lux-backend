import express from "express";
import fs from "fs";

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
 *         chapters: {
 *             ch1: ["pg1", "pg2", ...],
 *             ...
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
 *  Set up the FS index. Blocking, so that the server will not start
 *  until the index is ready.
 */
function initFSIndex() {
  try {
    // Loop through all titles in the manga directory
    const titles = fs.readdirSync(config.folders.FolderManga);

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
        logger.error(err);
        titleData["isGood"] = false;
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
  fs.readdir(config.folders.FolderManga, (err, titles) => {
    if (err) {
      logger.error(err);
      _fsIndex["isGood"] = false;
      return;
    }

    for (let title of titles) {
      const titleDir = config.folders.FolderManga + title;

      // For each title get the list of chapters,
      // and for each of those chapters get a list of pages.
      // Add that list of pages to the chapter index for this title.
      // If anything goes wrong, mark this title's index as bad.
      fs.readdir(titleDir, (err, chapters) => {
        if (err) {
          logger.error(err);
          titleData = _fsIndex["index"][title] ?? {
            chapters: {},
            isGood: false,
          };
          titleData["isGood"] = false;
          _fsIndex["index"][title] = titleData;
          return;
        }

        for (let chapter of chapters) {
          fs.readdir(`${titleDir}/${chapter}`, (err, pages) => {
            if (err) {
              logger.error(err);
              titleData = _fsIndex["index"][title] ?? {
                chapters: {},
                isGood: false,
              };
              titleData["isGood"] = false;
              _fsIndex["index"][title] = titleData;
              return;
            }

            titleData = _fsIndex["index"][title] ?? {
              chapters: {},
              isGood: true,
            };
            titleData["chapters"][chapter] = pages;
            _fsIndex["index"][title] = titleData;
          });
        }
      });
    }
  });

  setInterval(updateFSIndex, config.server.PollingRateMediaSeconds * 1000);
}

/**
 * @api {get} /collection-index Request manga collection index.
 * @apiName GetMangaCollectionIndex
 * @apiGroup Manga
 *
 * @apiSuccess {Object[]} 200 List of manga titles.
 *
 * @apiError {String} 500 Server unable to get metadata on manga.
 */
router.get("/collection-index", function (req, res) {
  getCollectionHomepageMetadata("manga")
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
 * @api {get} /metadata Request manga metadata.
 * @apiName GetMangaMetadata
 * @apiGroup Manga
 *
 * @apiSuccess {Object[]} 200 List of manga titles.
 *
 * @apiError {String} 400 Caller did not provide any titles.
 * @apiError {String} 500 Database issues.
 */
router.get("/metadata", function (req, res) {
  // Extract the title from the request
  if (!req.query.hasOwnProperty("titles") || req.query.titles == "") {
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
  queryDbByTitle(titles, "manga")
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
 * @api {get} /chapters Request manga chapters.
 * @apiName GetMangaChapters
 * @apiGroup Manga
 *
 * @apiParam {String} titles Comma separated list of titles.
 *
 * @apiSuccess {List<Obj>} 207 Chapter list for each title.
 *                          Status code for each title is present in the
 *                          object.
 *                          If status is 200, then the chapter list is
 *                          present in the object.
 *                          If status is 500, then we return an error message.
 *                          e.g.:
 *                         ```
 *                         [
 *                           {
 *                             data: {
 *                               ch1: ["pg1", "pg2", ...],
 *                               ...
 *                             },
 *                            status: 200,
 *                          },
 *                          {
 *                            data: "Server data for title 'MyBook' is bad.",
 *                            status: 500,
 *                          },
 *                          ...
 *                         ]
 *                        ```
 *
 * @apiError {String} 400 Caller did not provide a title.
 * @apiError {String} 404 Server does not recognize title.
 * @apiError {String} 500 Server index is stale.
 */
router.get("/chapters", function (req, res) {
  // Parse request
  if (!req.query.hasOwnProperty("titles") || req.query.titles == "") {
    res
      .status(400)
      .send(
        'Title must be specified under "titles", please see documentation.'
      );
    return;
  }
  const titles_str = req.query.titles;
  const titles = titles_str.split(",");

  // Build a list containing the chapter index for each requested title
  // Data is in the FS index
  // Include with each index a status flag
  let chapterIndex = [];
  for (let title of titles) {
    if (_fsIndex["index"].hasOwnProperty(title)) {
      var { chapters, isGood } = _fsIndex["index"][title];
      chapterIndex.push({
        data: isGood ? chapters : `Server data for title "${title}" is bad.`,
        status: isGood ? 200 : 500,
      });
    } else {
      chapterIndex.push({
        data: `Server does not recognize title "${title}".`,
        status: 404,
      });
    }
  }

  res.status(207).send(chapterIndex);
});

// Initialize the FS index
// then start a timer to update it periodically.
initFSIndex();
setInterval(updateFSIndex, config.server.PollingRateMediaSeconds * 1000);

export default router;
