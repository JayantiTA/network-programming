import socket

BUFFER_SIZE = 1024

def receive_file(client_sock, file_name, file_size):
    total_data_recv = 0
    with open(file_name, "wb") as file:
        while True:
            data_recv = client_sock.recv(BUFFER_SIZE)
            file.write(data_recv)
            total_data_recv += len(data_recv)
            if file_size == total_data_recv:
                print(f"{file_name} has been received successful!")
                break

def parse_header_to_dict(msg_header):
    headers = {}
    for line in msg_header.split("\n"):
        if not line:
            break
        key, value = line.strip().split(": ")
        headers[key] = value
    return headers

def run_client():
    host = "172.17.0.3" # host server (using docker)
    port = 2410 # custom port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        client_sock.connect((host, port))

        # input the download command
        while True:
            command = input("Command (download file_name): ")
            if not command:
                return

            client_sock.send(command.encode())
            data_recv = client_sock.recv(BUFFER_SIZE)
            response = data_recv.decode()
            if response.startswith("ERROR"):
                print(response)
                return

            msg_header, data_recv = response.split("\n\n", 1)
            headers = parse_header_to_dict(msg_header)
            file_name = headers["file-name"]
            file_size = int(headers["file-size"])
            print(f"Receiving {file_name} ({file_size} bytes)...")
            receive_file(client_sock, file_name, file_size)

if __name__ == "__main__":
    run_client()
