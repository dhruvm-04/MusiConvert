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

## Extra Files and Folders Created by MusiConvert

When you use MusiConvert, several files and directories are automatically created and managed by the application to support its features. Here’s what will appear in your project directory during normal use:

---

### **1. `playlists/` Directory**
- **Purpose:** Stores all playlist data files you import or generate.
- **Behavior:**  
  - Created automatically if it does not exist when you import or export playlists.
  - Contains `.json` files, each representing a playlist with track details and cross-platform links.
- **Location:**  
  - Relative to your project root (i.e., `./playlists`).

---

### **2. `encryption_key.key`**
- **Purpose:** Stores the symmetric encryption key used for encrypting and decrypting playlist files during transfer.
- **Behavior:**  
  - Automatically created in your project directory the first time you run a file transfer (send/receive).
  - Used by both sender and receiver for secure end-to-end encryption.
- **Location:**  
  - Project root (i.e., `./encryption_key.key`).

---

### **3. `peers.txt`**
- **Purpose:** Maintains a list of known receiver names and their IP addresses for easier Wi-Fi Direct sharing.
- **Behavior:**  
  - Automatically created and updated as you add or select receivers during file transfer.
  - Each line contains a receiver’s name and IP address, separated by a comma.
- **Location:**  
  - Project root (i.e., `./peers.txt`).

---

### **4. `credentials.env`**
- **Purpose:** Stores your API keys and authentication credentials for Spotify and YouTube Music.
- **Behavior:**  
  - You create and edit this file manually to add your credentials.
  - Loaded automatically by the application on startup.
- **Location:**  
  - Project root (i.e., `./credentials.env`).

---

### **5. `client_secrets.json`**
- **Purpose:** Used for YouTube Music/Google API authentication.
- **Behavior:**  
  - You download this file from Google Cloud Console and reference its path in `credentials.env`.
- **Location:**  
  - Anywhere you prefer, but path must be set correctly in `credentials.env`.

---

## **Summary Table**

| File/Folder           | Created By        | Purpose                                          | Location           |
|-----------------------|-------------------|--------------------------------------------------|--------------------|
| `playlists/`          | MusiConvert       | Stores all playlist JSON files                    | Project root       |
| `encryption_key.key`  | MusiConvert       | Encryption key for secure transfers               | Project root       |
| `peers.txt`           | MusiConvert       | Stores known receiver names and IPs               | Project root       |
| `credentials.env`     | User (manual)     | API credentials for Spotify/YouTube               | Project root       |
| `client_secrets.json` | User (manual)     | Google API OAuth credentials                      | User-defined       |
| `.gitignore`, `README.md`, etc. | User/manual | Standard repo/documentation files                | Project root       |
