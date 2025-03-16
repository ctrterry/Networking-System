#  * Program Name: Networking System -> Proxy
#  * Author: Tianren Chen
#  * Date: Feb 19/2025 (Final_Version_v04)
#  * Description:
    # Testing case explain
    # Learning  Socket and Json
    # Link: https://docs.python.org/3/howto/sockets.html.
    # Link: https://docs.python.org/3/library/json.html
import socket
import json

PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8000
BLOCKED_IPS = ['10.10.10.10']  
_max_buffersize = 1024

# Handling about the client parts
def handle_client(conn, addr):
    print(f"Handling connection from {addr}")
    # https://stackoverflow.com/questions/64237717/conn-sendhi-encode-brokenpipeerror-errno-32-broken-pipe-socket
    data = conn.recv(_max_buffersize).decode()
    print(f"Received JSON data: {data}")
    
    try:
        client_data = json.loads(data)
        server_ip = client_data['server_ip']
        server_port = client_data['server_port']
        message = client_data['message']
    except (json.JSONDecodeError, KeyError) as e:
        error_msg = "Error: Invalid JSON format"
        conn.send(error_msg.encode())
        conn.close()
        return
    
    print(f"Forwarding message '{message}' to {server_ip}:{server_port}")
    
    
    # Handling about the IP filtering (Third Requirement)
    if server_ip in BLOCKED_IPS:
        print(f"Blocked server IP: {server_ip}")
        conn.send("Error".encode())
        conn.close()
        return
    
    # My proxy will handling the server's IP from the client's data 
    # Also handling about the proxy sending the correct data to the Serives
    # Handling the recived response from the serves 
    # Reference useed: 
    # https://stackoverflow.com/questions/55661626/with-socket-socketsocket-af-inet-socket-sock-stream-as-s-get-error-attribut
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.connect((server_ip, server_port))
            server_socket.sendall(message.encode()) # encoding my message and sending to the Server
            response = server_socket.recv(_max_buffersize).decode() # Decoding my response msg from Server
            print(f"Received server response: {response}")
    except Exception as errorHanlding:
        response = f"Error: {str(errorHanlding)}"  # Error Handling if the response has issues
        print(response)
    # https://stackoverflow.com/questions/64237717/conn-sendhi-encode-brokenpipeerror-errno-32-broken-pipe-socket
    conn.send(response.encode())
    conn.close()

def run_proxy():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((PROXY_HOST, PROXY_PORT))
        s.listen()
        print(f"Proxy server running on {PROXY_HOST}:{PROXY_PORT}")
        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)

if __name__ == '__main__':
    run_proxy()
