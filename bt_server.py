#!/usr/bin/env python3

import socket
from bluezero import peripheral

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHAR_UUID = "12345678-1234-5678-1234-56789abcdef1"

response = []  
sock = None
char = None

def read_callback():
    return response

def write_callback(value):
    global response
    msg = bytes(value).decode().strip()
    if msg:
        print(f"PC → {msg}")
        sock.send(msg.encode())
        resp = sock.recv(1024).decode().strip()
        print(f"Program 3 → {resp}\n")
        response = list(resp.encode())  # Convert to list of bytes
        char.set_value(response)

# Connect to Program 3
print("Connecting to Program 3...")
sock = socket.socket()
sock.connect(('127.0.0.1', 7632))
print("Connected!\n")

# Setup BLE with explicit adapter address
app = peripheral.Peripheral(
    'B8:27:EB:10:2F:A3',
    local_name='RPi-Server'
)
app.add_service(srv_id=1, uuid=SERVICE_UUID, primary=True)
char = app.add_characteristic(
    srv_id=1, chr_id=1, uuid=CHAR_UUID,
    value=[],  # Start with empty list
    notifying=False,
    flags=['read', 'write', 'notify'],
    read_callback=read_callback,
    write_callback=write_callback
)

print("Starting BLE server...\n")
app.publish()