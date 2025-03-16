
import socket
import time

def main():
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 5005
    BUFFER_SIZE = 65535

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind((SERVER_IP, SERVER_PORT))
    print(f"Server started on {SERVER_IP}:{SERVER_PORT}")

    metadata_packet, client_addr = server_sock.recvfrom(4096)
    metadata = metadata_packet.decode()
    print(f"Received metadata from client {client_addr}: {metadata}")

    # Use split with a maxsplit of 2 so that the timestamp is preserved even if it contains colons.
    try:
        parts = metadata.split(":", 2)
        if len(parts) != 3 or parts[0] != "SIZE":
            raise ValueError("Incorrect metadata format")
        total_bytes_expected = int(parts[1])
        client_timestamp = parts[2]
    except Exception as e:
        print("Error parsing metadata:", e)
        server_sock.close()
        return

    print(f"Metadata indicates a payload size of {total_bytes_expected} bytes.")
    print(f"Client timestamp: {client_timestamp}")
    
    start_time = time.time()
    total_received = 0

    while total_received < total_bytes_expected:
        data, addr = server_sock.recvfrom(BUFFER_SIZE)
        total_received += len(data)

    end_time = time.time()
    elapsed_time = end_time - start_time
    throughput_kbps = (total_received / elapsed_time) / 1024.0 
    #The throughput is calculated in KB
    # and the server calculates the throughput correctly, i.e., the formula is correctly implemented

    print(f"Data received at server timestamp: {time.ctime(end_time)}")
    print(f"Total bytes received: {total_received}")
    print(f"Time taken: {elapsed_time:.2f} seconds")
    print(f"Throughput: {throughput_kbps:.2f} KB/s")
    print(f"Client IP: {client_addr[0]}, Server IP: {SERVER_IP}")

    throughput_message = f"{throughput_kbps:.2f}"
    server_sock.sendto(throughput_message.encode(), client_addr)
    #The server sends the throughput to the client correctly and the client prints it
    server_sock.close()

if __name__ == "__main__":
    main()
