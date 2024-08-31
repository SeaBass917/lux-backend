import React from "react";
import ReactDOM from "react-dom/client";

import { AuthProvider } from "./Auth/AuthContext";
import { RouterProvider } from "react-router-dom";
import { ThemeProvider } from "@mui/material";

import "./font.css";
import "./index.css";
import router from "./router";
import theme from "./theme";

// Create a context
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <AuthProvider>
    <ThemeProvider theme={theme}>
      <RouterProvider router={router} />
    </ThemeProvider>
  </AuthProvider>
);
