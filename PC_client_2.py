#!/usr/bin/env python3
import asyncio
from bleak import BleakClient, BleakScanner

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
RX_UUID = "12345678-1234-5678-1234-56789abcdef1"
TX_UUID = "12345678-1234-5678-1234-56789abcdef2"

def on_response(sender, data):
    msg = data.decode().strip()
    if msg:
        print(f"RPi: {msg}")

async def main():
    print("Scanning...")
    devices = await BleakScanner.discover(timeout=15.0)

    address = None
    for d in devices:
        print(d.name, d.address)  # helpful for debugging
        if d.name == "raspberrypi":        # confirm this matches your RPi's broadcast name
            address = d.address
            break

    if not address:
        print("RPi not found!")
        return

    print(f"Connecting to {address}...")
    async with BleakClient(address) as client:
        await client.start_notify(TX_UUID, on_response)
        print("Connected! Type messages (or 'bye' to quit):\n")

        while True:
            msg = await asyncio.to_thread(input, "You: ")
            msg = msg.strip()
            if msg:
                await client.write_gatt_char(RX_UUID, msg.encode())
                if msg == "bye":
                    break
            await asyncio.sleep(0.1)

asyncio.run(main())
