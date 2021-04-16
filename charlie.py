import socket
import pickle
import numpy as np


def listen(charlie, connections, length):
    while True:
        message_0 = connections[0].recv(length)
        message_1 = connections[1].recv(length)

        message_0 = pickle.loads(message_0)
        message_1 = pickle.loads(message_1)

        if message_1 != message_0 :
            print("Received messages do not match!")
            error_message = pickle.dumps("Received messages do not match!")
            connections[0].send(error_message)
            connections[1].send(error_message)
        elif message_0 == "close":
            charlie.close()
            print("Charlie is now closing")
            break
        elif 'triple' == message_0[0]:
            send_triple(connections, message_0[1], message_0[2])

        elif 'eda' == message_0[0]:
            send_eda(connections, message_0[1], message_0[2], message_0[3])


def secret_share(x, p):
    x = np.array(x)
    x_a = np.random.randint(0, p, x.shape)
    x_b = (x-x_a) % p
    return x_a.tolist(), x_b.tolist()


def send_triple(connections, p, shape):
    message = []
    a_0 = np.random.randint(0, p, shape)
    b_0 = np.random.randint(0, p, shape)
    a_1 = np.random.randint(0, p, shape)
    b_1 = np.random.randint(0, p, shape)
    c = ((a_0+a_1)*(b_0+b_1)) % p
    c_0 = np.random.randint(0, p, shape)
    c_1 = (c - c_0) % p
    message.append(pickle.dumps([a_0.tolist(), b_0.tolist(), c_0.tolist()]))
    message.append(pickle.dumps([a_1.tolist(), b_1.tolist(), c_1.tolist()]))
    for i in range(len(connections)):
        connections[i].send(message[i])


def convert_to_binary(numbers, width):
    return [[int(b) for b in f'{num:0{width}b}'[::-1]] for num in numbers]


# ONLY TRIPLE GENERATION FUNCTION IS COMPLETE
def send_eda(connections, size, k, shape):
    r = np.random.randint(0, 2**size, shape)
    r_a = np.random.randint(0, 2**k, shape)
    r_b = (r - r_a) % 2**k
    y = convert_to_binary(r, k)
    y_a, y_b = secret_share(y, 2)
    message_0 = pickle.dumps([r_a, y_a])
    connections[0].send(message_0)
    message_1 = pickle.dumps([r_b, y_b])
    connections[1].send(message_1)


def create_server(ip, port):
    server = socket.socket()
    server.bind((ip, port))
    return server


def accept_connections(server, num_players):
    server.listen()
    connections = []
    for i in range(num_players):
        conn, address = server.accept()
        connections.append(conn)
    return connections


def main(length, ip_charlie, port_charlie, num_players):
    ip_charlie, port_charlie = ip_charlie[0], port_charlie[0]
    charlie = create_server(ip_charlie, port_charlie)
    print("Charlie is online")
    connections = accept_connections(charlie, num_players)
    print("Charlie has accepted the connections")
    listen(charlie, connections, length)

