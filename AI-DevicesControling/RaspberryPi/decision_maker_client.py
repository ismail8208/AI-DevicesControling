import socket

def client_receive():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 65432))  # استخدم نفس IP و Port للسيرفر

    try:
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print(f"Received: {data}")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        client_socket.close()

client_receive()
