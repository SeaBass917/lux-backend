import { useContext } from "react";
import { useTheme } from "@emotion/react";

import { AuthContext } from "../../Auth/AuthContext";
import { VideoCard } from "./VideoCard";

function GridScrollSection({ title, metaDataList }) {
  const { auth } = useContext(AuthContext);

  // Constants for the component
  const containerPadding = 32;

  const theme = useTheme();

  return (
    <div
      className="GridScrollSection"
      style={{
        padding: `0 ${containerPadding}px`,
      }}
    >
      <h1
        style={{
          color: theme.palette.text.primary,
        }}
      >
        {title}
      </h1>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "space-around",
          overflow: "hidden",
        }}
      >
        {metaDataList.map((metaData, index) => {
          return (
            <VideoCard
              key={index}
              title={metaData.title}
              yearStart={metaData.yearStart}
              description={metaData.description}
              auth={auth}
            />
          );
        })}
      </div>
    </div>
  );
}

export default GridScrollSection;
