#!/usr/bin/env python3

import asyncio
from bleak import BleakClient, BleakScanner

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHAR_UUID = "12345678-1234-5678-1234-56789abcdef1"
""" need another characteristic (Rx and transition) """

def on_response(sender, data):
    """Print responses from RPi"""
    msg = data.decode().strip()
    if msg and msg != "Ready":
        print(f"RPi: {msg}")

async def main():
    # Find RPi
    print("Scanning...")
    devices = await BleakScanner.discover(timeout=15.0)
    
    address = None
    for d in devices:
        if d.name == "raspberrypi": 
            address = d.address
            break
    
    if not address:
        print("raspberrypi not found!")
        return
    
    # Connect
    print(f"Connecting to {address}...")
    async with BleakClient(address) as client:
        await client.start_notify(CHAR_UUID, on_response)
        print("Connected! Type messages (or 'bye' to quit):\n")
        
        loop = asyncio.get_event_loop()
        while True:
            msg = await loop.run_in_executor(None, input, "You: ")
            if msg.strip():
                await client.write_gatt_char(CHAR_UUID, msg.encode())
                if msg == "bye":
                    break
            await asyncio.sleep(0.1)

asyncio.run(main())