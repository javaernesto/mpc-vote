import socket
import pickle
import numpy as np
from multiprocessing import Process, Manager
import math


def not_same(messages):
    x = messages[0]
    for i in range(1, len(messages)):
        if messages[i] != x:
            return True
    return False


def get_message(connection, length, messages, i):
    message = connection.recv(length)
    message = pickle.loads(message)
    messages[i] = message


def listen(charlie, connections, length):
    manager = Manager()
    while True:
        messages = manager.list([0]*len(connections))
        processes = []
        for i in range(len(connections)):
            processes.append(Process(target=get_message, args=(connections[i], length, messages, i,)))
            processes[i].start()
        [processes[i].join() for i in range(len(connections))]

        if not_same(messages):
            print("Received messages do not match!")
            send_to_all(connections, ['Received messages do not match']*len(connections))

        elif messages[0] == "close":
            charlie.close()
            print("Charlie is now closing")
            break
        elif 'triple' == messages[0][0]:
            send_triple(connections, messages[0][1], messages[0][2])

        elif 'eda' == messages[0][0]:
            send_eda(connections, messages[0][1], messages[0][2], messages[0][3], messages[0][4])


def secret_share(x, mod, num_players):
    x = np.array(x)
    shares = []
    for i in range(num_players):
        shares.append(np.random.randint(0, mod, x.shape).tolist())
    shares[0] = ((x - np.sum(shares, 0) + np.array(shares[0])) % mod).tolist()
    return shares


def send_to_all(connections, shares):
    for i in range(len(connections)):
        message = pickle.dumps(shares[i])
        connections[i].send(message)


def prepare(a):
    shares = []
    for i in range(len(a[0])):
        shares.append([a[j][i] for j in range(len(a))])
    return shares


def send_triple(connections, p, shape):
    a = np.random.randint(0, p, shape)
    b = np.random.randint(0, p, shape)
    c = (a*b) % p
    a = secret_share(a, p, len(connections))
    b = secret_share(b, p, len(connections))
    c = secret_share(c, p, len(connections))
    shares = prepare([a, b, c])
    send_to_all(connections, shares)


def convert_to_binary(x, width):
    numbers = np.copy(x)
    length = np.prod(numbers.shape)
    original_shape = tuple(list(numbers.shape) + [width])
    numbers.shape = (1, length)
    numbers = numbers[0]
    array = [[int(b) for b in f'{num:0{width}b}'[::-1]] for num in numbers]
    array = np.array(array)
    array.shape = original_shape
    return array


# ONLY TRIPLE GENERATION FUNCTION IS COMPLETE
def send_eda(connections, size, bits, mod, shape):
    r = np.random.randint(0, size, shape)
    y = convert_to_binary(r, bits)
    r = secret_share(r, mod, len(connections))
    y = secret_share(y, 2, len(connections))
    shares = prepare([r, y])
    send_to_all(connections, shares)


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
