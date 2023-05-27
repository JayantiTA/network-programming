import socket
import sys
import os
from os.path import exists
from pathlib import Path
from datetime import datetime
import time
import platform
import threading
import select
from _thread import *

BUFFER_SIZE = 1024

# read httpserver.conf
CONFIG = {}
ALIAS = {}

# mime type that used in dataset and parent dir
MIME = {
    "html": "text/html",
    "pdf": "application/pdf",
    "txt": "text/plain",
    "zip": "application/zip"
}


def creation_date(path_to_file):
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            return stat.st_mtime


def return_html(client, header, html_text=""):
    # create response
    now = datetime.now()
    date_string = now.strftime("%d/%m/%Y %H:%M:%S")

    header += f"\r\n{date_string}"
    header += f"\r\nContent-Type: text/html; charset=utf-8"

    if len(html_text) > 0:
        header += f"\r\nContent-Length: {len(html_text)}"

    response = header + "\r\n\r\n" + html_text + "\r\n\r\n"
    client.sendall(response.encode())


def return_bytes(client, path_to_file):
    # get mime type from mime.csv
    file_type = path_to_file.split(".")[-1]
    if file_type in MIME:
        mime_type = MIME[file_type]
    else:
        mime_type = f"application/{file_type}"

    # create response
    now = datetime.now()
    date_string = now.strftime("%d/%m/%Y %H:%M:%S")

    header = "HTTP/1.1 200 OK"
    header += f"\r\n{date_string}"
    header += f"\r\nContent-Type: {mime_type}"
    header += f"\r\naccept-ranges: bytes"

    file_size = os.path.getsize(path_to_file)
    header += f"\r\nContent-Length: {file_size}"
    header += "\r\n\r\n"

    client.send(header.encode())

    with open(path_to_file, "rb") as file:
        total_bytes = 0
        while True:
            # read the bytes from the file
            bytes_read = file.read()
            total_bytes += len(bytes_read)
            if file_size == total_bytes:
                break

        # send to client
        client.sendall(bytes_read)


def load_config():
    global CONFIG, ALIAS
    print("[!] READING HTTPSERVER.CONF")

    file = open("httpserver.conf", "r")
    for line in file:
        line = line.rstrip()
        if "Listen" in line:
            CONFIG["LISTEN_PORT"] = int(line.split(" ")[1])
        if "ServerRoot" in line:
            CONFIG["SERVER_ROOT"] = line.split(" ")[1].replace('"', '')
        if "ServerName" in line:
            CONFIG["SERVER_NAME"] = line.split(" ")[1]
        if "ServerAdmin" in line:
            CONFIG["SERVER_ADMIN"] = line.split(" ")[1]
        if "ErrorDocument" in line:
            CONFIG["404"] = line.split(" ")[2].replace('"', '')
        if "Alias" in line:
            a_from = line.split(" ")[1].replace('"', '')
            a_to = line.split(" ")[2].replace('"', '')
            ALIAS[a_from] = a_to
    file.close()


def threaded_socket(client_socket):
    while True:
        client_request = ""
        ready_to_read, _, _ = select.select([client_socket], [], [])

        for sock in ready_to_read:
            request = sock.recv(BUFFER_SIZE)
            # if not request:
            #     client_sockets.remove(sock)
            #     sock.close()
            if request:
                client_request = request.decode()
                print("[!] CLIENT REQUEST:")
                print(client_request)

                # get request path
                first_head = client_request.split("\r\n")[0].split(" ")
                request_path = first_head[1]

                # check path alias
                if request_path in ALIAS:
                    request_path = ALIAS[request_path]

                absolute_path = CONFIG["SERVER_ROOT"] + request_path
                print("[!] Absolute path:", absolute_path)

                # check is path exist?
                if exists(absolute_path):
                    if Path(absolute_path).is_file():
                        if absolute_path.split(".")[-1] == "html":
                            # return html
                            # read file content
                            file = open(absolute_path, "r")
                            html_text = file.read()
                            file.close()
                            return_html(sock,
                                        "HTTP/1.1 200 OK", html_text)
                        else:
                            # return file bytes
                            return_bytes(sock, absolute_path)
                    else:
                        # return directory listing as HTML file
                        # get file list in path
                        dir_list = os.listdir(absolute_path)
                        directory_dom = ""
                        for file in dir_list:
                            # check file size and last modified
                            last_modified = time.ctime(
                                creation_date(f"{absolute_path}{file}"))

                            if Path(f"{absolute_path}{file}").is_file():
                                file_size = os.path.getsize(
                                    f"{absolute_path}{file}")
                                directory_dom += f"""
                                <tr>
                                    <td valign="top">[TXT]</td>
                                    <td><a href="{file}">{file}</a></td>
                                    <td align="right">{last_modified}</td>
                                    <td align="right">{file_size} B</td><td>&nbsp;</td>
                                </tr>
                                """
                                None
                            else:
                                directory_dom += f"""
                                <tr>
                                    <td valign="top">[DIR]</td>
                                    <td><a href="{file}/">{file}/</a></td>
                                    <td align="right">{last_modified}</td>
                                    <td align="right">  - </td><td>&nbsp;</td>
                                </tr>
                                """

                        file = open("directory.html", "r")
                        html_text = file.read()
                        file.close()

                        html_text = html_text.replace(
                            "==DIRECTORY_NAME==", request_path)
                        html_text = html_text.replace(
                            "==DIRECTORY_LIST==", directory_dom)
                        return_html(sock,
                                    "HTTP/1.1 200 OK", html_text)
                else:
                    # return 404 if file not found
                    file = open(CONFIG["SERVER_ROOT"] + CONFIG["404"], "r")
                    html_text = file.read()
                    file.close()
                    return_html(sock,
                                "HTTP/1.1 404 Not Found", html_text)


#
# START
#


load_config()

# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = CONFIG["LISTEN_PORT"]
ThreadCount = 0

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)
print('[!] Listening on port %s ...' % SERVER_PORT)

client_sockets = []

try:
    while True:
        # Wait for client connections
        client_socket, client_address = server_socket.accept()
        print(f"[+] New client {client_address} is connected.")
        client_sockets.append(client_socket)
        client_thread = threading.Thread(
            target=threaded_socket, args=(client_socket,))
        ThreadCount += 1
        print('[!] Thread Number: ' + str(ThreadCount))
        client_thread.start()

except KeyboardInterrupt:
    server_socket.close()
    sys.exit(0)
