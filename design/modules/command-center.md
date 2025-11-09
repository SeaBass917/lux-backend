# Media Server Command Center

## Big Picture

- Manage the server from a GUI.
- MVP1 Commands:
  - Accept a key exchange request
  - Manage the blacklist
  - Restart the app server
- Auth using the lux user that the app will be running on anyway.

## Setup

- The command center will come in the main app, so after docker-composing it will run.
  - Might as well have it run on the same web server. You're gunna require auth and you'll want the same saftey middleware of the main app anyway...
- We'll do `/admin` cuz we're simple
- Auth is never persisted, you log in every time.
- Landing page will be a Usr: Pwd: type affair
  - Password is plaintext BUT encrypted. This is OK because we are leveraging the OS password system.
    - I would love a nice key exchange algo, but that's work for another day. We are essentially guarding against SSL de-encryption.
      Which is a thing. And I do want that. But not right now.
  - Server will reply with a session token. We don't persist the token in storage just in memory.
