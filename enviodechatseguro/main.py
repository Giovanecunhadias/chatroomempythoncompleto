import socket
import select
import sys
import _thread
import hashlib
import tkinter as tk
from tkinter import scrolledtext, simpledialog

class ChatGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat")
        
        self.chat_log = scrolledtext.ScrolledText(master, state='disabled', width=60, height=20)
        self.chat_log.grid(row=0, column=0, padx=5, pady=5, columnspan=2)
        
        self.message_entry = tk.Entry(master, width=40)
        self.message_entry.grid(row=1, column=0, padx=5, pady=5)
        
        self.send_button = tk.Button(master, text="Send", width=10, command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=5, pady=5)
        
        self.IP_address = ""
        self.Port = 0
        self.nickname = ""
        self.server = None
        self.lista_de_clientes = []

        self.setup_connection()

    def setup_connection(self):
        self.IP_address = simpledialog.askstring("IP", "Digite seu Ip:")
        self.Port = int(simpledialog.askstring("Porta", "Digita a Porta:"))

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.IP_address, self.Port))
        self.server.listen(100)

        self.chat_log.configure(state='normal')
        self.chat_log.insert(tk.END, "Waiting for connections...\n")
        self.chat_log.configure(state='disabled')

        _thread.start_new_thread(self.accept_connections, ())

    def accept_connections(self):
        while True:
            conn, addr = self.server.accept()
            self.lista_de_clientes.append(conn)
            hashed_ip = hashlib.sha256(addr[0].encode()).hexdigest()
            self.display_message(hashed_ip + " Connected")

            _thread.start_new_thread(self.client_thread, (conn, addr))

    def client_thread(self, conn, addr):
        conn.send("Welcome to the Chat".encode())

        while True:
            try:
                message = conn.recv(2048).decode()
                if message:
                    hashed_ip = hashlib.sha256(addr[0].encode()).hexdigest()
                    self.display_message("<" + hashed_ip + "> " + message)
                    message_to_send = "<" + hashed_ip + "> " + message
                    self.broadcast(message_to_send, conn)
                else:
                    self.remove(conn)
            except Exception as e:
                print(e)
                continue

    def broadcast(self, message, connection):
        for clients in self.lista_de_clientes:
            if clients != connection:
                try:
                    clients.send(message.encode())
                except Exception as e:
                    print(e)
                    clients.close()
                    self.remove(clients)

    def remove(self, connection):
        if connection in self.lista_de_clientes:
            self.lista_de_clientes.remove(connection)

    def send_message(self):
        message = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        self.display_message("You: " + message)
        self.broadcast("You: " + message, None)

    def display_message(self, message):
        self.chat_log.configure(state='normal')
        self.chat_log.insert(tk.END, message + '\n')
        self.chat_log.configure(state='disabled')
        self.chat_log.yview(tk.END)

def main():
    root = tk.Tk()
    chat_gui = ChatGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
