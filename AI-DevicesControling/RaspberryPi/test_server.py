import socket

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            print(f"Received message: {message}")
            # Here, you can add your logic to handle the received message.

        except Exception as e:
            print(f"Error: {e}")
            break

    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8000))
    server_socket.listen(5)
    print("Server is waiting for a connection...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connected to {addr}")
        handle_client(client_socket)

if __name__ == "__main__":
    start_server()
