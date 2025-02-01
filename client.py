import socket
import errno
import threading
from utils import HEADER_LENGTH, generate_header

class ChatClient:
    LOGOUT_COMMAND = '!logout'

    def __init__(self, ip, port, username):
        self.IP = ip
        self.PORT = port
        self.username = username.encode('utf-8')
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.termination_flag = threading.Event()

    def connect(self):
        """Connect to the server and send the username."""
        self.client_socket.connect((self.IP, self.PORT))
        self.client_socket.setblocking(False) 
        self.username_header = generate_header(self.username)
        self.client_socket.send(self.username_header + self.username)

    def terminate(self):
        """Manage client resources."""
        self.termination_flag.set()
        self.client_socket.close()

    def receive_messages(self):
        """Continuously receive messages from the server."""
        while not self.termination_flag.is_set():
            try:
                while True:
                    header = self.client_socket.recv(HEADER_LENGTH)
                    if not len(self.username_header):
                        print('Connection closed by the server')
                        self.termination_flag.set()
                        break

                    message_len = int(header.decode('utf-8').strip())
                    message = self.client_socket.recv(message_len).decode('utf-8')
                    print(message)
            except IOError as e:
                if e.errno not in (errno.EAGAIN, errno.EWOULDBLOCK): #when there are no more messages to be received
                    print('Reading error', str(e))
                    self.terminate()
                    break
            except Exception as e:
                print('General error', str(e))
                self.terminate()
                break

    def send_messages(self):
        """Continuously send messages to the server."""
        while not self.termination_flag.is_set():
            message = input("")

            if message == self.LOGOUT_COMMAND:
                print('Logging out...')
                self.terminate()
                break
            elif message:
                message = message.encode('utf-8')
                message_header = generate_header(message)
                self.client_socket.send(message_header + message)

    def run(self):
        """Start the client and manage threads."""
        self.connect()

        # creating new threads that will handle receiving and sending messages from and to other users
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.send_thread = threading.Thread(target=self.send_messages, daemon=True)

        # start the threads
        self.send_thread.start()
        self.receive_thread.start()

        self.send_thread.join()
        self.termination_flag.set()
        self.receive_thread.join()

if __name__ == "__main__":
    username = input('Username: ')
    client = ChatClient('127.0.0.1', 1234, username)
    client.run()
