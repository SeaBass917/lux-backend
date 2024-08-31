import { useContext, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Button, Paper, Stack, useTheme } from "@mui/material";
import { PlayArrow } from "@mui/icons-material";

import { AxiosError } from "axios";

import { AuthContext } from "../../Auth/AuthContext";
import { EpisodeContext } from "../VideoEpisodeList/EpisodeListContext";
import { getVideoEpisodesByTitle } from "../../Server/ServerInterface";
import "./VideoEpisodeList.css";

/**
 * Cleans up the episode title by replacing underscores with spaces.
 * And removing the file extension.
 * @param {*} episode
 * @returns
 */
function cleanEpisodeTitle(episode) {
  // Remove the file extension
  const parts = episode.replace(/_/g, " ").split(".");
  if (parts.length > 1) {
    parts.pop(); // Remove the last element
    return parts.join(".");
  }
  return episode;
}

function VideoEpisodeList() {
  const { auth, setAuth } = useContext(AuthContext);
  const { episodeList, setEpisodeList } = useContext(EpisodeContext);

  const { seriesTitle } = useParams();
  const theme = useTheme();

  // Grab the metadata and the list of episodes from the server
  // once we have auth loaded.
  useEffect(() => {
    // If the user is not logged in, redirect them to the landing page
    if (auth.token === null) {
      window.location.href = "/";
      return;
    }

    getVideoEpisodesByTitle([seriesTitle], auth.token, auth.server)
      .then((episodeLists) => {
        // If we reach this case, then the server sent bad data
        // on a 200 status code.
        if (episodeLists.length === 0) {
          window.location.href = "/server-error";
          return;
        }

        setEpisodeList(episodeLists[0]);
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
  }, [auth, setAuth, seriesTitle, setEpisodeList]);

  return (
    <div className="VideoEpisodeList">
      <Stack spacing={2}>
        {episodeList &&
          episodeList.map((episode, index) => {
            return (
              <Paper
                className="VideoInfoPage__episodeCard"
                key={index}
                elevation={3}
                style={{
                  backgroundColor: theme.palette.secondary.main,
                }}
              >
                <Button variant="outlined" color="primary">
                  <PlayArrow />
                </Button>
                <h4
                  className="VideoInfoPage__episodeTitle"
                  style={{
                    color: theme.palette.text.secondary,
                  }}
                  onClick={() => {
                    window.location.href = `/video/${seriesTitle}/${episode}`;
                  }}
                >
                  {cleanEpisodeTitle(episode)}
                </h4>
              </Paper>
            );
          })}
      </Stack>
    </div>
  );
}

export { VideoEpisodeList, cleanEpisodeTitle };
