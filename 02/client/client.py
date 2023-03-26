import sys
import socket
import json
import logging
import ssl
import os
from bs4 import BeautifulSoup
from lxml import html, etree

import gzip

BUFFER_SIZE = 1024
SERVER_HOST = "localhost"


def create_socket(destination_address='localhost', port=12000):
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
        # https://curl.se/docs/caextract.html
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
    # Get Request Path
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
    headers_complete = False

    server_address = server[0]
    server_port = server[1]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # gunakan fungsi diatas
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
                # Special handling for Downloadable Content
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

                if not headers_complete:
                    headers += data.decode()
                else:
                    bytes_received += 1

                    if content_encoding == "utf-8":
                        content += data.decode()
                    else:
                        content_encoded = b"%b%b" % (content_encoded, data)

                if "\r\n\r\n" in headers and not headers_complete:
                    logging.warning("[!] HEADER COMPLETED")
                    print("[!] HEADERS:")
                    print(headers)
                    headers_complete = True

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
                        BUFFER_SIZE = 1024*10
                        try:
                            save_file_name = request_path.split("/")[-1]
                            os.remove(save_file_name)
                        except:
                            None

                if bytes_received == content_length:
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
            Host: 192.168.167.6
            User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36
            """
        headers, content = send_command(
            ("127.0.0.1", 8000), create_request_headers(request_headers), False)
        print("[!] HEADERS:")
        print(headers)
        soup = BeautifulSoup(content, "html.parser")
        html_text = soup.get_text()
        print(html_text)

except KeyboardInterrupt:
    sys.exit(0)
