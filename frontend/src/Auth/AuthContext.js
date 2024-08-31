import React, { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState({
    pepper: localStorage.getItem("pepper"),
    token: localStorage.getItem("token"),
  });

  useEffect(() => {
    if (auth.pepper) {
      localStorage.setItem("pepper", auth.pepper);
    } else {
      localStorage.removeItem("pepper");
    }
    if (auth.token) {
      localStorage.setItem("token", auth.token);
    } else {
      localStorage.removeItem("token");
    }
  }, [auth]);

  return (
    <AuthContext.Provider value={{ auth, setAuth }}>
      {children}
    </AuthContext.Provider>
  );
};
