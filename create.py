from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align
from rich.table import Table
from rich.progress import Progress
from rich.text import Text
import os
import readchar
import json
import datetime
from dotenv import load_dotenv
import google_auth_oauthlib.flow
import googleapiclient.discovery
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load credentials from .env
load_dotenv("credentials.env")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE")

console = Console()

SCOPES_YT = ["https://www.googleapis.com/auth/youtube.force-ssl"]
SCOPES_SPOTIFY = ["playlist-modify-public", "playlist-modify-private"]

def authenticate_youtube():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES_YT
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    auth_text = Text("If not automatically opened, please authorize using ", style="bold white")
    auth_text.append("this link", style="bold blue link " + auth_url)
    console.print(Panel(auth_text, border_style="cyan"))
    credentials = flow.run_local_server(port=0)
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def authenticate_spotify():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=" ".join(SCOPES_SPOTIFY)
    ))

def create_youtube_playlist(youtube, playlist_name, creation_datetime):
    description = f"Created using MusiConvert at {creation_datetime.strftime('%H:%M %d/%m/%Y')}"
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": playlist_name,
                "description": description,
                "tags": ["music"],
                "defaultLanguage": "en"
            },
            "status": {"privacyStatus": "public"},
        }
    )
    response = request.execute()
    return response["id"]

def add_video_to_youtube_playlist(youtube, playlist_id, video_id):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            },
        }
    )
    request.execute()

def create_spotify_playlist(spotify, playlist_name, creation_datetime):
    description = f"Created using MusiConvert at {creation_datetime.strftime('%H:%M %d/%m/%Y')}"
    user_id = spotify.me()["id"]
    playlist = spotify.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=True,
        description=description
    )
    return playlist["id"]

def add_track_to_spotify_playlist(spotify, playlist_id, track_uri):
    spotify.playlist_add_items(playlist_id, [track_uri])

def select_json_file(directory="playlists"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    files = [f for f in os.listdir(directory) if f.endswith('.json')]
    if not files:
        console.print("[red]No playlist JSON files found in the directory.[/red]")
        return None

    file_info = []
    for f in files:
        path = os.path.join(directory, f)
        ctime = os.path.getctime(path)
        dt = datetime.datetime.fromtimestamp(ctime)
        file_info.append((f, dt.strftime("%H:%M:%S"), dt.strftime("%Y-%m-%d")))

    table = Table(title="Available Playlists", show_lines=True)
    table.add_column("No.", justify="right")
    table.add_column("Name", style="cyan")
    table.add_column("Time of Creation", style="green")
    table.add_column("Date of Creation", style="magenta")
    for idx, (fname, time_str, date_str) in enumerate(file_info, 1):
        table.add_row(str(idx), fname, time_str, date_str)
    console.print(table)

    while True:
        choice = Prompt.ask("Enter the number of the playlist to select")
        if choice.isdigit() and 1 <= int(choice) <= len(file_info):
            selected_file = os.path.join(directory, file_info[int(choice) - 1][0])
            return selected_file
        else:
            console.print("[red]Invalid choice. Try again.[/red]")

def export_playlist():
    console.clear()
    console.print(Panel("[bold magenta]MusiConvert: Export Playlist[/bold magenta]", border_style="cyan"))
    selected_json = select_json_file("playlists")
    if not selected_json:
        return

    with open(selected_json, "r", encoding="utf-8") as file:
        playlist_data = json.load(file)

    platform_table = Table.grid(padding=(0, 4))
    platform_table.add_column(justify="center")
    platform_table.add_column(justify="center")
    platform_table.add_row(
        "[bold cyan]Y[/bold cyan] - [white]YouTube Music[/white]",
        "[bold cyan]S[/bold cyan] - [white]Spotify[/white]"
    )
    platform_panel = Panel(
        Align.center(Group(
            Align.center("[bold white]Choose Export Platform[/bold white]"),
            Align.center(platform_table)
        )),
        title="[cyan]Export Playlist[/cyan]",
        border_style="white",
        padding=(1, 2)
    )
    console.print(platform_panel, justify="left")
    console.print("\n[bold magenta]Press Y or S to export, or Q to cancel[/bold magenta]")

    creation_datetime = datetime.datetime.now()

    while True:
        key = readchar.readkey().lower()
        if key == 'y':
            youtube = authenticate_youtube()
            playlist_id = create_youtube_playlist(youtube, playlist_data["name"], creation_datetime)
            with Progress() as progress:
                task = progress.add_task("[cyan]Adding songs...", total=len(playlist_data["tracks"]))
                for track in playlist_data["tracks"]:
                    if "youtube_music_id" in track and track["youtube_music_id"]:
                        video_id = track["youtube_music_id"].split("?")[-1].split("=")[-1]
                        add_video_to_youtube_playlist(youtube, playlist_id, video_id)
                    progress.advance(task)
            console.print(Panel(f"\n[bold green]Playlist '{playlist_data['name']}' created on YouTube Music![/bold green]", border_style="green"))
            break
        elif key == 's':
            spotify = authenticate_spotify()
            playlist_id = create_spotify_playlist(spotify, playlist_data["name"], creation_datetime)
            with Progress() as progress:
                task = progress.add_task("[green]Adding tracks...", total=len(playlist_data["tracks"]))
                for track in playlist_data["tracks"]:
                    if "spotify_id" in track and track["spotify_id"]:
                        add_track_to_spotify_playlist(spotify, playlist_id, track["spotify_id"])
                    progress.advance(task)
            console.print(Panel(f"\n[bold green]Playlist '{playlist_data['name']}' created on Spotify![/bold green]", border_style="green"))
            break
        elif key == 'q':
            console.print(Panel("[bold yellow]Cancelled export.[/bold yellow]", border_style="yellow"))
            break
        else:
            console.print(Panel("[bold red]Invalid key. Press Y, S, or Q[/bold red]", border_style="red"))

if __name__ == "__main__":
    export_playlist()
