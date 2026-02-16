#!/usr/bin/env python3
import socket
import sys
import traceback

sys.stdout.flush()
sys.stderr.flush()

print("=" * 50, flush=True)
print("RPI_CLIENT STARTING", flush=True)
print("=" * 50, flush=True)

# Connect to the server (not bind!)
client = socket.socket()
print("Socket created", flush=True)

try:
    client.connect(('127.0.0.1', 7632))
    print("Connected to server at 127.0.0.1:7632\n", flush=True)
except Exception as e:
    print(f"CONNECTION FAILED: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

loop_count = 0
while True:
    loop_count += 1
    print(f"\n--- Loop iteration {loop_count} ---", flush=True)
    
    try:
        print("Waiting for message from server...", flush=True)
        msg = client.recv(1024).decode().strip()
        print(f"Raw received: '{msg}' (length: {len(msg)})", flush=True)
        
        if not msg or msg == "bye":
            print("Breaking loop (empty or bye)", flush=True)
            break
        
        print(f"Received: {msg}", flush=True)
        
        if msg == "1":
            response = "Hello!"
            print("Match! Setting response to 'Hello!'", flush=True)
        else:
            response = "Incorrect input, please type in a 1."
            print(f"No match. Msg was: '{msg}'", flush=True)
        
        print(f"About to send: {response}", flush=True)
        client.send(response.encode())
        print(f"SENT: {response}\n", flush=True)
        
    except Exception as e:
        print(f"ERROR in loop: {e}", flush=True)
        traceback.print_exc()
        break

print("Closing client...", flush=True)
client.close()
print("Client closed", flush=True)