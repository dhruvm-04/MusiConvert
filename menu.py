from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
import subprocess

console = Console()

def menu():
    while True:
        console.clear()
        console.print(Panel("[bold magenta]MusiConvert CLI[/bold magenta]", expand=False, border_style="cyan"))

        menu_table = Table(show_header=False, box=None, pad_edge=False)
        menu_table.add_column(justify="right")
        menu_table.add_column()
        menu_table.add_row("[cyan]1.[/cyan]", "[white]Import Playlist (YouTube/Spotify → JSON)[/white]")
        menu_table.add_row("[cyan]2.[/cyan]", "[white]Send/Receive Playlist[/white]")
        menu_table.add_row("[cyan]3.[/cyan]", "[white]Export Playlist (JSON → YouTube/Spotify)[/white]")
        menu_table.add_row("[cyan]4.[/cyan]", "[white]Exit[/white]")
        console.print(menu_table)

        choice = Prompt.ask("\n[bold green]Select an option[/bold green]")
        if choice == "1":
            subprocess.run(["python", "get_playlist.py"])
        elif choice == "2":
            subprocess.run(["python", "sender_receiver.py"])
        elif choice == "3":
            subprocess.run(["python", "create.py"])
        elif choice == "4":
            console.print(Panel("[bold green]Exiting...[/bold green]\n[bold green]Thank you for using MusiConvert![/bold green]", border_style="green"))
            break
        else:
            console.print(Panel("[red]Invalid choice. Try again.[/red]", border_style="red"))
            input("Press Enter to return to main menu")

if __name__ == "__main__":
    menu()
