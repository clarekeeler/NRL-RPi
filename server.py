#!/usr/bin/env python3
import socket
from threading import Thread
from bluezero import adapter
from bluezero import peripheral

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
RX_UUID = "12345678-1234-5678-1234-56789abcdef1"  # PC writes here
TX_UUID = "12345678-1234-5678-1234-56789abcdef2"  # PC reads here

class Server:
    def __init__(self):
        # Setup socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('127.0.0.1', 7632))
        self.sock.listen(1)
        print("Waiting for rpi_client...")
        self.client, _ = self.sock.accept()
        print("rpi_client connected!")
        
        # Setup BLE
        self.ble = peripheral.Peripheral(
            adapter.list_adapters()[0],
            local_name='raspberrypi'
        )
        
        # Add service
        self.ble.add_service(srv_id=1, uuid=SERVICE_UUID, primary=True)
        
        # RX Characteristic (PC writes to this)
        self.ble.add_characteristic(
            srv_id=1, chr_id=1, uuid=RX_UUID,
            value=[],
            notifying=False,
            flags=['write', 'write-without-response'],
            write_callback=self.on_pc_message,
            read_callback=None,
            notify_callback=None
        )
        
        # TX Characteristic (PC gets notifications from this)
        self.ble.add_characteristic(
            srv_id=1, chr_id=2, uuid=TX_UUID,
            value=[],
            notifying=False,
            flags=['notify'],
            write_callback=None,
            read_callback=None,
            notify_callback=self.on_tx_subscribe
        )
        
        self.tx_characteristic = None  # Will be set when client subscribes
        
        print("BLE ready!")
        
        # Listen for rpi_client responses
        Thread(target=self.listen_rpi_client, daemon=True).start()
    
    def on_pc_message(self, value, options):
        """PC writes → server → rpi_client"""
        msg = bytes(value).decode('utf-8').strip()
        print(f"PC → {msg}")
        self.client.send(msg.encode())
    
    def on_tx_subscribe(self, notifying, characteristic):
        """Called when PC subscribes to notifications"""
        if notifying:
            print("PC subscribed to notifications")
            self.tx_characteristic = characteristic
        else:
            print("PC unsubscribed from notifications")
            self.tx_characteristic = None
        return notifying
    
    def listen_rpi_client(self):
        """rpi_client → server → PC via TX characteristic"""
        while True:
            response = self.client.recv(1024).decode().strip()
            if response:
                print(f"RPI → {response}")
                # Send to PC via TX characteristic if subscribed
                if self.tx_characteristic:
                    self.tx_characteristic.set_value(response.encode())
    
    def run(self):
        """Start the BLE server"""
        print("Starting BLE server...")
        self.ble.publish()

if __name__ == "__main__":
    server = Server()
    server.run()