import { useContext, useRef, useState } from "react";
import { useTheme } from "@emotion/react";

import { Button } from "@mui/material";
import { ArrowBackIos, ArrowForwardIos } from "@mui/icons-material";

import { AuthContext } from "../../Auth/AuthContext";
import { VideoCard, cardWidth, cardHeight, cardMarginRight } from "./VideoCard";
import "./HorizontalScrollSection.css";

function HorizontalScrollSection({ title, metaDataList }) {
  const scrollContainerRef = useRef(null);
  const [isLeftScrollButtonVisible, setIsLeftScrollButtonVisible] =
    useState(false);
  const [isRightScrollButtonVisible, setIsRightScrollButtonVisible] =
    useState(true);
  const { auth } = useContext(AuthContext);

  // Constants for the component
  const containerPadding = 32;

  /**
   * Scroll the container by a fixed amount.
   * If left is true, scroll left. Otherwise, scroll right.
   * Scrolling will be in increments of the card length,
   * we should not scroll and hit the middle of a card.
   */
  const scrollFixedDistance = (left = false) => {
    const factor = left ? -1 : 1;
    const posCurrent = scrollContainerRef.current.scrollLeft;
    const totalCardSpace = cardWidth + cardMarginRight;

    // Scroll up to the last card visible
    const scrollAmount =
      Math.floor(window.innerWidth / totalCardSpace) * totalCardSpace;

    // Adjust the scroll amount so that we don't scroll to the middle of a card
    const scrollAmountAdjusted =
      scrollAmount - factor * (posCurrent % totalCardSpace);

    // Jump to that scroll position
    scrollContainerRef.current.scrollTo({
      left: posCurrent + factor * scrollAmountAdjusted,
      behavior: "smooth",
    });
  };

  /**
   * Check both scroll buttons to see if they should be visible,
   * and set their visibility accordingly.
   */
  const setScrollButtonVisibility = () => {
    const { scrollLeft, scrollWidth, offsetWidth } = scrollContainerRef.current;
    setIsLeftScrollButtonVisible(scrollLeft > 0);
    setIsRightScrollButtonVisible(scrollLeft < scrollWidth - offsetWidth);
  };

  const theme = useTheme();

  return (
    <div
      className="HorizontalScrollSection"
      style={{
        padding: `0 ${containerPadding}px`,
      }}
    >
      <h1>{title}</h1>
      <div style={{ display: "flex", position: "relative" }}>
        {isLeftScrollButtonVisible && (
          <Button
            style={{
              alignSelf: "flex-start",
              position: "absolute",
              left: -32,
              top: 0,
              zIndex: 1,
              height: `${cardHeight * 0.74}px`,
              background:
                "linear-gradient(to right, rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.05))",
            }}
            onClick={() => {
              scrollFixedDistance(true);
            }}
          >
            <ArrowBackIos
              style={{
                transform: "translateX(5px)",
                color: theme.palette.primary.light,
              }}
            />
          </Button>
        )}
        <div
          className="HorizontalScrollSection__container"
          ref={scrollContainerRef}
          onScroll={() => setScrollButtonVisibility()}
        >
          {metaDataList.map((metaData, index) => (
            <VideoCard
              key={index}
              title={metaData.title}
              yearStart={metaData.yearStart}
              description={metaData.description}
              auth={auth}
            />
          ))}
        </div>
        {isRightScrollButtonVisible && (
          <Button
            style={{
              alignSelf: "center",
              position: "absolute",
              right: -32,
              top: 0,
              height: `${cardHeight * 0.74}px`,
              background:
                "linear-gradient(to left, rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.05))",
            }}
            onClick={() => {
              scrollFixedDistance(false);
            }}
          >
            <ArrowForwardIos
              style={{
                color: theme.palette.primary.light,
              }}
            />
          </Button>
        )}
      </div>
    </div>
  );
}

export default HorizontalScrollSection;
