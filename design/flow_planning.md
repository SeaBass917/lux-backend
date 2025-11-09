# Main Paths

## Deploy The Backend

- Deploy the backend on your server
  - Create a lux User.
  - Set up the docker-compose to start in that dedicated user on startup.

## Connecting a new Client (Mobile)

- Install the mobile app
- Opening for the first time.
- Connect you to your server.
  - After connecting a key will be stored to re-connect you going forward.
  - Enter the Public IP address of your server, and submit.
  - Server will take the request, reply with a key, and await confirmation.
    - Make sure it's noted that repeated attempts to connect can cause blacklisting.
  - We will store that key for future requests.
  - Open an in-app web client (link to this) Log in to the Command Center. `https://{theIP}:{thePort}/admin/`
    - Confirm the request.
    - You will be auto mnav-ed back to the app on the log in page.
  - You will be logged in using the key.

## Connecting a new Client (Web)

# Additional Flows

## Refreshing Key or Server Changed Address

- Some sort of wording about refreshing the key and what it means.
- Should roughly pipe through the same process as [Connecting a new Client (Mobile)](#connecting-a-new-client-mobile) and [Connecting a new Client (Web)](#connecting-a-new-client-web)
  It's just gunna differ in the backend a bit since the backend should know now to prune previous connection info to this device.

## Auth Failed

There is a key present on your device, the server is responding, the key is invalid.

## Server Offline

Present a list of troubleshooting steps, at the same level that presents the option "This is expected, let me reconnect to a new address w/ a new key".

- If the 2nd option is selected just go to flow [Refreshing Key or Server Changed Address](#refreshing-key-or-server-changed-address)
- Otherwise the troubleshooting steps:
  - Is server online? (_Ping tool from here?.. We could just see if it is and tell them the status_)
  - Is the task running? (_how to check_)
  - Did the system f\*\*\* up and accidentally black list your IP?? (_If I haven't fixed that issue by the time I write this_)
  - ...
