#!/usr/bin/env python3
import socket
import sys

sys.stdout.flush()
sys.stderr.flush()

print("Starting...\n", flush=True)

# Connect to the server (not bind!)
client = socket.socket()
client.connect(('127.0.0.1', 7632))
print(f"Connected to server!\n", flush=True)

while True:
    msg = client.recv(1024).decode().strip()
    if not msg or msg == "bye":
        break
    
    print(f"Received: {msg}", flush=True)
    
    if msg == "1":
        response = "Hello!"
    else:
        response = "Incorrect input, please type in a 1."
    
    print(f"Sending: {response}\n", flush=True)
    client.send(response.encode())

client.close()