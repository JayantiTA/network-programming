import socket
import logging
import gzip
import ssl
from lxml import html, etree
BUFFER_SIZE=1

def create_request_headers(req_str):
    # Generate request based on HTTP protocol
    data = ""
    for head in req_str.split("\n"):
        if head != "":
            data += f"{head}\r\n"

    data += "\r\n"
    return data

def create_connection_secure(dest_addr='localhost',port=12000):
     try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (dest_addr, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        secure_socket = ssl.wrap_socket(sock, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)
        logging.warning(secure_socket.getpeercert())
        return secure_socket
     except Exception as ee:
        logging.warning(f"error {str(ee)}")

def create_connection(dest_addr='localhost',port=8000):
     try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (dest_addr, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
     except Exception as ee:
        logging.warning(f"error {str(ee)}")

def send_request(server, command,flag_secure=False):
    headers = ""
    content_encoded = b""
    content = ""
    content_encoding="utf-8"
    content_length=-1

    bytes_received=0
    headers_complete=False

    alamat_server = server[0]
    port_server = server[1]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if flag_secure == True:
        sock = create_connection_secure(alamat_server,port_server)
    else:
        sock = create_connection(alamat_server,port_server)

    try:
        logging.warning(f"sending data ")
        sock.sendall(command.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(BUFFER_SIZE)
            if data:
                #data is not empty, concat with previous content
                # print(data)
                
                if not headers_complete: # alias headers belum selesai dibaca
                    headers += data.decode()
                else: # encode datanya pakai encoding dari headers
                    bytes_received += 1

                    if content_encoding == "utf-8":
                        content += data.decode()
                    else:
                        content_encoded = b"%b%b" % (content_encoded, data)

                if "\r\n\r\n" in headers and not headers_complete:
                    logging.warning("HEADER COMPLETED")
                    headers_complete = True

                    # read content-encoding and content-length
                    for head in headers.split("\r\n"):
                        if "Content-Encoding:" in head:
                            content_encoding = head.split("Content-Encoding: ")[1]
                        if "Content-Length:" in head:
                            content_length = int(head.split("Content-Length: ")[1])
                    
                    logging.warning(f"Content-Encoding: {content_encoding}")
                    logging.warning(f"Content-Length: {content_length}")

                # logging.warning(f"bytes_received = {bytes_received} | content_length = {content_length}")
                if bytes_received == content_length:
                    if content_encoding == "gzip":
                        content = gzip.decompress(content_encoded).decode()
                    
                    break
            else:
                print("No More Data Received")
                # no more data, stop the process by break
                break
        
        logging.warning("data receive is done~")
        # print(content)
        return headers, content
    except Exception as ee:
        logging.warning(f"error during data receiving {str(ee)}")
        return False
    
request_header = """
GET / HTTP/1.1
Host: www.its.ac.id
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
"""

headers,contents = send_request(("www.its.ac.id",443),create_request_headers(request_header),True)
print("-----------------------------")
print("================Headers==============")
print(headers)
# print(contents)
print("===================================")
print("================Jawaban 1,2,3==============")
for head in headers.split("\r\n"):
    if("HTTP" in head):
        http_ver = head.split(" ")[0]
        http_stat_code = head.split(http_ver)[1].strip()
    if ("Content-Encoding" in head):
        content_encoding = head.split("Content-Encoding: ")[1]
# 1. Cetaklah status code dan deskripsinya dari HTTP response header
print(f"1. Status Code\t\t| {http_stat_code}")

# 2. Cetaklah versi Content-Encoding dari HTTP response header
print(f"2. Content-Encoding\t| {content_encoding}")

# 3. Cetaklah versi HTTP dari HTTP response header
print(f"3. HTTP Version\t\t| {http_ver}")
print("===================================")

#================================================================================================

request_header = """
GET / HTTP/1.1
Host: classroom.its.ac.id
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
"""
headers, content = send_request(("classroom.its.ac.id", 443), create_request_headers(request_header), True)
print()
print(headers)
# 4. Cetaklah property charset pada Content-Type dari HTTP response header pada halaman classroom.its.ac.id
for head in headers.split("\r\n"):        
    if "Content-Type:" in head:
        content_type = head.split("Content-Type: ")[1]
        charset = content_type.split("charset=")[1]

print(f"4. Charset\t\t| {charset}")
# print("5. Dapatkanlah daftar menu pada halaman utama classroom.its.ac.id dengan melakukan parsing HTML")
# Print biar lebih rapi

def get_all_texts(els, class_name):
    return [e.text_content() for e in els.find_class(class_name)]

print("=================================== jawaban 5 =================")
# print(content)
root = html.fromstring(content) #https://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml
print("\n\n\n\n")
mainmenu_texts = get_all_texts(root, "navbar-nav h-100 wdm-custom-menus links")
html_text = "".join(mainmenu_texts)
print(html_text)