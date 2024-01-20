import logger from "./logger.js";

/**
 * Exit codes the server can close with.
 *
 * @property {number} SUCCESS       - Server closed successfully.
 * @property {number} UNKNOWN       - Unknown error (Try not to use this).
 * @property {number} CONFIG_ERROR  - Error with the config file.
 * @property {number} ENV_ERROR     - Problem with the environment variables.
 * @property {number} DB_ERROR      - Cannot communicate with the database.
 * @property {number} ADMIN_ERROR   - Something is missing that needed to be
 *                                    set up before starting the server the
 *                                    first time.
 * @property {number} FS_ERROR      - We can't read something that should be on
 *                                    file.
 */
const ExitCodes = {
  SUCCESS: 0,
  UNKNOWN: -1,
  CONFIG_ERROR: -2,
  ENV_ERROR: -3,
  DB_ERROR: -4,
  ADMIN_ERROR: -5,
  FS_ERROR: -6,
};

/**
 *  @brief  Handle the shutdown of the server.
 */
function shutdown(server = null, statusCode = ExitCodes.UNKNOWN) {
  if (server == null) {
    logger.info("Server is not running, exiting...");
    process.exit(statusCode);
  }
  logger.info("Shutting down the server...");
  server.close(() => {
    logger.info("Server has been gracefully closed.");
    process.exit(statusCode);
  });
}

export { ExitCodes, shutdown };
