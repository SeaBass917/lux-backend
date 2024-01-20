import dotenv from "dotenv";
import fs from "fs";

import logger from "./logger.js";
import { shutdown, ExitCodes } from "./shutdown.js";

const pathSecrets = "./.secrets.env";

/**
 *  Generate the secrets file.
 *  @returns {bool} Status of the operation.
 */
function generateSecrets() {
  try {
    fs.writeFileSync(
      pathSecrets,
      `JWT_SECRET=${bcrypt.genSaltSync(10)}\n` +
        `PASSWORD_PEPPER=${bcrypt.genSaltSync(10)}`
    );
    return true;
  } catch (err) {
    logger.error(err);
    return false;
  }
}

// Load the config and check that the secrets are present.
// If not, generate them.
// If that fails, exit.
dotenv.config({ path: pathSecrets });
if (!process.env.JWT_SECRET || !process.env.PASSWORD_PEPPER) {
  logger.info("Missing secrets, generating new ones...");
  if (generateSecrets()) {
    dotenv.config({ path: pathSecrets });
  } else {
    logger.error("Failed to generate secrets needed for operation.");
    shutdown(null, ExitCodes.ENV_ERROR);
  }
}

/**
 * Environment variables.
 */
const env = {
  JWT_SECRET: process.env.JWT_SECRET,
  PASSWORD_PEPPER: process.env.PASSWORD_PEPPER,
};

export default env;
