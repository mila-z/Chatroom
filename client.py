import socket
import errno
import threading

class ChatClient:
    def __init__(self, ip, port, username):
        self.HEADER_LENGTH = 10
        self.IP = ip
        self.PORT = port
        self.username = username.encode('utf-8')
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.termination_flag = threading.Event()

    def connect(self):
        self.client_socket.connect((self.IP, self.PORT))
        self.client_socket.setblocking(False) 

        # send the username to the server
        self.username_header = self.generate_header(self.username)
        self.client_socket.send(self.username_header + self.username)

    def generate_header(self, message):
        return f'{len(message):<{self.HEADER_LENGTH}}'.encode('utf-8')

    def receive_messages(self):
        while not self.termination_flag.is_set():
            try:
                # receiving messages from the server 
                while True:
                    header = self.client_socket.recv(self.HEADER_LENGTH)

                    if not len(self.username_header):
                        print('Connection closed by the server')
                        self.termination_flag.set()
                        break

                    message_len = int(header.decode('utf-8').strip())
                    message = self.client_socket.recv(message_len).decode('utf-8')

                    print(message)
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK: #when there are no more messages to be received
                    print('Reading error', str(e))
                    self.client_socket.close()
                    self.termination_flag.set()
                    break
            except Exception as e:
                print('General error', str(e))
                self.client_socket.close()
                self.termination_flag.set()
                break

    def send_messages(self):
        while not self.termination_flag.is_set():
            message = input("")

            if message == '!logout':
                print('Logging out...')
                self.termination_flag.set()
                self.client_socket.close()
                break
            elif message:
                message = message.encode('utf-8')
                message_header = self.generate_header(message)
                self.client_socket.send(message_header + message)

    def run(self):
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
