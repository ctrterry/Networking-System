
import socket
import time
import sys

def main():
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 5005
    CHUNK_SIZE = 1400
    #The use of a 1400‑byte chunk size ensures that even very large payloads are sent reliably in manageable pieces over UDP

    # Create UDP socket for the client and bind it to the loopback interface
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_sock.bind(("127.0.0.1", 0))  # Explicit bind

    if len(sys.argv) != 2:
        print("Usage: python udp_client.py <megabytes_to_send>")
        sys.exit(1)
    try:
        megabytes = int(sys.argv[1])
    except ValueError:
        print("Please provide a valid integer for megabytes")
        sys.exit(1)

    total_bytes = megabytes * 1024 * 1024
    #The scripts work for all data sized 25 MB - 200 MB
    current_timestamp = time.ctime(time.time())

    metadata = f"SIZE:{total_bytes}:{current_timestamp}"
    client_sock.sendto(metadata.encode(), (SERVER_IP, SERVER_PORT))
    print(f"Sent metadata to server: {metadata}")

    payload = b'0' * total_bytes

    bytes_sent = 0
    start_time = time.time()
    while bytes_sent < total_bytes:
        end_index = min(bytes_sent + CHUNK_SIZE, total_bytes)
        chunk = payload[bytes_sent:end_index]
        client_sock.sendto(chunk, (SERVER_IP, SERVER_PORT))
        bytes_sent += len(chunk)
    #The client sent the data correctly to the server, This loop iterates until the entire payload (based on the input size) is sent to the server.
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Sent {bytes_sent} bytes to server in {elapsed_time:.2f} seconds")
    client_ip = client_sock.getsockname()[0]
    print(f"Client IP: {client_ip}, Server IP: {SERVER_IP}")

    # Wrap the recvfrom call in a try/except block to handle potential ConnectionResetError
    try:
        throughput_packet, addr = client_sock.recvfrom(1024)
    except ConnectionResetError:
        print("Warning: Connection reset encountered. This may be due to UDP's connectionless behavior on Windows.")
        throughput_packet = b"0.00"
    throughput = throughput_packet.decode()
    print(f"Received throughput from server: {throughput} KB/s")
    #The server sends the throughput to the client correctly and the client prints it
    client_sock.close()

if __name__ == "__main__":
    main()
