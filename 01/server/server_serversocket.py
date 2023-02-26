import socketserver
import os

# https://docs.python.org/3/library/socketserver.html

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).decode()
        if not self.data:
            return
        
        file_name = self.data
        if os.path.isfile("files/" + file_name):
            # buka file yang diminta dan baca isinya
            with open("files/" + file_name, "rb") as f:
                file_data = f.read()

            # tambahkan header pada pesan
            header = f"file-name: {file_name}\nfile-size: {len(file_data)}\n\n"
            message = header.encode() + file_data
            # kirim pesan yang telah ditambahkan header ke klien
            self.request.sendall(message)
            print(f"File {file_name} berhasil dikirim ke {self.client_address[0]}:{self.client_address[1]}")
        else:
            self.request.sendall("File tidak ditemukan".encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
