#  * Program Name: Networking System -> Proxy
#  * Author: Tianren Chen
#  * Date: Feb 19/2025 (Final_Version_v04)
#  * Description:
    # Testing case explain
    # Learning  Socket and Json
    # Link: https://docs.python.org/3/howto/sockets.html.
    # Link: https://docs.python.org/3/library/json.html
    
import socket

# We need specific the port detials
# Client sends JSON with server_ip '127.0.0.1
services_ip = '127.0.0.1'
_connection_port = 7000
_max_buffersize = 1024


# Trying to creative a new TCP. Using the socket 
# Reference: https://www.geeksforgeeks.org/socket-programming-python/
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_of_server:
    socket_of_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_of_server.bind((services_ip, _connection_port))
    socket_of_server.listen(1)
    print(f"Server is listening on port {_connection_port}...")

    # Handling error, if we can't accept from the connection! 
    try:
        conn, addr = socket_of_server.accept()
        print(f"Connection was accepted from {addr}")
    except socket.error as error_handling:
        print(f"Error accepting connection: {error_handling}")
        # If we can't accept a connection, no point continuing
        exit(1)

    # Use the connection in a context manager
    with conn:
        while True:
            data = conn.recv(_max_buffersize)
            if not data:
                break  # Client closed the connection

            print(f"Message received from client: {data.decode()}")
            response = "pong"
            conn.sendall(response.encode())
        # print("The connection was closed From the Serive Side.") # Debug
