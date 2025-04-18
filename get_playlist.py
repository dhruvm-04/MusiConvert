import os
import json
import certifi
import requests
import spotipy
from dotenv import load_dotenv
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress
from rich.panel import Panel
from rich.table import Table
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build

# Load credentials from .env
load_dotenv("credentials.env")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

console = Console()

SCOPE = "playlist-read-private"

try:
    os.environ['PYTHONHTTPSVERIFY'] = '1'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ))
    console.print(Panel("[bold green]Spotify authentication successful[/bold green]", border_style="green"))
except Exception as e:
    console.print(Panel(f"[bold red]Spotify authentication failed:[/bold red] {e}", border_style="red"))
    exit()

def search_youtube(song_name, artist):
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        query = f"{song_name} {artist} audio"
        search_response = youtube.search().list(
            q=query, part="snippet", maxResults=1, type="video"
        ).execute()
        if search_response.get("items"):
            video_id = search_response["items"][0]["id"].get("videoId")
            return f"https://music.youtube.com/watch?v={video_id}" if video_id else None
        return None
    except Exception as e:
        console.print(Panel(f"[red]YouTube search error:[/red] {e}", border_style="red"))
        return None

def get_matching_song(youtube_url):
    try:
        api_url = "https://api.song.link/v1-alpha.1/links"
        params = {"url": youtube_url, "userCountry": "US"}
        response = requests.get(api_url, params=params, verify=certifi.where())
        if response.status_code == 200:
            data = response.json()
            return {"spotify_id": data.get("linksByPlatform", {}).get("spotify", {}).get("url")}
        console.print(Panel(f"[yellow]Odesli API error:[/yellow] Status code {response.status_code}", border_style="yellow"))
        return {"spotify_id": None}
    except Exception as e:
        console.print(Panel(f"[red]Error fetching cross-platform links:[/red] {e}", border_style="red"))
        return {"spotify_id": None}

def get_spotify_playlist(playlist_id):
    try:
        playlist = sp.playlist(playlist_id)
        playlist_name = playlist.get("name", "Unnamed Playlist")
        tracks = []
        results = sp.playlist_items(playlist_id, limit=50)
        while results:
            if "items" not in results:
                break
            tracks.extend(results["items"])
            results = sp.next(results) if results.get("next") else None

        playlist_data = {"name": playlist_name, "tracks": []}
        with Progress() as progress:
            task = progress.add_task("[green]Processing tracks...", total=len(tracks))
            for item in tracks:
                track = item.get("track")
                if not track:
                    progress.advance(task)
                    continue
                track_id = track.get("id")
                spotify_url = f"https://open.spotify.com/track/{track_id}" if track_id else None
                matched_links = get_matching_song(spotify_url) if spotify_url else {"youtube_music_id": None}
                youtube_music_id = matched_links.get("youtube_music_id") or search_youtube(
                    track.get("name", ""), track.get("artists", [{}])[0].get("name", "")
                )
                playlist_data["tracks"].append({
                    "name": track.get("name", "Unknown"),
                    "artist": track.get("artists", [{}])[0].get("name", "Unknown"),
                    "album": track.get("album", {}).get("name", "Unknown"),
                    "spotify_id": spotify_url,
                    "youtube_music_id": youtube_music_id
                })
                progress.advance(task)
        return playlist_data
    except Exception as e:
        console.print(Panel(f"[red]Error fetching Spotify playlist data:[/red] {e}", border_style="red"))
        return None

def get_youtube_playlist(playlist_id):
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        playlist_data = {"name": "YouTube Playlist", "tracks": []}
        next_page_token = None
        with Progress() as progress:
            task = progress.add_task("[cyan]Fetching YouTube tracks...", total=50)
            while True:
                response = youtube.playlistItems().list(
                    part="snippet", playlistId=playlist_id, maxResults=50, pageToken=next_page_token
                ).execute()
                for item in response.get("items", []):
                    snippet = item["snippet"]
                    title = snippet["title"]
                    artist = snippet.get("videoOwnerChannelTitle", "Unknown")
                    youtube_url = f"https://music.youtube.com/watch?v={snippet['resourceId']['videoId']}"
                    matched_links = get_matching_song(youtube_url)
                    playlist_data["tracks"].append({
                        "name": title,
                        "artist": artist,
                        "album": "Unknown",
                        "spotify_id": matched_links.get("spotify_id"),
                        "youtube_music_id": youtube_url
                    })
                    progress.advance(task)
                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break
        return playlist_data
    except Exception as e:
        console.print(Panel(f"[red]Error fetching YouTube playlist data:[/red] {e}", border_style="red"))
        return None

console.print(Panel("[bold magenta]MusiConvert - Import Playlist[/bold magenta]", border_style="cyan"))
playlist_url = Prompt.ask("[bold green]Enter Playlist URL or ID[/bold green]").strip()

if "spotify" in playlist_url:
    playlist_id = playlist_url.split("playlist/")[-1].split("?")[0]
    playlist_info = get_spotify_playlist(playlist_id)
elif "youtube" in playlist_url or "list=" in playlist_url:
    playlist_id = playlist_url.split("list=")[-1].split("&")[0]
    playlist_info = get_youtube_playlist(playlist_id)
else:
    console.print(Panel("[red]Invalid playlist URL. Must be from Spotify or YouTube Music.[/red]", border_style="red"))
    exit()

if playlist_info:
    table = Table(title=f"Playlist: {playlist_info['name']}", header_style="bold magenta")
    table.add_column("Track", style="cyan", no_wrap=True)
    table.add_column("Artist", style="green")
    table.add_column("Album", style="yellow")
    for track in playlist_info["tracks"][:10]:
        table.add_row(track["name"], track["artist"], track["album"])
    if len(playlist_info["tracks"]) > 10:
        table.add_row(f"...and {len(playlist_info['tracks']) - 10} more", "", "")
    console.print(table)
    console.print(Panel("[green]Playlist fetched successfully![/green]", border_style="green"))

    save_dir = "playlists"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_name = Prompt.ask("[bold magenta]Enter a name for the playlist file (without .json)[/bold magenta]").strip()
    save_path = os.path.join(save_dir, save_name + ".json")
    try:
        with open(save_path, "w", encoding="utf-8") as file:
            json.dump(playlist_info, file, indent=4)
        console.print(Panel(f"[bold green]Playlist data saved at:[/bold green] {save_path}", border_style="green"))
    except Exception as e:
        console.print(Panel(f"[red]Error saving playlist file:[/red] {e}", border_style="red"))
else:
    console.print(Panel("[red]Failed to fetch playlist data.[/red]", border_style="red"))
