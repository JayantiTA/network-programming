def parse_log_file(log_file):
    with open(log_file, 'r') as file:
        log_lines = file.readlines()

    ehlo_message = None
    tls_support_message = None
    ready_message = None
    hashed_username = None
    hello_reply = None
    connection_closed_message = None

    for line in log_lines:
        if line.startswith("send: 'ehlo"):
            ehlo_message = line.strip().split("send: ")[1]
        elif line.startswith("reply: b'250-STARTTLS"):
            tls_support_message = line.strip()
        elif line.startswith("reply: retcode (220)"):
            ready_message = line.strip()
        elif line.startswith("send: 'AUTH LOGIN"):
            hashed_username = line.strip().split("send: ")[1]
        elif line.startswith("reply: b'250-"):
            if "Hello" in line:
                hello_reply = line.strip()
        elif line.startswith("reply: retcode (221)"):
            connection_closed_message = line.strip()

    return ehlo_message, tls_support_message, ready_message, hashed_username, hello_reply, connection_closed_message

# Memanggil fungsi parse_log_file dan mencetak jawaban
log_file = "answer.log"  # Ganti dengan nama file log yang sesuai
ehlo_message, tls_support_message, ready_message, hashed_username, hello_reply, connection_closed_message = parse_log_file(log_file)

print("1. Pesan EHLO yang dicetak:")
print(ehlo_message)
print()
print("2. Pesan yang menyatakan bahwa server mendukung TLS:")
print(tls_support_message)
print()
print("3. Pesan yang menyatakan server siap mengirim email:")
print(ready_message)
print()
print("4. Pesan yang menunjukkan username yang sudah di-hash:")
print(hashed_username)
print()
print("5. Pesan balasan server dari sebuah hello message dari client:")
print(hello_reply)
print()
print("6. Pesan bahwa koneksi telah ditutup:")
print(connection_closed_message)
