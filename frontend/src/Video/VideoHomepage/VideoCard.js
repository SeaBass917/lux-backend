import { useTheme } from "@emotion/react";
import { getVideoCoverURL } from "../../Server/ServerInterface";
import "./VideoCard.css";

// Constants for the child cards
const cardWidth = 400;
const cardHeight = 300;
const cardMarginRight = 16;
const cardMarginBottom = 16;

function VideoCard({ title, yearStart, description, auth }) {
  const theme = useTheme();

  return (
    <div
      className="VideoCard"
      style={{
        width: `${cardWidth}px`,
        minWidth: `${cardWidth}px`,
        maxWidth: `${cardWidth}px`,
        height: `${cardHeight}px`,
        marginRight: `${cardMarginRight}px`,
        display: "flex",
        flexDirection: "column",
        userSelect: "none",
        marginBottom: `${cardMarginBottom}px`,
        cursor: "pointer",
        position: "relative",
      }}
      onClick={() => {
        window.location.href = `/video/${title}`;
      }}
    >
      <img
        src={getVideoCoverURL(auth, title)}
        alt={title}
        style={{
          height: "85%",
          width: "100%",
          marin: "auto",
          display: "block",
          objectFit: "cover",
          overflow: "hidden",
        }}
      />
      <div
        id="VideoCard__title"
        style={{
          height: "30%",
          width: "100%",
          margin: "auto",
          backgroundColor: "transparent",
          display: "flex",
          alignItems: "top",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "row",
          }}
        >
          <h2
            style={{
              margin: "10px 0 0 0",
              padding: "0",
              textAlign: "left",
              alignSelf: "flex-start",
              width: "100%",
              color: theme.palette.text.primary,
              whiteSpace: "nowrap",
            }}
          >
            {title}
          </h2>
          {yearStart && (
            <h2
              style={{
                margin: "10px 0 0 5px",
                padding: "0",
                textAlign: "left",
                alignSelf: "flex-start",
                width: "100%",
                color: theme.palette.text.disabled,
              }}
            >
              ({yearStart})
            </h2>
          )}
        </div>
      </div>
      <div
        className="VideoCard__description"
        onMouseEnter={(e) => {
          e.target.scrollTop = 0;
        }}
      >
        <p>{description}</p>
      </div>
    </div>
  );
}

export { VideoCard, cardWidth, cardHeight, cardMarginRight };
