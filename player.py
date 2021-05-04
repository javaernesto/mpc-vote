import socket
import pickle
import common
import numpy as np
import time


def create_server_identity(identity, ip, port):
    server = socket.socket()
    server.bind((ip[identity], port[identity]))
    return server


def get_votes(x, length, server, t):
    server.listen()
    t0 = time.time()
    while time.time() - t0 < t:
        try:
            server.settimeout(1)
            conn, address = server.accept()
            pickled_message = conn.recv(length)
            x.append(pickle.loads(pickled_message))
            conn.close()
        except:
            continue


def connect_before(player, identity, ips, ports, text):
    for i in range(identity):
        player[i] = socket.socket()
        player[i].connect((ips[i], ports[i]))
        text.write(f'{identity} : Player {identity} is now connected to player {i} \n')


def connect_after(player, identity, ips):
    for i in range(identity + 1, len(ips)):
        conn, address = player[identity].accept()
        player[i] = conn


def connect_to_charlie(ip, port):
    server = socket.socket()
    server.connect((ip, port))
    return server


def evaluate(identity, charlie, player, length, mod, precision, x):
    other_players = player[:identity]+player[identity+1:]
    function = common.Function(identity, charlie, other_players, length, mod, precision)
    y = function.function(x)
    return y


def main(identity, length, ip_charlie, port_charlie, ips, ports, mod, precision):
    ip_charlie, port_charlie = ip_charlie[0], port_charlie[0]
    text = open('players.txt', 'a')
    text.write('\n'*identity)

    player = [0] * len(ips)
    player[identity] = create_server_identity(identity, ips, ports)
    print(f'{identity} is online')
    x = []
    get_votes(x, length, player[identity], 3)
    print(f'{identity} has closed the voting')
    player[identity].setblocking(True)
    x = np.array(x)
    text.write(f'{identity} : {x} \n')
    
    connect_before(player, identity, ips, ports, text)
    connect_after(player, identity, ips)

    charlie = connect_to_charlie(ip_charlie, port_charlie)
    text.write(f'{identity} : Player {identity} is now connected to Charlie \n')
    print(f'{identity} is now connected to charlie')

    print(f'{identity} is now evaluating the MPC protocol')
    y = evaluate(identity, charlie, player, length, mod, precision, x)
    if identity == 0:
        print(y)

    text.write(f'{identity} : {y} \n')
    text.close()
    player[identity].close()
    print(f'{identity}s server is now closed')
