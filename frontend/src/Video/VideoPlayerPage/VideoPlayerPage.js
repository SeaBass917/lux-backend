import { useContext, useRef, useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import ReactPlayer from "react-player";
import { Button, Collapse, useTheme } from "@mui/material";
import { ArrowBack, ArrowForward } from "@mui/icons-material";

import { AuthContext } from "../../Auth/AuthContext";
import { EpisodeContext } from "../VideoEpisodeList/EpisodeListContext";
import { getVideoURL } from "../../Server/ServerInterface";
import TopNavBar from "../../TopNavBar/TopNavBar";
import {
  VideoEpisodeList,
  cleanEpisodeTitle,
} from "../VideoEpisodeList/VideoEpisodeList";
import "./VideoPlayerPage.css";

function VideoPlayerPage() {
  const { auth } = useContext(AuthContext);
  const { seriesTitle, episodeTitle } = useParams();
  // const [playing, setPlaying] = useState(true);
  const player = useRef();
  const [episodeList, setEpisodeList] = useState(null);
  const [currIndex, setCurrIndex] = useState(-1);

  const theme = useTheme();

  // Once the episodes are loaded in, set the current episode index by
  // Searching the episode list for the current episode
  useEffect(() => {
    if (episodeList) {
      for (let i = 0; i < episodeList.length; i++) {
        if (episodeList[i] === episodeTitle) {
          setCurrIndex(i);
          break;
        }
      }
    }
  }, [episodeList, episodeTitle]);

  /**
   *  Returns true if the previous button should be enabled.
   *    - Episode list is loaded
   *    - Episode list is not empty
   *    - Current index is valid (i.e. not -1 or out of bounds)
   *    - Current index is not the first episode
   *  @returns {boolean} true if the previous button should be enabled.
   */
  function isPrevButtonValid() {
    const isEpisodeListValid = episodeList && episodeList.length > 0;
    const isCurrIndexValid = 0 < currIndex && currIndex < episodeList.length;
    return isEpisodeListValid && isCurrIndexValid;
  }

  /**
   *  Returns true if the next button should be enabled.
   *    - Episode list is loaded
   *    - Episode list is not empty
   *    - Current index is valid (i.e. not -1 or out of bounds)
   *    - Current index is not the last episode
   *  @returns {boolean} true if the next button should be enabled.
   */
  function isNextButtonValid() {
    const isEpisodeListValid = episodeList && episodeList.length > 0;
    const isCurrIndexValid =
      0 <= currIndex && currIndex < episodeList.length - 1;
    return isEpisodeListValid && isCurrIndexValid;
  }

  return (
    <div className="VideoPlayerPage">
      <TopNavBar />
      <ReactPlayer
        url={getVideoURL(auth, seriesTitle, episodeTitle)}
        controls={true}
        playing
        width={"50%"}
        height={"auto"}
        volume={0.05}
        ref={player}
        style={{
          margin: "48px auto 0",
        }}
        config={{
          file: {
            attributes: {
              crossOrigin: "use-credentials",
              preload: "auto",
            },
            forceVideo: true,
            forceAudio: true,
          },
        }}
      />
      {/* <video controls autoPlay muted>
        <source
          src={getVideoURL(auth, seriesTitle, episodeTitle)}
          type="video/mp4"
        />
      </video> */}
      <div
        className="VideoPlayerPage__navButtonContainer"
        style={{
          margin: "16px 25% 0",
          display: "flex",
          flexDirection: "row",
          justifyContent: "space-between",
        }}
      >
        <Collapse in={isPrevButtonValid()}>
          <Button
            sx={{
              justifyContent: "center",
            }}
            className="VideoInfoPage__watchingButton"
            variant="contained"
            color="primaryDark"
            onClick={() => {
              if (!isPrevButtonValid()) {
                return;
              }
              const prevEpisode = episodeList[currIndex - 1];
              window.location.href = `/video/${seriesTitle}/${prevEpisode}`;
            }}
            disabled={!isPrevButtonValid()}
          >
            <ArrowBack />
            Previous
          </Button>
        </Collapse>

        <Collapse in={isNextButtonValid()}>
          <Button
            sx={{
              justifyContent: "center",
            }}
            className="VideoInfoPage__watchingButton"
            variant="contained"
            color="primaryDark"
            onClick={() => {
              if (!isNextButtonValid()) {
                return;
              }
              const nextEpisode = episodeList[currIndex + 1];
              window.location.href = `/video/${seriesTitle}/${nextEpisode}`;
            }}
            disabled={!isNextButtonValid()}
          >
            Next
            <ArrowForward />
          </Button>
        </Collapse>
      </div>
      <div className="VideoPlayerPage__titleContainer">
        <div>
          <h3
            style={{
              color: theme.palette.primary.main,
            }}
            onClick={() => {
              window.location.href = `/video/${seriesTitle}`;
            }}
          >
            {seriesTitle}
          </h3>
          <h2>{cleanEpisodeTitle(episodeTitle)}</h2>
        </div>
      </div>
      <Collapse in={isPrevButtonValid() || isNextButtonValid()}>
        <EpisodeContext.Provider value={{ episodeList, setEpisodeList }}>
          <VideoEpisodeList />
        </EpisodeContext.Provider>
      </Collapse>
    </div>
  );
}

export default VideoPlayerPage;
