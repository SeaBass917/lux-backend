import "./TopNavBar.css";
import logo from "../assets/imgs/tibix-logo.png";
import { useEffect } from "react";

function TopNavBar() {
  useEffect(() => {
    // Set the current tab as the selected tab
    const currentTab = window.location.pathname;

    // Safety check to make sure we are on a valid tab
    if (!currentTab.startsWith("/") || currentTab.length < 2) {
      return;
    }

    // Extract only the first part of the path,
    // e.g. "/video/foo/bar" -> "video"
    const currentTabName = currentTab.substring(1).split("/")[0];

    // Get the tab element
    const currentTabElement = document.getElementById(currentTabName);
    if (currentTabElement === null) {
      return;
    }

    // Add the selected class
    currentTabElement.classList.add("NavSelected");
  }, []);

  return (
    <div className="TopNavBar">
      <div className="NavSector" id="navPaddingBegin"></div>
      <div
        className="NavSector"
        id="logo"
        onClick={(_) => {
          // Check to see that we are not already there
          if (window.location.pathname === "/") {
            return;
          }
          window.location.href = "/";
        }}
      >
        <img src={logo} id="logoImg" alt="Lux Logo"></img>
        <h1 id="logoText">Lux</h1>
      </div>
      <div
        className="NavSector NavTab"
        id="video"
        onClick={(_) => {
          // Check to see that we are not already there
          if (window.location.pathname === "/video") {
            return;
          }

          window.location.href = "/video";
        }}
      >
        <div>
          <h3>Video</h3>
        </div>
      </div>
      <div
        className="NavSector NavTab"
        id="manga"
        onClick={(_) => {
          // Check to see that we are not already there
          if (window.location.pathname === "/manga") {
            return;
          }

          window.location.href = "/manga";
        }}
      >
        <div>
          <h3>Manga</h3>
        </div>
      </div>
      <div
        className="NavSector NavTab"
        id="music"
        onClick={(_) => {
          // Check to see that we are not already there
          if (window.location.pathname === "/music") {
            return;
          }

          window.location.href = "/music";
        }}
      >
        <div>
          <h3>Music</h3>
        </div>
      </div>
      <div
        className="NavSector NavTab"
        id="images"
        onClick={(_) => {
          // Check to see that we are not already there
          if (window.location.pathname === "/images") {
            return;
          }

          window.location.href = "/images";
        }}
      >
        <div>
          <h3>Images</h3>
        </div>
      </div>
    </div>
  );
}

export default TopNavBar;
