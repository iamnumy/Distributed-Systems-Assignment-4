import socket
import threading
from config import SERVER_IP, SERVER_PORT, BUFFER_SIZE

clients = {}
channels = {"general": []}
client_channels = {}


def broadcast_message_to_channel(sender_nickname, msg, exclude_sender=True):
    """Broadcasts a message to all clients in the same channel."""
    channel_name = client_channels.get(sender_nickname, "general")
    for nickname in channels[channel_name]:
        if exclude_sender and nickname == sender_nickname:
            continue
        client_conn = clients[nickname]
        try:
            client_conn.send(f"{sender_nickname}: {msg}".encode('utf-8'))
        except:
            remove_client(nickname)


def handle_private_message(sender_nickname, recipient_nickname, msg):
    """Handles sending a private message from one client to another."""
    if recipient_nickname in clients:
        recipient_conn = clients[recipient_nickname]
        try:
            recipient_conn.send(f"Private from {sender_nickname}: {msg}".encode('utf-8'))
        except:
            remove_client(recipient_nickname)
    else:
        sender_conn = clients[sender_nickname]
        sender_conn.send(f"User {recipient_nickname} not found.".encode('utf-8'))


def move_client_to_channel(nickname, channel_name):
    """Moves a client to a new channel, creating the channel if it doesn't exist."""
    if nickname in client_channels:
        old_channel = client_channels[nickname]
        if old_channel in channels and nickname in channels[old_channel]:
            channels[old_channel].remove(nickname)
    if channel_name not in channels:
        channels[channel_name] = []
    channels[channel_name].append(nickname)
    client_channels[nickname] = channel_name
    clients[nickname].send(f"You joined {channel_name}".encode('utf-8'))
    # Updated join message format here
    broadcast_message_to_channel(nickname, f"{nickname} joined {channel_name} channel", exclude_sender=False)

def remove_client(nickname):
    """Removes a client from the server's tracking structures."""
    if nickname in clients:
        del clients[nickname]
    if nickname in client_channels:
        channel = client_channels[nickname]
        if nickname in channels[channel]:
            channels[channel].remove(nickname)
        del client_channels[nickname]
        broadcast_message_to_channel(nickname, f"{nickname} has left the chat.", exclude_sender=False)


def handle_client(conn, addr):
    """Handles incoming client connections and messaging."""
    print(f"[NEW CONNECTION] {addr} connected.")
    nickname = conn.recv(BUFFER_SIZE).decode('utf-8')
    clients[nickname] = conn
    move_client_to_channel(nickname, "general")

    while True:
        try:
            msg = conn.recv(BUFFER_SIZE).decode('utf-8')
            if msg.startswith("/join"):
                _, channel_name = msg.split(' ', 1)
                move_client_to_channel(nickname, channel_name)
            elif msg.startswith("/private"):
                _, recipient_nickname, private_msg = msg.split(' ', 2)
                handle_private_message(nickname, recipient_nickname, private_msg)
            elif msg.startswith("/quit"):
                break
            else:
                broadcast_message_to_channel(nickname, msg)
        except:
            break

    remove_client(nickname)
    conn.close()


def start_server():
    """Starts the server, listening for connections and handling them."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print(f"[LISTENING] Server is listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


if __name__ == "__main__":
    start_server()