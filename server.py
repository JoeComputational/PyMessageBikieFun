"""Server app for network messaging. Fill in IP and PORT in the config.py"""
import socket
import threading
from config import *


class Server:
    """Implementing Server functional class"""
    def __init__(self, host, port):
        """
        Given host and port - this then creates the class instance.
        :param host: IP-address string
        :param port: port integer
        """
        # instantiate socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind it to the host and port
        self.socket.bind((host, port))
        # start listening
        self.socket.listen()
        # lists for ips and names of connected users
        self.ips = []
        self.names = []

    def broadcast(self, message):
        """
        Send the messages to all connected users
        :param message: str
        :return: None
        """
        # iterate through clients and send message
        for client in self.ips:
            client.send(message)

    def handle(self, client):
        """
        Handle the particular client
        :param client: socket object of connected client
        :return: None
        """
        # infinite loop
        while True:
            try:
                # recive a message from the client
                message = client.recv(MESSAGE_SIZE)
                # broadcast this message
                self.broadcast(message)
            # remove disconnected client
            except (ConnectionResetError, ConnectionAbortedError):
                # get index of the client to remove
                index = self.ips.index(client)
                # remove the client ip from the list
                self.ips.remove(client)
                # close the socket of the client
                client.close()
                # get  the name of the client
                name = self.names[index]
                # message everyone that client left
                self.broadcast('{} left!'.format(name).encode('utf8'))
                # remove the name of the disconnected client
                self.names.remove(name)
                # print logs in the console
                print(f"{name} disconnected!")
                break

    def listen(self):
        """
        The main loop thats in control of listening to network sockets
        :return: None
        """
        # infinite loop
        while True:
            # accept the connection request if there is one
            client, address = self.socket.accept()
            # print logs in the console
            print(f"{address} connected!")

            # send a name request to the client
            client.send('#GETNAME#'.encode('utf8'))
            # receive a response
            name = client.recv(MESSAGE_SIZE).decode('utf8')
            # store the name
            self.names.append(name)
            # store the client socket
            self.ips.append(client)

            # print logs in the console
            print(f"User name is {name}")
            # broadcast the new user message
            self.broadcast(f"*{name} joined!\n".encode('utf8'))
            # send back a successfully connected message to the user
            client.send('*Connected successfully!\n'.encode('utf8'))

            # create a new thread for this client to handle his messages
            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()


# if we run the file as a script
if __name__ == "__main__":
    # make a Server class instance
    s = Server(HOST, PORT)
    # start listening
    s.listen()
