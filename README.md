# MusiConvert
**Cross-Platform Playlist Conversion & Secure Wi-Fi Direct Sharing Tool**
MusiConvert is a Python-based cross-platform tool for secure playlist sharing and conversion between Spotify and YouTube Music, with a focus on Wi-Fi Direct transfer, encryption, and reliable data transfer. Designed for music lovers and network enthusiasts, MusiConvert enables you to fetch playlists, convert them across platforms, and share them securely—without internet access.

## Features
- **Fetch & Convert Playlists:** Import playlists from Spotify or YouTube Music, extract song metadata, and automatically retrieve cross-platform links.
- **Export/Import:** Save playlists as JSON, and export them back to Spotify or YouTube Music, recreating playlists in your account.
- **Secure Wi-Fi Direct Sharing:** Share playlists over Wi-Fi Direct using encrypted, reliable data transfer (Selective Repeat ARQ with packet loss handling).
- **End-to-End Encryption:** Uses AES-based symmetric encryption via cryptography.fernet for all transferred data.
- **Automated Playlist Creation:** Create and populate playlists on YouTube Music or Spotify using their respective APIs.
- **CLI Menu:** Easy-to-use command-line interface with clear options for import, export, and sharing.
- **Rich Terminal UI:** Enhanced CLI experience using the rich library for colorful tables, prompts, and progress bars.

## Tools Used
- **Python**
  - **Spotipy** (Spotify API)
  - **ytmusicapi** (YouTube Music API)
  - **Cryptography** (Fernet) (AES-based encryption)
  - **PyWiFi** (Wi-Fi Direct setup)
- **Socket Programming** (Reliable data transfer & networks)

## System Requirements
- **Python:** 3.8 or higher
- **Operating Systems:** Windows, macOS, Linux
- **Network:** Wi-Fi Direct-compatible network adapter (for sharing)
- **APIs:** Spotify Developer credentials, Google Cloud YouTube API credentials
