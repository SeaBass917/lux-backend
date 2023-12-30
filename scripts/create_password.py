# ============================================================================ #
#
#                             Copyright (c) 2023
#                               Sebastian Thiem
#
#                 Permission is hereby granted, free of charge,
#                to any person obtaining a copy of this software
#              and associated documentation files (the "Software"),
#                 to deal in the Software without restriction,
#                 including without limitation the rights to
#            use, copy, modify, merge, publish, distribute, sublicense,
#                     and/or sell copies of the Software,
#         and to permit persons to whom the Software is furnished to do so,
#                    subject to the following conditions:
#
#     The above copyright notice and this permission notice shall be included
#             in all copies or substantial portions of the Software.
#
#         THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#               EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
#                      THE WARRANTIES OF MERCHANTABILITY,
#             FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#             IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
#               LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#              WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#            ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
#                 OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ============================================================================ #
#
# Description:  Help a user create a new media server password.
#
# ============================================================================ #
from bcrypt import hashpw
from getpass import getpass

from dotenv import load_dotenv
import os
load_dotenv(".secrets.env")


def is_password_secure(password: str) -> str | None:
    """Check to see if the password is secure enough.
    Currently that means it is at least 8 characters long.

    Args:
        password (str): The password to check.

    Returns:
        bool: True if the password is secure, false if not.
    """
    common_passwords_30 = [
        "123456", "password", "123456789", "12345", "12345678", "qwerty",
        "1234567", "111111", "1234567890", "123123", "abc123", "1234",
        "password1", "iloveyou", "1q2w3e4r", "000000", "qwerty123", "zaq12wsx",
        "dragon", "sunshine", "princess", "letmein", "654321", "monkey",
        "27653", "1qaz2wsx", "123321", "qwertyuiop", "superman", "asdfghjkl"
    ]

    if len(password) < 8:
        return "Password must be at least 8 characters long."
    elif password in common_passwords_30:
        return "That password is not allowed. Too easy to guess."

    return None


def get_pepper():
    """ Get the pepper from the environment variable.

    Returns:
        str|None: The pepper.
    """
    return os.getenv('PASSWORD_PEPPER')


def create_password(pw_file: str):
    """Create a new password for the media server.
    Store the password in `.pwd_hash`

    pw_file (str): The file to store the password in.
    """

    while True:

        # Get the password from the user
        password = getpass("Enter a new password: ")

        # Check to see if the password is secure
        if err := is_password_secure(password):
            print(err)
            continue

        # Ask the user to confirm the password
        password_confirm = getpass("Confirm the password: ")

        # Check to see if the passwords match
        if password != password_confirm:
            print("Passwords do not match. Please try again.")
            continue

        # Get the pepper
        pepper = get_pepper()
        if not pepper:
            print("Error! Pepper not found. ")
            print("Please run the server at least once.")
            return

        # Hash the password
        password = password.encode("utf-8")
        pepper = pepper.encode("utf-8")
        hashed = hashpw(password, pepper)

        # Store the password
        with open(pw_file, "wb") as f:
            f.write(hashed)

        print("Password successfully created.")
        return


def main():
    """Main entry point for the script."""
    pw_file = ".pwd_hash"

    # Inform user if password already exists
    if os.path.exists(pw_file):
        print("Warning. Password already on file. "
              "Continuing will overwrite the existing password.")

    create_password(pw_file)


if __name__ == "__main__":
    main()
