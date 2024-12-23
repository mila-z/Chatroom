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

# key: socket, value: {'header': username header, 'data': username}
clients = {}


def generate_header(message):
    return f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        # if there is no data, the client closed the connection
        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    #if someone closed abruptly
    except Exception as e: 
        print(f'Error receiving message: {e}')
        return False


def send_message_to_all_except_sender(sender_socket, message):
    for client_socket in clients:
        if client_socket != sender_socket:
            client_socket.send(message)


# accepting and handling new connection
def handle_new_connection(client_socket, client_address, user):
    sockets_list.append(client_socket)

    clients[client_socket] = user

    print(f'Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf-8')}')

    # notifying everybody besides the new user, that the new user has joined the chat
    connection_message = f'{user['data'].decode('utf-8')} has joined the chat!'.encode('utf-8')
    connection_message_header = generate_header(connection_message)
    send_message_to_all_except_sender(client_socket, connection_message_header + connection_message)
            
    # confirming to the new user that they have successfully joined the chatroom   
    confirmation_message = 'You have joined the chat!'.encode('utf-8')
    confirmation_message_header = generate_header(confirmation_message)
    client_socket.send(confirmation_message_header + confirmation_message)


# handling a disconnection
def handle_disconnection(disconnected_socket):
    disconnected_user = clients[disconnected_socket]['data'].decode('utf-8')

    print(f'Closed connection from {disconnected_user}')
    
    sockets_list.remove(disconnected_socket)
    del clients[disconnected_socket]
                
    # notify the rest of the users for the leaving of user
    leave_message = f'{disconnected_user} has left the chat!'.encode('utf-8')
    leave_message_header = generate_header(leave_message)

    for client in clients:
        client.send(leave_message_header + leave_message)


def show_active_users(sender_socket):
    
    for client_socket in clients:
        if client_socket != sender_socket:
            message = ('->' + clients[client_socket]['data'].decode('utf-8')).encode('utf-8')
            message_header = generate_header(message)
            sender_socket.send(message_header + message)
        elif len(clients) == 1 and client_socket == sender_socket:
            message = ('no one but you is active').encode('utf-8')
            message_header = generate_header(message)
            sender_socket.send(message_header + message)

def send_private_message(sender_user, receiver_user, message):
    sender_user_encoded = sender_user.encode('utf-8')
    receiver_user_encoded = receiver_user.encode('utf-8')
    found = False
    for client_socket in clients:
        if clients[client_socket]['data'] == receiver_user_encoded:
            private_message = f'privately {sender_user} > {message}'
            private_message_header = generate_header(private_message)
            private_message = private_message.encode('utf-8')
            client_socket.send(private_message_header + private_message) 
            found = True
        
        if clients[client_socket]['data'] == sender_user_encoded:
            sender_socket = client_socket
    
    if not found:
        message = f'{receiver_user} is not online'
        message_header = generate_header(message)
        message = message.encode('utf-8')
        sender_socket.send(message_header + message)

# broadcast sent message
def broadcast_message_to_users(sender_socket, message):
    user = clients[sender_socket]

    username = user['data'].decode('utf-8')
    message_data = message['data'].decode('utf-8')

    if message_data == '!who':
        show_active_users(sender_socket)
        return
    elif message_data.split(' ')[0] == '!msg':
        _, receiver_user, private_message = message_data.split(' ', 2)
        send_private_message(username, receiver_user, private_message)
        return

    print(f'Received message from {username}: {message_data}')

    broadcast_message = f'{username} > {message_data}'.encode('utf-8')
    broadcast_message_header = generate_header(broadcast_message)

    send_message_to_all_except_sender(sender_socket, broadcast_message_header + broadcast_message)


while True:
    # select takes read list, write list and sockets we might error on 
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        # new connection
        if notified_socket == server_socket: 
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)

            if user is False: 
                continue

            handle_new_connection(client_socket, client_address,user)
        # standard message
        else:
            message = receive_message(notified_socket)

            # lost connection
            if message is False:
                handle_disconnection(notified_socket)
                continue
            
            broadcast_message_to_users(notified_socket, message)
    
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]