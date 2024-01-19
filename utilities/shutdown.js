import logger from "./logging.js";

/**
 * Error codes the server can close with.
 */
const ExitCodes = {
  SUCCESS: 0,
  UNKNOWN: -1,
  CONFIG_ERROR: -2,
  ENV_ERROR: -3,
};

/**
 *  @brief  Handle the shutdown of the server.
 */
function shutdown(server = null, statusCode = ExitCodes.SUCCESS) {
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
