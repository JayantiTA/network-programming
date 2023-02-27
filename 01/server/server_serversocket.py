import os
import sys
import socketserver

BUFFER_SIZE = 1024
FILE_DIRECTORY = "files/" # path to folder files

class FileTransferHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # handle reuse address
        socketserver.TCPServer.allow_reuse_address = True

        while True:
            print(f"Connected to {self.client_address}")

            recv_data = self.request.recv(BUFFER_SIZE)
            if not recv_data:
                return

            request = recv_data.decode().strip()
            if not request.startswith("download"):
                self.request.send("ERROR: Invalid command!\n".encode())

            file_name = request.split()[1]
            file_path = os.path.join(FILE_DIRECTORY, file_name)
            if not os.path.exists(file_path):
                self.request.send(f"ERROR: File {file_name} is not found\n".encode())

            file_size = os.path.getsize(file_path)
            msg_header = f"file-name: {file_name}\nfile-size: {file_size}\n\n\n"
            with open(file_path, "rb") as file:
                self.request.send(msg_header.encode())
                total_data_sent = 0
                while True:
                    data_sent = file.read(BUFFER_SIZE)
                    self.request.sendall(data_sent)
                    total_data_sent += len(data_sent)
                    if file_size == total_data_sent:
                        print(f"{file_name} has been received successful!")
                        break
            print(f"{file_name} has success sent to {self.client_address}")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def run_server():
    host = "" # all host can acceess the server
    port = 2410 # custom port
    with ThreadedTCPServer((host, port), FileTransferHandler) as server:
        print(f"Server is running on {host}:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()
            sys.exit(0)

if __name__ == "__main__":
    run_server()
