import { useEffect, useContext, useState } from "react";

import { AxiosError } from "axios";

import { AuthContext } from "../../Auth/AuthContext";
import GridScrollSection from "./GridScrollSection";
import HorizontalScrollSection from "./HorizontalScrollSection";
import { getVideoCollectionIndex } from "../../Server/ServerInterface";
import TopNavBar from "../../TopNavBar/TopNavBar";
import "./VideoHomepage.css";

function VideoHomepage() {
  const { auth, setAuth } = useContext(AuthContext);
  const [metaDataList, setMetaDataList] = useState([]);

  useEffect(() => {
    // If the user is not logged in, redirect them to the landing page
    if (auth.token === null) {
      window.location.href = "/";
      return;
    }

    // Get the videos from the server
    getVideoCollectionIndex(auth.token, auth.server)
      .then((videoCollectionIndex) => {
        setMetaDataList(videoCollectionIndex);
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
        }
        console.error(err);
      });
  }, [auth, setAuth]);

  return (
    <div className="VideoHomepage">
      <TopNavBar />
      <div
        style={{
          margin: "32px",
        }}
      >
        <HorizontalScrollSection
          title="Recently Watched"
          // TODO: This is a faux list for spacing right now, recently watched
          // should be implemented in the future.
          metaDataList={metaDataList.slice(0, 15)}
        />
        <HorizontalScrollSection
          title="What's new"
          metaDataList={metaDataList
            .sort((a, b) => {
              return b.dateAdded - a.dateAdded;
            })
            .slice(0, 15)}
        />
        <GridScrollSection
          title="All Videos"
          metaDataList={metaDataList.sort((a, b) => {
            return a.title.localeCompare(b.title);
          })}
        />
      </div>
    </div>
  );
}

export default VideoHomepage;
