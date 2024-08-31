import { render, screen } from "@testing-library/react";
import LandingPage from "./LandingPage";
import { AuthContext } from "../Auth/AuthContext";
import { getPepper, getAuthToken } from "../Server/ServerInterface";

jest.mock("../Server/ServerInterface");

// Helper for rendering with Mock AuthContent
const renderWithAuthContext = (component, authValue) => {
  return {
    ...render(
      <AuthContext.Provider value={authValue}>{component}</AuthContext.Provider>
    ),
  };
};

// Helper for creating a fake local storage
const localStorageMock = (function () {
  let store = {};

  return {
    getItem: function (key) {
      return store[key];
    },
    setItem: function (key, value) {
      store[key] = value.toString();
    },
    clear: function () {
      store = {};
    },
  };
})();

// Patch fix so that navigation does not cause a warning in tests.
beforeEach(() => {
  // Mock window.location.reload
  delete window.location;
  window.location = { reload: jest.fn() };
});

/**
 * Tests that the LandingPage title is present.
 */
test("Title is present", () => {
  const authValue = {
    auth: {
      token: "test-token",
      server: "123.456.789.0",
      pepper: "$2b$10$EwPepper00000000000000",
    },
    setAuth: jest.fn(),
  };

  // When getPepper is called, it will resolve to '$2b$10$EwPepper00000000000000'
  getPepper.mockResolvedValue("$2b$10$EwPepper00000000000000");
  getAuthToken.mockResolvedValue(
    "WowSuchToken123456789123456789123456789123456789"
  );

  const { getByText } = renderWithAuthContext(<LandingPage />, authValue);

  const titleElement = screen.getByText(/Lux Media Server/i);
  expect(titleElement).toBeInTheDocument();
});

/**
 * Tests that the LandingPage correctly grabs the last known IP address from
 * local storage.
 */
test("Loads last known Server Address", () => {
  /**
   * Setup Mocks
   */

  const serverMock = "123.456.789.0";
  const pepperMock = "$2b$10$EwPepper00000000000000";
  const tokenMock = "WowSuchToken123456789123456789123456789123456789";

  // Mock the local storage
  // Set the last known server address to something
  Object.defineProperty(window, "localStorage", {
    value: localStorageMock,
  });
  localStorage.setItem("server", serverMock);
  localStorage.setItem("pepper", pepperMock);
  localStorage.setItem("token", tokenMock);

  // Set Auth Cache to reflect the local storage
  const authValue = {
    auth: {
      server: serverMock,
      pepper: pepperMock,
      token: tokenMock,
    },
    setAuth: jest.fn(),
  };

  // When getPepper is called, it will resolve to '$2b$10$EwPepper00000000000000'
  getPepper.mockResolvedValue(pepperMock);
  getAuthToken.mockResolvedValue(tokenMock);

  // Render the component
  const { getByText } = renderWithAuthContext(<LandingPage />, authValue);
  const serverAddressTextInput = document.getElementById("serverTextInput");
  expect(serverAddressTextInput).toBeInTheDocument();

  // Check that the server address is correct
  expect(serverAddressTextInput.value).toBe(serverMock);
});
