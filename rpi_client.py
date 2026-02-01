#!/usr/bin/env python3

import socket

print("Starting...\n")
server = socket.socket()
server.bind(('127.0.0.1', 7632))
server.listen()

client, addr = server.accept()
print(f"Connected!\n")

while True:
    msg = client.recv(1024).decode().strip()
    if not msg or msg == "bye":
        break
    
    print(f"Received: {msg}")
    

    if msg == "1":
        response = "Hello!"
    else:
        response = "Incorrect input, please type in a 1."
    
    print(f"Sending: {response}\n")
    client.send(response.encode())