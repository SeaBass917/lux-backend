import axios from "axios";
// eslint-disable-next-line
import { hash } from "bcryptjs-react";
import VideoMetaData from "../Video/VideoMetaData";

/**************************
 * Constants
 **************************/

const serverTimeoutSeconds = 5;

// TODO: Move this under configuration?
/// Server Port
const serverIP = process.env.REACT_APP_SERVER_IP;
const defaultServerPort = process.env.REACT_APP_SERVER_PORT || 8081;

// Endpoints
const endpointGetPepper = "auth/pepper";
const endpointGetAuthToken = "auth/auth-token";

// const endpointMangaCollectionIndex = "manga/collection-index";
// const endpointMangaMetaDataByTitle = "manga/metadata";
// const endpointMangaChaptersByTitle = "manga/chapters";

const endpointVideoCollectionIndex = "video/collection-index";
const endpointVideoMetaDataByTitle = "video/metadata";
const endpointVideoEpisodesByTitle = "video/episodes";
// const endpointSubtitleSelections = "video/subtitle-selections";
// const endpointSubtitlesChewieFmt = "video/subtitles-chewie";

// Known Paths
// const pathManga = "manga";
const pathVideo = "video";
// const pathMusic = "music";
// const pathImage = "images";
// const pathSubtitles = "subtitles";
// const pathMangaThumbnail = "lux-assets/thumbnails/manga/";
// const pathMangaCoverArt = "lux-assets/covers/manga/";
// const pathVideoThumbnail = "lux-assets/thumbnails/video/";
// const pathVideoCoverArt = "lux-assets/covers/video/";
// const pathMusicThumbnail = "lux-assets/thumbnails/music/";
// const pathMusicCoverArt = "lux-assets/covers/music/";

// TODO: This is jank af. Have this be a local resource
//       The reason it is currently not, is because the list is a list of
//       Network images. So, you'd need to find some common class, etc...
// const endpointBlackPng = "public/assets/images/_black.png";

/**
 * Convert a JWT to a signed folder used on the server side.
 * This is where our authorized data will be.
 * @param {string} jwt
 * @returns {string}
 */
function convertJWTToSignedFolder(jwt) {
  if (jwt.length < 25) {
    return jwt;
  }
  return jwt.substring(jwt.length - 25);
}

/**************************
 * Server Auth Endpoints
 **************************/

/**
 * Get the pepper from the server.
 * @param {string} serverPort Defaults to 8081
 * @returns {string} The pepper from the server.
 * @throws {Error} If the server does not respond, or the response is not 200.
 */
export async function getPepper(serverPort = defaultServerPort) {
  const response = await axios.get(
    `http://${serverIP}:${serverPort}/${endpointGetPepper}`,
    {
      timeout: serverTimeoutSeconds * 1000,
    }
  );

  console.log(response);

  if (response.status !== 200) {
    throw new Error(response.data);
  }

  return response.data;
}

/**
 * Get the JWT auth token from the server.
 * @param {string} pwd The password to hash.
 * @param {string} pepper The pepper to hash with.
 * @param {string} serverPort Defaults to 8081
 * @returns {string} The JWT auth token from the server.
 * @throws {Error} If the server does not respond, or the response is not 200.
 */
export async function getAuthToken(
  pwd,
  pepper,
  serverPort = defaultServerPort
) {
  // Hash the password
  const hashedPassword = await hash(pwd, pepper);

  // Send the request to the server
  const response = await axios.post(
    `http://${serverIP}:${serverPort}/${endpointGetAuthToken}`,
    {
      pwdHash: hashedPassword,
    },
    {
      timeout: serverTimeoutSeconds * 1000,
    }
  );

  if (response.status !== 200) {
    throw new Error(response.data);
  }

  return response.data;
}

/**************************
 * Video Endpoints
 **************************/

/**
 * Retrieve a url for the specified video's thumbnail art.
 * @param {AuthContext} auth Contains token, server.
 * @param {String} title Title of the video.
 * @returns {String} URL to the thumbnail art for the video.
 */
export function getVideoThumbnailURL(auth, title) {
  if (!auth) return null;
  const port = defaultServerPort;
  const signedFolder = convertJWTToSignedFolder(auth.token);
  return `http://${serverIP}:${port}/public/${signedFolder}/lux-assets/thumbnail/video/${title}.jpg`;
}

/**
 * Retrieve a url for the specified video's cover art.
 * @param {AuthContext} auth Contains token, server.
 * @param {String} title Title of the video.
 * @returns {String} URL to the cover art for the video.
 */
export function getVideoCoverURL(auth, title) {
  if (!auth) return null;
  const port = defaultServerPort;
  const signedFolder = convertJWTToSignedFolder(auth.token);
  return `http://${serverIP}:${port}/public/${signedFolder}/lux-assets/covers/video/${title}.jpg`;
}

/**
 * Retrieve a url for the specified video.
 * @param {AuthContext} auth Contains token, server.
 * @param {String} seriesTitle Title of the series.
 * @param {String} episodeTitle Title of the episode.
 * @returns {String} URL to the video, or null if auth is null.
 */
export function getVideoURL(auth, seriesTitle, episodeTitle) {
  if (!auth) return null;
  const port = defaultServerPort;
  const signedFolder = convertJWTToSignedFolder(auth.token);
  return `http://${serverIP}:${port}/public/${signedFolder}/${pathVideo}/${seriesTitle}/${episodeTitle}`;
}

/**
 * Get the video metadata for a given list of titles.
 * @param {String} token JWT token for auth.
 * @param {String} serverPort (Optional) Port of the endpoint (default: 8081)
 * @returns {List<VideoMetaData>} List of VideoMetaData objects representing
 *                                each of the available titles.
 *                                Each VideoMetaData object will have limited
 *                                data: title, nsfw, yearstart, description.
 */
export async function getVideoCollectionIndex(
  token,
  serverPort = defaultServerPort
) {
  const response = await axios.get(
    `http://${serverIP}:${serverPort}/${endpointVideoCollectionIndex}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (response.status !== 200) {
    throw new Error(response.status);
  }

  // Parse the response in VideoMetaData objects
  const videoMetaDataList = [];
  for (const metadata of response.data) {
    videoMetaDataList.push(new VideoMetaData(metadata));
  }

  return videoMetaDataList;
}

/**
 * Get the video metadata for a given list of titles.
 * @param {List<String>} titles List of titles whose data we need.
 * @param {String} token JWT token for auth.
 * @param {String} serverPort (Optional) Port of the endpoint (default: 8081)
 * @returns {List<VideoMetaData>} List of VideoMetaData objects for each of the
 *                                requested titles.
 */
export async function getVideoMetaDataByTitle(
  titles,
  token,
  serverPort = defaultServerPort
) {
  const titlesStr = titles.join(",");
  const response = await axios.get(
    `http://${serverIP}:${serverPort}/${endpointVideoMetaDataByTitle}?titles=${titlesStr}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  // NOTE: 207 means the status is per data item. So, we need to check each
  //       item individually.
  if (response.status !== 207) {
    throw new Error(response.status);
  }

  // Parse the response in VideoMetaData objects
  const videoMetaDataList = [];
  for (const statusDataPair of response.data) {
    if (statusDataPair?.status !== 200) {
      videoMetaDataList.push(null);
      continue;
    }
    const metadata = statusDataPair?.data;
    videoMetaDataList.push(new VideoMetaData(metadata));
  }

  return videoMetaDataList;
}

/**
 * Get the list of episodes available for each of the provided titles.
 * @param {List<String>} titles List of titles whose data we need.
 * @param {String} token JWT token for auth.
 * @param {String} serverPort (Optional) Port of the endpoint (default: 8081)
 * @returns {List<List<String>>} For each episode, a list of available episodes.
 */
export async function getVideoEpisodesByTitle(
  titles,
  token,
  serverPort = defaultServerPort
) {
  const titlesStr = titles.join(",");
  const response = await axios.get(
    `http://${serverIP}:${serverPort}/${endpointVideoEpisodesByTitle}?titles=${titlesStr}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  // NOTE: 207 means the status is per data item. So, we need to check each
  //       item individually.
  if (response.status !== 207) {
    throw new Error(response.status);
  }

  // Parse the response in VideoMetaData objects
  const episodeLists = [];
  for (const statusDataPair of response.data) {
    if (statusDataPair?.status !== 200) {
      episodeLists.push(null);
      continue;
    }
    const episodeList = statusDataPair?.data;
    episodeLists.push(episodeList);
  }

  return episodeLists;
}
