# **How to Run**
## **Requirements**
Before proceeding, make sure you have the following libraries and packages installed on your system.
Alternatively, you may use the `lib_reqs.txt` text file to install all packages simultaneously.
Use command `pip install -r lib_reqs.txt` on your command prompt.
- ```sh
  pip install spotipy
  pip install requests
  pip install cryptography
  pip install pywifi
  pip install ytmusicapi
  pip install google-auth-oauthlib
  pip install google-api-python-client
  pip install python-dotenv
  pip install rich
  pip install certifi
  pip install readchar
- In case of any issues, check the installations using
  - `pip list | grep -E "spotipy|requests|cryptography|pywifi|ytmusicapi|google-auth-oauthlib|google-api-python-client|python-dotenv|rich|certifi|readchar"`

## **Steps to Run**

- Create an app on the Spotify Developer Dashboard. Add your SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_REDIRECT_URI to the file named credentials.env in the project directory.
- Set up a project in Google Cloud Console and enable the YouTube Data API v3. Download your OAuth client secrets file and set its path as CLIENT_SECRETS_FILE in credentials.env. Add your YOUTUBE_API_KEY to credentials.env.
- All main functions are accessible via the CLI menu: `python menu.py`
