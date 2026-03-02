#!/usr/bin/env python3
import socket
import sys
import traceback
import ctypes
import numpy as np
import os
import time

# --- Load the Driver ---
# Make sure lkdriver_python.so is in the same folder!
dll_path = os.path.abspath("lkdriver_python.so")
if not os.path.exists(dll_path):
    print(f"Error: DLL not found at {dll_path}")
    sys.exit(1)

luke_driver = ctypes.CDLL(dll_path)

# --- Define C types ---
luke_driver.py_lk_start.restype = ctypes.c_int
luke_driver.py_lk_stop.restype = ctypes.c_int
luke_driver.py_lk_set_command.restype = None
luke_driver.py_lk_set_command.argtypes = [ctypes.POINTER(ctypes.c_double)]
luke_driver.py_lk_get_sensor.restype = ctypes.c_int
luke_driver.py_lk_get_sensor.argtypes = [ctypes.POINTER(ctypes.c_double)]

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

# --- Start Driver ---
print("Initializing Driver...", flush=True)
if luke_driver.py_lk_start() != 0:
    print("Failed to start driver. Check USB/Power.")
    client.close()
    sys.exit(1)
print("Driver Started. Background thread is handling SYNCs. You can power on the hand now", flush=True)
time.sleep(1) # Give it a second to stabilize

# Initial Command (Neutral/Zeros)
current_cmd = np.zeros(6, dtype=np.float64)

# Send initial zero command
cmd_ptr = current_cmd.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
luke_driver.py_lk_set_command(cmd_ptr)

loop_count = 0
try:
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

            # Parse the 1x6 array
            try:
                parts = msg.strip().split()
                if len(parts) != 6:
                    response = "Error: Please enter exactly 6 numbers."
                    print(response, flush=True)
                else:
                    new_values = [float(x) for x in parts]
                    current_cmd = np.array(new_values, dtype=np.float64)

                    # 4. Send to Driver
                    # This updates the global variable that the background thread reads.
                    # The NEXT time the hand sends a SYNC (0x80), it will get these new values.
                    cmd_ptr = current_cmd.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
                    luke_driver.py_lk_set_command(cmd_ptr)
                    print(f"   -> Updated: {current_cmd}", flush=True)

                    # Optional: Read Sensors to confirm it's alive
                    sensor_data = np.zeros(22, dtype=np.float64)
                    sensor_ptr = sensor_data.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
                    frame_count = luke_driver.py_lk_get_sensor(sensor_ptr)
                    print(f"   [Status] Frame Count: {frame_count} (sensors read)", flush=True)

                    response = "Command received"

            except ValueError:
                response = "Error: Invalid number format."

            print(f"About to send: {response}", flush=True)
            client.send(response.encode())
            print(f"SENT: {response}\n", flush=True)

        except Exception as e:
            print(f"ERROR in loop: {e}", flush=True)
            traceback.print_exc()
            break

except KeyboardInterrupt:
    print("\nInterrupted.", flush=True)

finally:
    print("Stopping Driver... Do not power off the hand until this completes.", flush=True)
    # Reset to zero before quitting (safer)
    zeros = np.zeros(6, dtype=np.float64)
    luke_driver.py_lk_set_command(zeros.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
    time.sleep(5.0)
    luke_driver.py_lk_stop()
    print("Driver Stopped.", flush=True)
    print("Closing client...", flush=True)
    client.close()
    print("Client closed", flush=True)