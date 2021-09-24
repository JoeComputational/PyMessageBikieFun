"""The client app for internal network messaging app."""
import socket
import threading
import tkinter as tk
from tkinter import ttk
from config import *
from random import choice


class ClientWindow(tk.Tk):
    # Client window class implementation
    def __init__(self):
        """
        Create a window with all needed elements - this is the GUI
        """
        # initialize the standard tk window
        super().__init__()
        # Set the window title
        self.title("Internal")
        # set the label "server"
        tk.Label(self, text="Server:").grid(column=0, row=0, sticky="E")

        # create edit box for an IP
        self.ip = tk.Entry(self, width=25)
        # set default value
        self.ip.insert(tk.END, HOST)
        # make element visible and aligned by a grid
        self.ip.grid(column=1, row=0, sticky="W")

        # make the "Connect" button
        self.connect = tk.Button(self, text="Connect", command=self.connect, width=10, height=3)
        # make element visible and aligned by a grid
        self.connect.grid(column=4, row=0, sticky="E", rowspan=3)

         # set the label "port"
        tk.Label(self, text="Port:").grid(column=0, row=1, sticky="E")

        # create edit box for a port
        self.port = tk.Entry(self, width=25)
        # make element visible and aligned by a grid
        self.port.grid(column=1, row=1, sticky="W")
        # set default value
        self.port.insert(tk.END, "55555")

        # set the label "Name"
        tk.Label(self, text="Name:").grid(column=0, row=2, sticky="E")

        # create edit box for a name
        self.name = tk.Entry(self, width=25)
        # make element visible and aligned by a grid
        self.name.grid(column=1, row=2, sticky="W")
        # set default value
        self.name.insert(tk.END, choice(NAMES))
        # create horizontal separator
        ttk.Separator(orient='horizontal').grid(column=0, row=4)

        # create a text widget for messages
        self.messages = tk.Text(self, width=50, height=20)
        # make element visible and aligned by a grid
        self.messages.grid(column=0, row=5, columnspan=5, sticky="es")
        # make a scrollbar for the messages text widget
        scrollbar = tk.Scrollbar(self, command=self.messages.yview)
        # add scrollbar to a text widget
        self.messages.config(yscrollcommand=scrollbar.set)
        # make element visible and aligned by a grid
        scrollbar.grid(column=6, row=5, columnspan=5, sticky="nsew")
        # create horizontal separator
        ttk.Separator(orient='horizontal').grid(column=0, row=6)
        # make Text widget uneditable
        self.messages.config(state=tk.DISABLED)

        # create a text widget for writing a message
        self.message = tk.Text(self, width=40, height=4)
        # make element visible and aligned by a grid
        self.message.grid(column=0, row=7, columnspan=3, sticky="ne")
        # put the editing focus on the message writing field
        self.message.focus()

        # make the "Send" button
        self.send = tk.Button(self, text="Send", command=self.send_msg, width=10, height=3)
        # make element visible and aligned by a grid
        self.send.grid(column=4, row=7, sticky="E")
        # create horizontal separator
        ttk.Separator(orient='horizontal').grid(column=0, row=8)

    def update_messages(self, message):
        """
        Add new message to the messages text widget
        :param message: str
        :return: None
        """
        # make text widget editable
        self.messages.config(state=tk.NORMAL)
        # add message text to the end
        self.messages.insert(tk.END, message)
        # scroll to the end
        self.messages.see(tk.END)
        # make text widget uneditable
        self.messages.config(state=tk.DISABLED)

    def connect(self):
        """
        The function for connecting to the server. The function is attached to the "Connect" button. (This SUCKED)
        :return: None
        """
        try:
            # create socket for connection
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connect to ip and port from corresponding fields
            self.client.connect((self.ip.get(), int(self.port.get())))
        except ConnectionRefusedError:
            # print error log in the messages text widget
            self.update_messages("#Can't connect to the server!")
            # end the function running
            return

        # waiting for a name request
        while True:
            try:
                # receive message from the server
                message = self.client.recv(MESSAGE_SIZE).decode('utf8')
                # if the message is the name request
                if message == '#GETNAME#':
                    # send name from the corresponding field
                    self.client.send(self.name.get().encode('utf8'))
                    # stop the while loop
                    break
                else:
                    # print other messages in the messages text widget
                    self.update_messages(message)
            except BaseException:
                # catch all the possible errors and print message in the message box
                self.update_messages("An error has been occurred!")
                # close the client socket
                self.client.close()
                # end the function running
                return

        # make a thread for receiving messages from the server
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def receive(self):
        """
        The function to receive messages from the server
        :return: None
        """
        # infinite loop
        while True:
            try:
                # receive message from the server
                message = self.client.recv(MESSAGE_SIZE).decode('utf8')
                # print the received message in the messages text widget
                self.update_messages(message)
            # if connection is reset by server
            except ConnectionResetError:
                # print the log message in the messages text widget
                self.update_messages("#Disconnected from server!")
                # close the client socket
                self.client.close()
                # end the function running
                return

    def send_msg(self):
        """
        Send the message from the message text box to the server - this is linked similaraly to the connect button (SUCKED!)
        :return: None
        """
        # add the name to the message and format it before sending
        message = f'{self.name.get()}: {self.message.get("1.0", tk.END)}'
        # send message to the server
        self.client.send(message.encode('utf8'))
        # clear the message that has been sent
        self.message.delete('1.0', tk.END)


# if we run the file as a script
if __name__ == "__main__":
    # instantiate client window
    cw = ClientWindow()
    # run the main loop to manage actions
    cw.mainloop()
