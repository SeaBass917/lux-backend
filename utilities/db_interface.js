import * as mongodb from "mongodb";
import dotenv from "dotenv";
import logger from "./logger.js";
import { ExitCodes, shutdown } from "./shutdown.js";

dotenv.config({
  path: ".env",
});

var dbClient = null;
try {
  dbClient = new mongodb.MongoClient(process.env.DB_ADDRESS, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  });
  logger.info("DB is online.");
} catch (err) {
  logger.error("Failed to connect to DB.");
  shutdown(null, ExitCodes.DB_ERROR);
}

/**
 *  Connect to the database and return the client.
 * @returns {Promise<mongodb.MongoClient>} The database client.
 */
async function getDBConnection() {
  try {
    await dbClient.connect();
    logger.info("Connected to MongoDB");
    return dbClient;
  } catch (error) {
    logger.error("Error connecting to MongoDB", error);
    return null;
  }
}

/**
 *  Disconnect to the database.
 *  @returns {Promise<bool>} Status of the disconnect.
 */
async function dbDisconnect() {
  try {
    await dbClient.close();
    logger.info("Closed MongoDB connection");
    return true;
  } catch (error) {
    logger.error("Error closing MongoDB connection", error);
    return false;
  }
}

/**
 *  Query the DB, and return the metadata for each of the specified titles.
 *
 *  @param {String[]} titles The set of titles to query.
 *  @param {String} dbName The name of the DB to query.
 *  @returns {Promise<List<Object>>}
 *           The metadata for each of the titles.
 *           Metadata will be null if we fail for a specific title.
 */
async function queryDbByTitle(titles, dbName) {
  if (titles.length == 0 || !dbName) {
    return null;
  }

  try {
    // Get the specified collection from the db.
    const dbClient = await getDBConnection();
    if (!dbClient) return null;
    const dbMedia = dbClient.db("mediaMetadata");
    const collection = dbMedia.collection(dbName);

    // Query the DB for the titles
    const docs = await collection.find({ title: { $in: titles } }).toArray();

    // Ensure the doc list is in the same order as the titles
    var docsOut = [];
    for (let title of titles) {
      let docFound = null;
      for (let doc of docs) {
        if (title == doc.title) {
          docFound = doc;
          break;
        }
      }
      docsOut.push(docFound);
      if (!docFound) {
        logger.error(`Failed to find ${title} in ${dbName} DB.`);
      }
    }

    // Close the connection and return the metadata
    dbDisconnect();
    return docsOut;
  } catch (error) {
    dbDisconnect();
    logger.error(error);
    return null;
  }
}

/**
 *  Query the DB, and return the metadata for each of the specified titles.
 *  This is a subset of the metadata, the bare minimum needed for the homepage.
 *  @param {String} dbName The name of the DB to query.
 *  @returns {Promise<List<Object>>} The metadata for each of the titles.
 */
async function getCollectionHomepageMetadata(dbName) {
  if (!dbName || !["manga", "video"].includes(dbName)) {
    return null;
  }

  try {
    // Get the specified collection from the db.
    const dbClient = await getDBConnection();
    if (!dbClient) return null;
    const dbMedia = dbClient.db("mediaMetadata");
    const collection = dbMedia.collection(dbName);

    // Query the collection for all docs
    const docs = await collection.find({}).toArray();

    // Filter down to only what we need to send.
    // Base the dataset on the type of media.
    var docsOut = [];
    if (dbName == "manga") {
      for (let doc of docs) {
        docsOut.push({
          title: doc["title"],
          nsfw: doc["nsfw"],
          dateAdded: doc["dateAdded"],
          author: doc["author"],
        });
      }
    } else if (dbName == "video") {
      for (let doc of docs) {
        docsOut.push({
          title: doc["title"],
          nsfw: doc["nsfw"],
          dateAdded: doc["dateAdded"],
          yearstart: doc["yearstart"],
          description: doc["description"],
        });
      }
    }

    // Close the connection and return the metadata
    dbDisconnect();
    return docsOut;
  } catch (error) {
    dbDisconnect();
    logger.error(error);
    return null;
  }
}

export {
  getDBConnection,
  dbDisconnect,
  queryDbByTitle,
  getCollectionHomepageMetadata,
};
