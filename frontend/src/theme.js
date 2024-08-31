import { createTheme } from "@mui/material";

const theme = createTheme({
  palette: {
    primary: {
      main: "#C5A0FC",
      light: "#E4D1FF",
      dark: "#37364F",
      contrastText: "#F9F9FF",
    },
    primaryDark: {
      main: "#4c3f61",
      light: "#5b4f71",
      dark: "#322941",
      contrastText: "#F9F9FF",
    },
    secondary: {
      main: "#5A5884",
      light: "#9C99F0",
      dark: "#4C4B6A",
      contrastText: "#F9F9FF",
    },
    text: {
      primary: "#F9F9FF",
      secondary: "#C8C8CC",
      disabled: "#A5A5A5",
    },
    error: {
      main: "#f76666",
    },
  },
  typography: {
    fontFamily: ["Satoshi", "Roboto", "sans-serif"].join(","),
  },
});

export default theme;
