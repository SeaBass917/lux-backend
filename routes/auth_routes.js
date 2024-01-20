import express from "express";
import fs from "fs";

import { createMediaPath, generateNewToken } from "../auth/auth.js";
import logger from "../utilities/logger.js";
import env from "../utilities/env.js";

const router = express.Router();
const pathPasswordHash = "./.pwd_hash";

/**
 * @api {get} /pepper Request secret key pepper.
 * @apiName GetPepper
 * @apiGroup Auth
 *
 * @apiSuccess {String} 200 Pepper for the server auth hashing.
 */
router.get("/pepper", function (req, res) {
  /// NOTE: env.PASSWORD_PEPPER validation is handled in env.js
  res.status(200).send(env.PASSWORD_PEPPER);
});

/**
 * @api {get} /auth-token Request an auth token.
 * @apiName GetAuthToken
 * @apiGroup Auth
 *
 * @apiParam {String} pwdHash Password hash.
 *
 * @apiSuccess {String} 200 JWT auth token.
 *
 * @apiError {String} 400 Caller did not provide a password.
 * @apiError {String} 401 Invalid password hash.
 * @apiError {String} 500 Server failed to read password hash.
 */
router.post("/auth-token", function (req, res) {
  // Parse request string
  if (!req.body.hasOwnProperty("pwdHash") || req.body.pwdHash == "") {
    res
      .status(400)
      .send(
        'Password Hash must be specified under "pwdHash", please see documentation.'
      );
    return;
  }
  const pwdHash = req.body.pwdHash;

  // Load the password hash
  fs.readFile(pathPasswordHash, (err, pwdHashOnFile) => {
    if (err) {
      logger.error(err);
      res.status(500).send("Server failed to read password hash.");
      return;
    }
    // Check the password hash
    if (pwdHash == pwdHashOnFile) {
      // Create a new token
      const token = generateNewToken();

      // Ensure that the jwt path is set up
      createMediaPath(token);

      // Send the token
      res.status(200).send(token);
    } else {
      res.status(401).send("Invalid password hash.");
    }
  });
});

export default router;
