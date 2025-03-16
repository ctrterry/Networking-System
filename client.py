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

_proxy_host = '127.0.0.1'
_proxy_port = 8000


# Since, the input should be accept a 4-character string as an input to be forwarded
message = input("Enter the 4 characters message, like 'ping': ")
if len(message) != 4:
    print("Message must be exactly 4 characters, Error to exit it")
    exit()

# As given information from the Part 2,  JSON formating 
data = {
    "server_ip": "127.0.0.1", # The servies IP destination 
    "server_port": 7000,      # The serives port destination
    "message": message        # The acutal message trying to send it
}

# Convert the data to the json parse 
# Reference: https://www.geeksforgeeks.org/json-dumps-in-python/
json_data = json.dumps(data)


# Learning Link: https://www.geeksforgeeks.org/socket-programming-python/
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((_proxy_host, _proxy_port))
    s.sendall(json_data.encode())
    response = s.recv(1024).decode()

print(f"Sent message is : {message}")
print(f"Received response messgae is : {response}")
print(f"JSON data sent is : {json_data}")
