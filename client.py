import socket
import errno
import threading
import sys

HEADER_LENGTH = 10

IP = '127.0.0.1'
PORT = 1234

my_username = input('Username: ')
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False) # the recieve functionality won't be blocking

#send username to the server
username = my_username.encode('utf-8')
username_header = f'{len(username):<{HEADER_LENGTH}}'.encode('utf-8')
client_socket.send(username_header + username)

termination_flag = threading.Event()

def receive_messages():
    while not termination_flag.is_set():
        try:
            while True:
                # username_header = client_socket.recv(HEADER_LENGTH)
                header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print('Connection closed by the server')
                    termination_flag.set()
                    break
                
                # username_length = int(username_header.decode('utf-8').strip())
                # username = client_socket.recv(username_length).decode('utf-8')
# 
                # message_header = client_socket.recv(HEADER_LENGTH)
                # message_length = int(message_header.decode('utf-8').strip())
                # message = client_socket.recv(message_length).decode('utf-8')

                mess_len = int(header.decode('utf-8').strip())
                mess = client_socket.recv(mess_len).decode('utf-8')

                print(mess)
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK: #when there are no more messages to be received
                print('Reading error', str(e))
                client_socket.close()
                termination_flag.set()
                break
        except Exception as e:
            print('General error', str(e))
            client_socket.close()
            termination_flag.set()
            break


def send_messages():
    while not termination_flag.is_set():
        message = input("")

        if message == '!logout':
            print('Logging out...')
            termination_flag.set()
            client_socket.close()
            break
        elif message:
            message = message.encode('utf-8')
            message_header = f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')
            client_socket.send(message_header + message)

# creating a new thread that will handle receiving messages from other users
receive_thread = threading.Thread(target=receive_messages, daemon=True)
send_thread = threading.Thread(target=send_messages, daemon=True)

# start the threads
send_thread.start()
receive_thread.start()

send_thread.join()
termination_flag.set()
receive_thread.join()

print('Client program exited')