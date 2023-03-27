import sys
import socket
import logging
import ssl
import os
from bs4 import BeautifulSoup

import gzip

BUFFER_SIZE = 1024 * 10
SERVER_HOST = "localhost"


def create_socket(destination_address=SERVER_HOST, port=12000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")


def create_secure_socket(destination_address=SERVER_HOST, port=10000):
    try:
        # get it from https://curl.se/docs/caextract.html
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        secure_socket = ssl.wrap_socket(sock, keyfile=None, certfile=None, server_side=False,
                                        cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)
        logging.warning(secure_socket.getpeercert())
        return secure_socket
    except Exception as ee:
        logging.warning(f"error {str(ee)}")


def send_command(server, command_str, is_secure=False):
    request_path = command_str.split("\r\n")[0].split("GET")[
        1].split("HTTP")[0].strip()
    print("request_path", request_path)

    headers = ""
    content_encoded = b""
    content = ""
    content_encoding = "utf-8"
    content_length = -1
    content_type = "text/html"

    bytes_received = 0

    server_address = server[0]
    server_port = server[1]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if is_secure == True:
        sock = create_secure_socket(server_address, server_port)
    else:
        sock = create_socket(server_address, server_port)

    try:
        logging.warning(f"[+] Sending data ")
        sock.sendall(command_str.encode())
        while True:
            # socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(BUFFER_SIZE)
            if data:
                if "html" not in content_type:
                    bytes_received += len(data)
                    print(
                        f"[!] Bytes Received {bytes_received}/{content_length}")

                    save_file_name = request_path.split("/")[-1]
                    file = open(save_file_name, "ab")
                    file.write(data)
                    file.close()

                    if bytes_received == content_length:
                        content = f""
                        break
                    continue

                decoded_data = data.decode().split("\r\n\r\n")
                headers += decoded_data[0] + "\r\n\r\n"
                content += decoded_data[1]

                # read content-encoding and content-length
                for head in headers.split("\r\n"):
                    if "Content-Encoding:" in head:
                        content_encoding = head.split(
                            "Content-Encoding: ")[1]
                    if "Content-Length:" in head:
                        content_length = int(
                            head.split("Content-Length: ")[1])
                    if "Content-Type:" in head:
                        content_type = head.split(
                            "Content-Type: ")[1].strip()

                logging.warning(f"Content-Encoding: {content_encoding}")
                logging.warning(f"Content-Length: {content_length}")
                logging.warning(f"Content-Type: {content_type}")

                if "html" not in content_type:
                    try:
                        save_file_name = request_path.split("/")[-1]
                        os.remove(save_file_name)
                    except:
                        None

                if len(content) == content_length:
                    if content_encoding == "gzip":
                        content = gzip.decompress(content_encoded).decode()
                    elif content_encoding == "utf-8":
                        None
                    else:
                        content = "[Downloadable Content!]"
                    break
            else:
                print("[!] No More Data Received")
                break

        logging.warning("[+] All data has been received")
        return headers, content
    except Exception as ee:
        logging.warning(f"[!] Error during data receiving {str(ee)}")
        return False


def create_request_headers(req_str):
    data = ""
    for head in req_str.split("\n"):
        if head != "":
            data += f"{head}\r\n"

    data += "\r\n"
    return data

#
# START
#


try:
    while True:
        print(f"[!] Where to?: http://{SERVER_HOST}/", end="")
        dest = input()
        request_headers = f"""
GET /{dest} HTTP/1.1
Host: {SERVER_HOST}
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36
"""
        headers, content = send_command(
            (SERVER_HOST, 8000), create_request_headers(request_headers), False)
        print("[!] HEADERS:")
        print(headers)
        soup = BeautifulSoup(content, "html.parser")
        html_text = soup.get_text()
        print(html_text)

except KeyboardInterrupt:
    sys.exit(0)
