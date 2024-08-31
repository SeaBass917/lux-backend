import { Button } from "@mui/material";
import { useTheme } from "@mui/material/styles";

function BlackListLandingPage() {
  const theme = useTheme();

  return (
    <div
      className="BlackListLandingPage"
      style={{
        backgroundColor: theme.palette.secondary.dark,
        color: theme.palette.primary.contrastText,
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        textAlign: "center",
        padding: "0 10vw",
      }}
    >
      <div style={{ marginBottom: "20px" }}>
        <h1>Sorry, something is wrong on the server side.</h1>
        <p>
          Try going back to see if it fixes the problem. If not, you may need to
          investigate the server status.
        </p>
      </div>
      <Button variant="contained" color="secondary" href="/">
        Go Home
      </Button>
    </div>
  );
}

export default BlackListLandingPage;
