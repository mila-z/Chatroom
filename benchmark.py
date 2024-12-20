import socket
import threading
import time

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234
NUM_CLIENTS = int(input('Number of clients: '))
NUM_MESSAGES = int(input('Number of messages per client: '))

def generate_header(message):
    return f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')

def client_task(client_id, results):
    try:
        # connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))

        # send a username to the server
        username = f'User{client_id}'.encode('utf-8')
        username_header = generate_header(username)
        client_socket.send(username_header + username)
    
        # measure time for sending and recieving messages
        start_time = time.time()
        for _ in range(NUM_MESSAGES):
            message = f'Hello from {client_id}'.encode('utf-8')
            message_header = generate_header(message)
            client_socket.send(message_header + message)

            # receive response from server
            response_header = client_socket.recv(HEADER_LENGTH)
            response_length = int(response_header.decode('utf-8').strip())
            client_socket.recv(response_length)
        
        end_time = time.time()

        results[client_id] = end_time - start_time

        client_socket.close()
    except Exception as e:
        results[client_id] = str(e)

if __name__ == '__main__':
    results = {}
    threads = []

    for i in range(NUM_CLIENTS):
        thread = threading.Thread(target=client_task, args=(i, results))
        threads.append(thread)
        thread.start()
        time.sleep(0.1) # Delay between client startups

    for thread in threads:
        thread.join()

    total_time = 0
    successful_clients = 0
    for client_id, time_taken in results.items():
        if isinstance(time_taken, float):
            print(f'Client {client_id}: {time_taken:.4f} seconds')
            total_time += time_taken
            successful_clients += 1
        else:
            print(f'Client {client_id} encountered an error: {time_taken}')

    if successful_clients > 0:
        average_time = total_time/successful_clients
        print(f'\nAverage time per client: {average_time:.4f} seconds')