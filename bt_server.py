#!/usr/bin/env python3

import asyncio
from bleak import BleakServer, BleakGATTCharacteristic, BleakGATTServiceCollection
from bleak.backends.characteristic import GattCharacteristicsFlags
import socket

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHAR_UUID = "12345678-1234-5678-1234-56789abcdef1"

response = b"Ready"
characteristic = None

# Connect to Program 3
print("Connecting to Program 3...")
sock = socket.socket()
sock.connect(('127.0.0.1', 7632))
print("Connected!\n")

def read_cb(char):
    return response

def write_cb(char, value):
    global response
    msg = value.decode().strip()
    if not msg:
        return
    
    print(f"PC → {msg}")
    sock.send(msg.encode())
    
    resp = sock.recv(1024).decode().strip()
    print(f"Program 3 → {resp}\n")
    
    response = resp.encode()
    if characteristic:
        asyncio.create_task(characteristic.notify(response))

async def main():
    global characteristic
    
    def setup(sc: BleakGATTServiceCollection):
        global characteristic
        svc = sc.add_service(SERVICE_UUID)
        characteristic = sc.add_characteristic(
            svc, CHAR_UUID,
            GattCharacteristicsFlags.read | GattCharacteristicsFlags.write | GattCharacteristicsFlags.notify,
            None, read_cb, write_cb
        )
    
    print("Starting Bluetooth server...")
    async with BleakServer("RPi-Server", setup):
        print("Waiting for PC...\n")
        while True:
            await asyncio.sleep(1)

asyncio.run(main())