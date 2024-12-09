import socket
import select 

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()

print('Server is listening...')

sockets_list = [server_socket]

clients = {}

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        # if there is no data, the client closed the connection
        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    #if someone closed abruptly
    except: 
        return False



while True:
    # select takes read list, write list and sockets we might error on 
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        # if someone just connected, accepting and handling the new connection 
        if notified_socket == server_socket: 
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)

            if user is False: 
                continue

            sockets_list.append(client_socket)

            clients[client_socket] = user

            print(f'Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf-8')}')

            # notifying everybody besides the new user, that the new user has joined the chat
            connection_message = f'{user['data'].decode('utf-8')} has joined the chat!'.encode('utf-8')
            connection_message_header = f'{len(connection_message):<{HEADER_LENGTH}}'.encode('utf-8')
            for client in clients:
                if client != client_socket:
                    client.send(connection_message_header + connection_message)
            
            # confirming to the new user that they have successfully joined the chatroom   
            confirmation_message = 'You have joined the chat!'.encode('utf-8')
            confirmation_message_header = f'{len(confirmation_message):<{HEADER_LENGTH}}'.encode('utf-8')
            client_socket.send(confirmation_message_header + confirmation_message)

        else:
            message = receive_message(notified_socket)

            # handling a disconnected user
            if message is False:
                user_left = clients[notified_socket]['data'].decode('utf-8')
                print(f'Closed connection from {user_left}')
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                
                # notify the rest of the users for the leaving of user
                leave_message = f'{user_left} has left the chat!'.encode('utf-8')
                leave_message_header = f'{len(leave_message):<{HEADER_LENGTH}}'.encode('utf-8')
                for client in clients:
                    client.send(leave_message_header + leave_message)
                
                continue
            
            user = clients[notified_socket]
            
            print(f'Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}')

            # send the message to everybody besides the 'sender'
            for client_socket in clients:
                if client_socket != notified_socket:
                    mess = f'{user['data'].decode('utf-8')} > {message['data'].decode('utf-8')}'.encode('utf-8')
                    mess_header = f'{len(mess):<{HEADER_LENGTH}}'.encode('utf-8')
                    client_socket.send(mess_header + mess)
    
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]