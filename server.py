import socket
import select #os system level i/o capabilities, i.e. the code will run the same on any os

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()

# the list of clients = the list of sockets
sockets_list = [server_socket]

# client_socket is the key, client_data is the value = {'header': len username, 'data': username}
clients = {}

def receive_message(client_socket):
    try:
        # will be handled by the client. first it will send the length of the message, and then it will send the actual message
        message_header = client_socket.recv(HEADER_LENGTH)

        # if we didnt get any data, the client closed the connection
        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except: #if someone closed abruptly
        return False


#event loop
while True:
    # select takes read list, write list and sockets we might error on 
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket: #smn just connected and we need to accept + the connection
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            if user is False: #smn disconnected
                continue

            sockets_list.append(client_socket)

            clients[client_socket] = user

            print(f'Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf-8')}')
        else:
            message = receive_message(notified_socket)
            if message is False:
                print(f'Closed connection from {clients[notified_socket]['data'].decode('utf-8')}')
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            
            user = clients[notified_socket]
            print(f'Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}')

            # move into a broadcast function
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
    
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]