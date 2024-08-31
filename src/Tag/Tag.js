import { Chip } from "@mui/material";

const tagColors = [
  "#1f77b4",
  "#ff7f0e",
  "#2ca02c",
  "#d62728",
  "#9467bd",
  "#8c564b",
  "#e377c2",
  "#bcbd22",
  "#17becf",
  "#4e79a7",
  "#f28e2c",
  "#e15759",
  "#76b7b2",
  "#59a14f",
  "#edc949",
  "#af7aa1",
  "#ff9da7",
  "#9c755f",
];

function getTagColor(tag) {
  let hash = 0;
  for (let i = 0; i < tag.length && i < 3; i++) {
    hash = hash + tag.charCodeAt(i);
  }
  return tagColors[hash % tagColors.length];
}

function GenreTag({ text }) {
  return (
    <div className="GenreTag">
      <Chip
        label={text}
        variant="outlined"
        style={{
          margin: "4px",
          borderWidth: "4px",
          fontSize: "18px",
          borderColor: getTagColor(text),
          userSelect: "none",
        }}
      />
    </div>
  );
}

export default GenreTag;
