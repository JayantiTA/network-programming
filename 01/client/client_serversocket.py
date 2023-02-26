import socket

HOST, PORT = "localhost", 9999
print("Masukkan command 'download' dan nama file:\n")

while True:
    command = input()
    list_command = command.split(' ')

    if (list_command[0] != 'download'):
        print("command salah!")
        continue

    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(list_command[1].encode())

        data = sock.recv(1024)

        # parsing pesan untuk mendapatkan isi file dan header
        header_end = data.find(b"\n\n")
        header = data[:header_end]
        file_data = data[header_end+2:]

        # parsing header untuk mendapatkan nama file dan ukuran file
        header_lines = header.decode().split("\n")
        file_name = header_lines[0].split(": ")[1]
        file_size = int(header_lines[1].split(": ")[1])

        # tulis isi file ke dalam file baru
        with open(file_name, "wb") as f:
            f.write(file_data)

        # tutup koneksi
        sock.close()

    print("Received: {}".format(file_name))
    continue
