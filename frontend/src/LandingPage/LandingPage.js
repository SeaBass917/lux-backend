import React, { useContext, useState, useRef, useEffect } from "react";

import { AuthContext } from "../Auth/AuthContext";
import { getPepper, getAuthToken } from "../Server/ServerInterface";
import "./LandingPage.css";

import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Collapse from "@mui/material/Collapse";
import { useTheme } from "@mui/material/styles";
import TextField from "@mui/material/TextField";

function LandingPage() {
  const [alertText, setAlertText] = useState("");
  const [isPasswordValid, setIsPasswordValid] = useState(true);
  const textFieldPasswordRef = useRef();
  const { auth, setAuth } = useContext(AuthContext);

  /**
   * Verify that the password text fits the requirements for a server address.
   * If it does not, set the error message and draw the border around the text
   * input as red.
   * @returns {bool}  True if the password text is valid, false otherwise.
   */
  function validatePassword(setAlert = true) {
    // Get references to the required divs
    const passwordTextInput = document.getElementById("passwordTextInput");
    if (passwordTextInput === null) {
      console.error("Could not find required element(s).");
      setIsPasswordValid(false);
      return false;
    }

    // Grab the server text from the dedicated text box
    const passwordText = passwordTextInput.value.trim();

    // Check that anything was provided
    // If there is a validation error, set the error message.
    // And draw the border around the text input as red.
    if (passwordText === "") {
      if (setAlert) setAlertText("Please provide a password.");
      setIsPasswordValid(false);
      return false;
    }

    // If everything was valid, then clear the error borders.
    // And return true.
    setIsPasswordValid(true);
    setAlertText("");
    return true;
  }

  /**
   * Run validations on the text inputs,
   * then submit the data to the user specified server.
   * @param {React.FocusEvent<HTMLFormElement>} event
   * @returns {void}
   */
  function submitCb(event) {
    // Prevent the page from refreshing.
    // And flag the submit button event so that validations can run.
    event.preventDefault();

    // Run validations on the server address and password.
    if (!validatePassword()) {
      return;
    }

    // Get password string
    const password = textFieldPasswordRef.current.value.trim();

    // Get the pepper for hashing the password
    // Then, get the auth token
    getPepper()
      .then((pepper) => {
        getAuthToken(password, pepper)
          .then((authToken) => {
            // Store the pepper token in the auth context
            // This will trigger a redirect to the video homepage
            setAuth({
              pepper: pepper,
              token: authToken,
            });
          })
          .catch((error) => {
            console.error(error);
            setAlertText("Failed to connect to server.");
          });
      })
      .catch((error) => {
        console.error(error);
        setAlertText("Failed to connect to server.");
      });
  }

  // When the page loads, check if the user is already logged in.
  // If they are, redirect them to the video homepage.
  useEffect(() => {
    if (auth.token) {
      // Redirect to the video homepage
      window.location.href = "/video";
    }
  }, [auth]);

  const theme = useTheme();
  return (
    <div className="LandingPage">
      <h1
        style={{
          color: theme.palette.primary.main,
        }}
      >
        Lux <br /> Media Server
      </h1>

      <form onSubmit={submitCb}>
        <TextField
          id="passwordTextInput"
          type="password"
          label="Password"
          inputRef={textFieldPasswordRef}
          error={!isPasswordValid}
          onFocus={(event) => {
            setIsPasswordValid(true);
          }}
        />
        <Button type="submit" variant="contained" color="secondary">
          Submit
        </Button>
        <Collapse in={alertText !== ""}>
          <Alert severity="error" variant="outlined">
            {alertText}
          </Alert>
        </Collapse>
      </form>
    </div>
  );
}

export default LandingPage;
