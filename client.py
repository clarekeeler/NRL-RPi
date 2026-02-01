import socket
from threading import Thread
import os

class Client:
    def __init__(self, HOST, PORT):
        self.socket = socket.socket()
        self.socket.connect((HOST, PORT))
        self.talk_to_server()
    
    def talk_to_server(self):
        Thread(target=self.receive_message).start()
        self.send_message()
    
    def send_message(self):
        while True:
            client_message = input("")
            self.socket.send(client_message.encode())
    
    def receive_message(self):
        while True:  # Added this!
            server_message = self.socket.recv(1024).decode()
            if (server_message.strip() == "bye" or not server_message.strip()):
                os._exit(0)
            print("\033[1;31;40m" + "Server: " + server_message + "\033[0m")

Client('127.0.0.1', 7632)