import socket
import sys
from time import sleep
import os
from os import path
import tqdm

def get_string_between(str, sep1, sep2):
    result = ""
    try:
        result = str.split(sep1)[1].split(sep2)[0]
    except:
        None
    return result


BUFFER_SIZE = 1024
HOST = sys.argv[1]
PORT = int(sys.argv[2])

server_address = (HOST, PORT)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"[+] Connecting to {HOST}:{PORT}")
client_socket.connect(server_address)
print("[+] Connected.")
print("[SEND] >> ")

try:
    while True:
        message = sys.stdin.readline()
        client_socket.send(bytes(message, 'utf-8'))
        received_data = client_socket.recv(BUFFER_SIZE).decode('utf-8')

        # Special handling if we send unduh message
        if message.split(" ")[0] == "download":
            # check the confirmation is the file exist
            if received_data == "CONFIRMATION::FILE_EXIST\n":
                # read the header message
                received_header = client_socket.recv(BUFFER_SIZE)
                print(f"received_header : [{received_header}]")
                received_header = received_header.decode('utf-8')
                recv_filename = get_string_between(received_header, "file-name: ", "\n")
                recv_filesize = int(get_string_between(received_header, "file-size: ", "\n"))
                
                print(f"We got header ::\nFile Name : {recv_filename}\nFile Size: {recv_filesize}")
                # delete the file first,
                try:
                    os.remove(recv_filename)
                except:
                    None

                #read the file content
                #setup the progress bar
                total_data_recv = 0
                with open(recv_filename, "wb") as f:
                    while True:
                        # read %BUFFER_SIZE% bytes from the socket (receive)
                        bytes_read = client_socket.recv(BUFFER_SIZE)
                        # print(bytes_read)

                        if not bytes_read:    
                            # nothing is received
                            # file transmitting is done
                            break
                        # write to the file the bytes we just received
                        f.write(bytes_read)
                        total_data_recv += len(bytes_read)
                        #update the progress status
                        print(f"[!] File transfer {recv_filename} : {total_data_recv}B/{recv_filesize}B ({(total_data_recv/recv_filesize)*100}%)                 \r", end="")

                        # check is the file transfer completed
                        if path.getsize(recv_filename) == recv_filesize:
                            sys.stdout.write("\n[!] File transfer done ~\n[SEND] >> ")
                            break
            else:
                sys.stdout.write(f"[RECV] << {received_data}[SEND] >> ")
        #special handling for exit
        elif f"{message.rstrip()} ".split(" ")[0] == "exit":
            client_socket.send(bytes("REQUEST::DISCONNECT", 'utf-8'))
            client_socket.close()
            sys.stdout.write(f"[!] Bye")
            break
        else:
            sys.stdout.write(f"[RECV] << {received_data}[SEND] >> ")

except KeyboardInterrupt:
    client_socket.close()
    sys.exit(0)