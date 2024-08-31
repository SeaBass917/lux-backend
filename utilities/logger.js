import fs from "fs";
import { get as stackTraceGet } from "stack-trace";
import winston from "winston";
import "winston-daily-rotate-file";

import config from "./config.js";
import projectDir from "./project_dir.js";

/**
 * Utility for cleaning up the full path of a file.
 */
function cleanupFullPath(fullPath) {
  return fullPath.replace(`file://${projectDir}/`, "");
}

/**
 *  Utility for getting the file name and line number of the caller.
 */
function getCallSiteInfo() {
  const trace = stackTraceGet();

  // Get the first trace after the call to "winston/create-logger"
  let indexCallSite = -1;
  for (let i = 0; i < trace.length; i++) {
    const traceFileName = trace[i].getFileName();
    if (traceFileName.includes("winston/create-logger.js")) {
      indexCallSite = i;
      break;
    }
  }
  // Check to make sure we found a valid index
  if (indexCallSite == -1 || trace.length - 1 <= indexCallSite) {
    return "unknown:0";
  }

  // Get the next trace after the call to "winston/create-logger"
  const callSite = trace[indexCallSite + 1];
  const fileName = cleanupFullPath(callSite.getFileName());
  const lineNumber = callSite.getLineNumber();

  return `${fileName}:${lineNumber}`;
}

/**
 *  Setup the logging manager.
 *
 *  Using the logger:
 *  ```js
 *     logger.info('This is an info message');
 *     logger.error('This is an error message');
 *  ```
 *
 *  @param {string} folderPathOut   The full path to the log folder.
 *  @param {boolean} doArchiveLogs  Whether or not to zip the log file at the
 *                                  end of a day.
 *  @param {number} maxLogSize      The maximum size of the log files before we
 *                                  roll over to a new file with suffix
 *                                  `.1`, `.2`, etc...
 *  @param {number} periodPurgeLogs The maximum number of log files we keep on
 *                                  archive before deleting them.
 *
 *  @returns {winston.Logger} The logging manager.
 */
function setupLoggingManager(
  folderPathOut,
  doArchiveLogs,
  maxLogSize,
  periodPurgeLogs
) {
  // If the folder is null, then we can't log.
  // If the folder does not exist, then create it.
  if (!folderPathOut) return null;
  if (!fs.existsSync(folderPathOut)) {
    fs.mkdirSync(folderPathOut, { recursive: true });
  }

  // Configure the logger to write to the provided files using timestamped JSON.
  const logger = winston.createLogger({
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.json(),
      winston.format.printf((info) => {
        const callSiteInfo = getCallSiteInfo();
        return `${info.timestamp} ${info.level} ${callSiteInfo}: ${info.message}`;
      })
    ),
    transports: [
      new winston.transports.DailyRotateFile({
        dirname: folderPathOut,
        extension: ".sterrdout",
        filename: "lux_%DATE%",
        datePattern: "YYYY-MM-DD",
        zippedArchive: doArchiveLogs,
        maxSize: maxLogSize,
        maxFiles: periodPurgeLogs,
        level: "error",
        format: winston.format.combine(
          winston.format.colorize(),
          winston.format.timestamp({
            format: () => new Date().toLocaleString(),
          }),
          winston.format.printf((error) => {
            const callSiteInfo = getCallSiteInfo();
            return `${error.timestamp} ERROR ${callSiteInfo}: ${error.message}`;
          })
        ),
      }),
      new winston.transports.DailyRotateFile({
        dirname: folderPathOut,
        extension: ".stdout",
        filename: "lux_%DATE%",
        datePattern: "YYYY-MM-DD",
        zippedArchive: doArchiveLogs,
        maxSize: maxLogSize,
        maxFiles: periodPurgeLogs,
        level: "info",
        format: winston.format.combine(
          winston.format.colorize(),
          winston.format.timestamp({
            format: () => new Date().toLocaleString(),
          }),
          winston.format.printf((info) => {
            const callSiteInfo = getCallSiteInfo();
            return `${info.timestamp} INFO ${callSiteInfo}: ${info.message}`;
          })
        ),
      }),
      new winston.transports.Console({
        format: winston.format.combine(
          winston.format.colorize(),
          winston.format.timestamp(),
          winston.format.printf((info) => {
            const callSiteInfo = getCallSiteInfo();
            return `${info.timestamp} ${info.level} ${callSiteInfo}: ${info.message}`;
          })
        ),
        level: "info",
      }),
    ],
  });

  return logger;
}

/**
 * Logging manager.
 */
const logger = setupLoggingManager(
  config.logging.FolderLogging,
  config.logging.ArchiveLogs,
  config.logging.LogFileSizeMax,
  config.logging.PeriodPurgeLogs
);

export default logger;
