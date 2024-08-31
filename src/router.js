import { createBrowserRouter } from "react-router-dom";

import LandingPage from "./LandingPage/LandingPage";
import VideoHomepage from "./Video/VideoHomepage/VideoHomepage";
import BlackListLandingPage from "./ErrorLandingPages/BlackListLandingPage";
import ServerErrorLandingPage from "./ErrorLandingPages/ServerErrorLandingPage";
import VideoInfoPage from "./Video/VideoInfoPage/VideoInfoPage";
import MangaHomepage from "./Manga/MangaHomepage/MangaHomepage";
import MusicHomepage from "./Music/MusicHomepage/MusicHomepage";
import ImageHomepage from "./Image/ImageHomepage/ImageHomepage";
import VideoPlayerPage from "./Video/VideoPlayerPage/VideoPlayerPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage />,
  },
  {
    path: "/video",
    element: <VideoHomepage />,
  },
  {
    path: "/manga",
    element: <MangaHomepage />,
  },
  {
    path: "/music",
    element: <MusicHomepage />,
  },
  {
    path: "/images",
    element: <ImageHomepage />,
  },
  {
    path: "/blacklist",
    element: <BlackListLandingPage />,
  },
  {
    path: "/server-error",
    element: <ServerErrorLandingPage />,
  },
  {
    path: "/video/:seriesTitle",
    element: <VideoInfoPage />,
  },
  {
    path: "/video/:seriesTitle/:episodeTitle",
    element: <VideoPlayerPage />,
  },
]);

export default router;
