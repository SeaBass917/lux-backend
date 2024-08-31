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
        <h1>This IP has been blacklisted.</h1>
        <p>
          If you are authorized to access this server, you can simply remove
          this IP from the blacklist.
        </p>
        <p>Otherwise, go away stinky.</p>
      </div>
      <Button variant="contained" color="secondary" href="/">
        Go Home
      </Button>
    </div>
  );
}

export default BlackListLandingPage;
