import { useContext, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Button, useTheme } from "@mui/material";
import { PlayArrow } from "@mui/icons-material";

import { AxiosError } from "axios";

import { AuthContext } from "../../Auth/AuthContext";
import { EpisodeContext } from "../VideoEpisodeList/EpisodeListContext";
import {
  getVideoCoverURL,
  getVideoMetaDataByTitle,
} from "../../Server/ServerInterface";
import GenreTag from "../../Tag/Tag";
import TopNavBar from "../../TopNavBar/TopNavBar";
import { VideoEpisodeList } from "../VideoEpisodeList/VideoEpisodeList";
import "./VideoInfoPage.css";

function VideoInfoPage() {
  const { auth, setAuth } = useContext(AuthContext);
  const [metaData, setMetaData] = useState(null);
  const { seriesTitle } = useParams();
  const theme = useTheme();
  const [episodeList, setEpisodeList] = useState(null);

  // Constants for the page
  const coverImgHeight = 700;
  const coverImgBlurRadius = 2;

  useEffect(() => {
    console.log(episodeList);
  }, [episodeList]);

  // Grab the metadata and the list of episodes from the server
  // once we have auth loaded.
  useEffect(() => {
    // If the user is not logged in, redirect them to the landing page
    if (auth.token === null) {
      window.location.href = "/";
      return;
    }

    getVideoMetaDataByTitle([seriesTitle], auth.token, auth.server)
      .then((metaDataList) => {
        // If we reach this case, then the server sent bad data
        // on a 200 status code.
        if (metaDataList.length === 0) {
          window.location.href = "/server-error";
          return;
        }
        setMetaData(metaDataList[0]);
      })
      .catch((err) => {
        if (err instanceof AxiosError) {
          const status = err.response?.status;
          if (status === 401) {
            setAuth({
              token: null,
              server: auth.server,
              pepper: auth.pepper,
            });
            return;
          } else if (status === 403) {
            window.location.href = "/blacklist";
            return;
          }

          // All other errors, just redirect to the server error page.
          console.error(err);
          window.location.href = "/server-error";
          return;
        }
      });
  }, [auth, setAuth, seriesTitle]);

  return (
    <div className="VideoInfoPage">
      <TopNavBar />
      <div className="VideoInfoPage__coverArt">
        <div
          className="VideoInfoPage__coverArtBlur"
          style={{
            height: `${coverImgHeight}px`,
            background: `url("${getVideoCoverURL(
              auth,
              seriesTitle
            )}") no-repeat center center`,
            backgroundSize: "cover",
            filter: `blur(${coverImgBlurRadius}px) saturate(90%)`,
          }}
        ></div>
        <img
          className="VideoInfoPage__coverArtMain"
          src={getVideoCoverURL(auth, seriesTitle)}
          alt={`Cover art depicting ${seriesTitle}.`}
          style={{
            height: `${coverImgHeight + 3 * coverImgBlurRadius}px`,
            transform: `translateY(-${coverImgBlurRadius}px)`,
          }}
        />
        <div
          className="VideoInfoPage__coverArtSpacer"
          style={{
            height: `${coverImgHeight + 3 * coverImgBlurRadius}px`,
            transform: `translateY(-${coverImgBlurRadius}px)`,
          }}
        ></div>
      </div>
      <div className="VideoInfoPage__header">
        <div>
          <div className="VideoInfoPage__title">
            <h1
              id="VideoInfoPage__titleText"
              style={{ color: theme.palette.text.primary }}
            >
              {seriesTitle}
            </h1>
            <h2
              id="VideoInfoPage__yearText"
              style={{
                color: theme.palette.text.disabled,
              }}
            >
              ({(metaData && metaData.yearStart) || "...."})
            </h2>
          </div>
          <div className="VideoInfoPage__studio">
            <h2 style={{ color: theme.palette.text.disabled }}>
              {(metaData && metaData.studio) || "..."}
            </h2>
          </div>
          <div className="VideoInfoPage__tags">
            {metaData &&
              metaData.tags.map((tag, index) => {
                return <GenreTag key={index} text={tag} />;
              })}
          </div>
        </div>
        <div className="VideoInfoPage__watchingButtons">
          <Button
            sx={{
              justifyContent: "flex-start",
            }}
            className="VideoInfoPage__watchingButton"
            variant="contained"
            color="primary"
          >
            <PlayArrow />
            Continue
          </Button>
          <Button
            sx={{
              justifyContent: "flex-start",
            }}
            className="VideoInfoPage__watchingButton"
            variant="outlined"
            color="primary"
            onClick={() => {
              if (!episodeList || episodeList.length === 0) return;
              window.location.href = `/video/${seriesTitle}/${episodeList[0]}`;
            }}
          >
            <PlayArrow />
            Start
          </Button>
        </div>
      </div>
      <div className="VideoInfoPage__description">
        <p
          style={{
            color: theme.palette.text.secondary,
          }}
        >
          {(metaData && metaData.description) || "..."}
        </p>
      </div>
      <EpisodeContext.Provider value={{ episodeList, setEpisodeList }}>
        <VideoEpisodeList />
      </EpisodeContext.Provider>
    </div>
  );
}

export default VideoInfoPage;
