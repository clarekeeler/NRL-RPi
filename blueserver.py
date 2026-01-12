import bluetooth
from threading import Thread

def receive_messages(client_sock):
    while True:
        try:
            msg = client_sock.recv(1024).decode().strip()
            if msg == "bye":
                print("Bye!")
                exit()
            
            print(f"Client: {msg}")
            
            if msg == "1":
                response = "Hello!"
            else:
                response = "Incorrect input, please type in a 1."
            
            client_sock.send(response.encode())
            
        except:
            exit()

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", 1))
server_sock.listen(1)

print("Waiting for connection...")
client_sock, address = server_sock.accept()
print(f"Connected to {address}")

# Start receiving
Thread(target=receive_messages, args=(client_sock,), daemon=True).start()

# Send messages
while True:
    msg = input("")
    client_sock.send(msg.encode())