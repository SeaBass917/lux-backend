import axios from "axios";
import { getPepper, getAuthToken } from "../Server/ServerInterface";

jest.mock("axios");

test("getPepper - Happy Path", async () => {
  const serverIP = "123.456.789.0";
  const serverPepper = "$2b$10$EwPepper00000000000000";

  // Mock the axios get call
  axios.get.mockResolvedValue({
    status: 200,
    data: serverPepper,
  });

  // Call the function
  await expect(getPepper(serverIP)).resolves.toEqual(serverPepper);
});

test("getPepper - Server Error", async () => {
  const serverIP = "123.456.789.0";
  const serverErrMsg = "Server is missing JWT secret key.";

  // Mock the axios get call to return a server error
  axios.get.mockResolvedValue({
    status: 500,
    data: serverErrMsg,
  });

  // Call the function
  await expect(getPepper(serverIP)).rejects.toThrow(serverErrMsg);
});

test("getPepper - On the blacklist", async () => {
  const serverIP = "123.456.789.0";
  const serverErrMsg = "This IP has been blacklisted.";

  // Mock the axios get call to return a server error
  axios.get.mockResolvedValue({
    status: 403,
    data: serverErrMsg,
  });

  // Call the function
  await expect(getPepper(serverIP)).rejects.toThrow(serverErrMsg);
});

test("getAuthToken - Happy Path", async () => {
  const serverIP = "123.456.789.0";
  const password = "OohPassword";
  const serverPepper = "$2b$10$EwPepper0000000000000000000000000000";
  const serverToken = "WowSuchToken123456789123456789123456789123456789";

  // Mock the axios get call
  axios.post.mockResolvedValue({
    status: 200,
    data: serverToken,
  });

  // Call the function
  await expect(getAuthToken(serverIP, password, serverPepper)).resolves.toEqual(
    serverToken
  );
});

test("getAuthToken - Server Error", async () => {
  const serverIP = "123.456.789.0";
  const password = "OohPassword";
  const serverPepper = "$2b$10$EwPepper00000000000000";
  const serverErrMsg = "Server failed to read password hash.";

  // Mock the axios get call to return a server error
  axios.post.mockResolvedValue({
    status: 500,
    data: serverErrMsg,
  });

  // Call the function
  await expect(getAuthToken(serverIP, password, serverPepper)).rejects.toThrow(
    serverErrMsg
  );
});

test("getAuthToken - On the blacklist", async () => {
  const serverIP = "123.456.789.0";
  const password = "OohPassword";
  const serverPepper = "$2b$10$EwPepper00000000000000";
  const serverErrMsg = "This IP has been blacklisted.";

  // Mock the axios get call to return a server error
  axios.post.mockResolvedValue({
    status: 403,
    data: serverErrMsg,
  });

  // Call the function
  await expect(getAuthToken(serverIP, password, serverPepper)).rejects.toThrow(
    serverErrMsg
  );
});

test("getAuthToken - Wrong password", async () => {
  const serverIP = "123.456.789.0";
  const password = "OohPassword";
  const serverPepper = "$2b$10$EwPepper00000000000000";
  const serverErrMsg = "Invalid password hash.";

  // Mock the axios get call to return a server error
  axios.post.mockResolvedValue({
    status: 401,
    data: serverErrMsg,
  });

  // Call the function
  await expect(getAuthToken(serverIP, password, serverPepper)).rejects.toThrow(
    serverErrMsg
  );
});
