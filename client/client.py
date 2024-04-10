import socket
import threading
from config import SERVER_IP, SERVER_PORT, BUFFER_SIZE


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode('utf-8')
            print(message)
        except:
            print("You have been disconnected from the server.")
            client_socket.close()
            break


def send_messages(client_socket):
    while True:
        message = input('')
        if message == "/quit":
            client_socket.send(message.encode('utf-8'))
            client_socket.close()
            break
        client_socket.send(message.encode('utf-8'))


def main():
    nickname = input("Choose your nickname: ")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    client_socket.send(nickname.encode('utf-8'))

    thread_recv = threading.Thread(target=receive_messages, args=(client_socket,))
    thread_recv.start()

    thread_send = threading.Thread(target=send_messages, args=(client_socket,))
    thread_send.start()


if __name__ == "__main__":
    main()
