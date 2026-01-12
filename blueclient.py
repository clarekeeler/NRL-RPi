
import bluetooth
from threading import Thread

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode().strip()
            if msg == "bye":
                print("Bye!")
                exit()
            print(f"Server: {msg}")
        except:
            exit()

print("Searching for devices...")
devices = bluetooth.discover_devices()

if not devices:
    print("No devices found!")
    exit()

server_address = devices[0]  # Use first device found
print(f"Connecting to {server_address}...")

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((server_address, 1))
print("Connected!")


Thread(target=receive_messages, args=(sock,), daemon=True).start()

while True:
    msg = input("You: ")
    sock.send(msg.encode())
    if msg == "bye":
        exit()