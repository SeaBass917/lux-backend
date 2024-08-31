import { dirname } from "path";
import { fileURLToPath } from "url";

// Determine the current working directory of the main application
// So that we can filter that out of the logging.
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectDir = __dirname.substring(0, __dirname.lastIndexOf("/"));

export default projectDir;
