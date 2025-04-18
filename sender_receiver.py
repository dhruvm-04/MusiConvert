import os
import datetime
import socket
import time
import threading
import struct
import sys
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

# Load credentials if needed
load_dotenv("credentials.env")

console = Console()
PEER_FILE = "peers.txt"

def load_peers():
    if not os.path.exists(PEER_FILE):
        return []
    with open(PEER_FILE, "r") as f:
        return [line.strip().split(",") for line in f.readlines() if line.strip()]

def save_peer(name, ip):
    peers = load_peers()
    if not any(p[1] == ip for p in peers):
        with open(PEER_FILE, "a") as f:
            f.write(f"{name},{ip}\n")

def choose_receiver():
    peers = load_peers()
    if peers:
        table = Table(title="Known Receivers", header_style="bold magenta")
        table.add_column("Index", justify="right")
        table.add_column("Name", style="cyan")
        table.add_column("IP Address", style="green")
        for i, (name, ip) in enumerate(peers, 1):
            table.add_row(str(i), name, ip)
        table.add_row("0", "[yellow]New Receiver[/yellow]", "-")
        console.print(table)
        choice = Prompt.ask("Select a receiver (number)")
        if choice.isdigit() and 1 <= int(choice) <= len(peers):
            return peers[int(choice) - 1]
    name = Prompt.ask("Enter receiver's name")
    ip = Prompt.ask("Enter receiver's IP")
    save_peer(name, ip)
    return (name, ip)

def load_or_generate_key():
    key_file_path = "encryption_key.key"
    if not os.path.exists(key_file_path):
        key = Fernet.generate_key()
        with open(key_file_path, "wb") as key_file:
            key_file.write(key)
    else:
        with open(key_file_path, "rb") as key_file:
            key = key_file.read()
    return Fernet(key)

fernet = load_or_generate_key()

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
        choice = Prompt.ask("Enter the number of the playlist to send")
        if choice.isdigit() and 1 <= int(choice) <= len(file_info):
            selected_file = os.path.join(directory, file_info[int(choice) - 1][0])
            return selected_file
        else:
            console.print("[red]Invalid choice. Try again.[/red]")

console.clear()
console.print(Panel("[bold cyan]Secure Selective Repeat File Transfer (Raw Sockets)[/bold cyan]", border_style="blue"))

CHUNK_SIZE = 1024
WINDOW_SIZE = 4
TIMEOUT = 2

IS_SENDER = Prompt.ask("[bold magenta]Are you the sender? (y/n)[/bold magenta]").lower() == 'y'

def sender():
    receiver_name, receiver_ip = choose_receiver()
    file_path = select_json_file("playlists")
    if not file_path:
        console.print(Panel("[bold red]No playlist file selected. Exiting.[/bold red]", border_style="red"))
        sys.exit(1)
    if not os.path.exists(file_path):
        console.print(Panel("[bold red]File not found. Exiting.[/bold red]", border_style="red"))
        sys.exit(1)
    with open(file_path, "rb") as f:
        file_data = f.read()
    total_packets = (len(file_data) + CHUNK_SIZE - 1) // CHUNK_SIZE
    base = 0
    lock = threading.Lock()
    acknowledged = set()
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    ack_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    def listen_for_acks():
        nonlocal base
        while True:
            try:
                packet, _ = ack_socket.recvfrom(65535)
                if packet[20:24] == b'ACK!':
                    seq_num = struct.unpack("!I", packet[24:28])[0]
                    with lock:
                        if seq_num not in acknowledged:
                            console.print(f"[green]ACK RECEIVED:[/green] Packet {seq_num}")
                            acknowledged.add(seq_num)
                        while base in acknowledged:
                            base += 1
                        if base >= total_packets:
                            break
                elif packet[20:24] == b'EACK':
                    console.print(Panel("[bold green]Receiver confirmed completion.[/bold green]", border_style="green"))
                    break
            except:
                break

    ack_thread = threading.Thread(target=listen_for_acks, daemon=True)
    ack_thread.start()
    timers = {}

    while base < total_packets:
        with lock:
            for seq in range(base, min(base + WINDOW_SIZE, total_packets)):
                if seq not in acknowledged and (seq not in timers or time.time() - timers[seq] >= TIMEOUT):
                    chunk = file_data[seq * CHUNK_SIZE:(seq + 1) * CHUNK_SIZE]
                    encrypted_chunk = fernet.encrypt(chunk)
                    header = struct.pack("!4sI", b'DATA', seq)
                    packet = header + encrypted_chunk
                    raw_socket.sendto(packet, (receiver_ip, 0))
                    timers[seq] = time.time()
                    console.print(f"[cyan]SENT:[/cyan] Packet {seq}")
        time.sleep(0.1)
    end_packet = struct.pack("!4sI", b'END!', 999999999)
    raw_socket.sendto(end_packet, (receiver_ip, 0))
    console.print(Panel("[yellow]Waiting for receiver to confirm completion...[/yellow]", border_style="yellow"))
    start_time = time.time()
    while time.time() - start_time < 5:
        try:
            packet, _ = ack_socket.recvfrom(65535)
            if packet[20:24] == b'EACK':
                console.print(Panel("[bold green]Receiver confirmed completion.[/bold green]", border_style="green"))
                break
        except:
            continue
    else:
        console.print(Panel("[bold red]No confirmation from receiver. Assuming timeout.[/bold red]", border_style="red"))
    raw_socket.close()
    ack_socket.close()
    ack_thread.join()

def receiver():
    sender_ip = Prompt.ask("[bold magenta]Enter sender IP[/bold magenta]").strip()
    output_file = Prompt.ask("[bold magenta]Enter output file name[/bold magenta]").strip()
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    raw_socket.bind(("", 0))
    received = {}
    console.print(Panel(f"[yellow]Waiting for data from {sender_ip}...[/yellow]", border_style="yellow"))
    while True:
        packet, addr = raw_socket.recvfrom(65535)
        if addr[0] != sender_ip:
            continue
        if packet[20:24] == b'DATA':
            seq_num = struct.unpack("!I", packet[24:28])[0]
            encrypted_data = packet[28:]
            try:
                data = fernet.decrypt(encrypted_data)
                if seq_num not in received:
                    received[seq_num] = data
                ack_packet = b'ACK!' + struct.pack("!I", seq_num)
                raw_socket.sendto(ack_packet, (sender_ip, 0))
                console.print(f"[blue]RECEIVED:[/blue] Packet {seq_num}")
            except Exception as e:
                console.print(Panel(f"[red]Decryption error for packet {seq_num}: {e}[/red]", border_style="red"))
        elif packet[20:24] == b'END!':
            ack_packet = b'EACK' + struct.pack("!I", 999999999)
            raw_socket.sendto(ack_packet, (sender_ip, 0))
            break
    with open(output_file, "wb") as f:
        for i in sorted(received):
            f.write(received[i])
    raw_socket.close()
    console.print(Panel("[bold green]\nFile received and saved successfully.[/bold green]", border_style="green"))

if IS_SENDER:
    sender()
else:
    receiver()
