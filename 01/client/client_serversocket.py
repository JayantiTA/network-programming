import socket

BUFFER_SIZE = 1024

def receive_file(client_sock, file_name):
    with open(file_name, "wb") as file:
        while True:
            recv_data = client_sock.recv(BUFFER_SIZE)
            if not recv_data:
                print(f"{file_name} has been received successful!")
                break
            file.write(recv_data)

def parse_header_to_dict(msg_header):
    headers = {}
    for line in msg_header.split("\n"):
        if not line:
            break
        key, value = line.strip().split(": ")
        headers[key] = value
    return headers

def run_client():
    host = "172.17.0.4" # host server (using docker)
    port = 2410 # custom port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        client_sock.connect((host, port))

        # input the download command
        command = input("Command (download file_name): ")
        if not command:
            return

        client_sock.send(command.encode())
        recv_data = client_sock.recv(BUFFER_SIZE)
        response = recv_data.decode()
        if response.startswith("ERROR"):
            print(response)
            return

        msg_header, recv_data = response.split("\n\n", 1)
        headers = parse_header_to_dict(msg_header)
        file_name = headers["file-name"]
        file_size = int(headers["file-size"])
        print(f"Receiving {file_name} ({file_size} bytes)...")
        receive_file(client_sock, file_name)

if __name__ == "__main__":
    run_client()
