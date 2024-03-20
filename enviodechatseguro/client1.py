import socket 
import select 
import sys 
import threading

def receive_from_server(server_socket):
    while True:
        try:
            message = server_socket.recv(2048)
            if message:
                print(message.decode())
        except Exception as e:
            print(e)
            server_socket.close()
            break

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
if len(sys.argv) != 3: 
    print("Correct usage: script, IP address, port number")
    exit() 
IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 
server.connect((IP_address, Port))

# Start a thread to handle receiving messages from the server
receive_thread = threading.Thread(target=receive_from_server, args=(server,))
receive_thread.daemon = True
receive_thread.start()

while True: 
    # Check for user input
    message = input("$: ")
    if message:
        server.send(message.encode())
    else:
        # If no input, sleep briefly to prevent busy waiting
        time.sleep(0.1)
