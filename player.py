import socket
import pickle
import common
import numpy as np
import time


def create_server_identity(identity, ip, port):
    server = socket.socket()
    server.bind((ip[identity], port[identity]))
    return server


def get_votes(votes, length, server, t):
    server.listen()
    t0 = time.time()

    while time.time() - t0 < t:
        try:
            server.settimeout(1)
            conn, address = server.accept()
            pickled_message = conn.recv(length)
            votes.append(pickle.loads(pickled_message))
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


def evaluate(identity, charlie, player, length, votes):
    function = common.Function(identity, charlie, player[(identity + 1) % 2], length)
    votes = function.function(votes, 100000)
    votes = function.reconstruct(votes, 100000)
    return votes


def main(identity, length, ip_charlie, port_charlie, ips, ports):
    ip_charlie, port_charlie = ip_charlie[0], port_charlie[0]
    text = open('players.txt', 'a')
    text.write('\n'*identity)

    player = [0] * len(ips)
    player[identity] = create_server_identity(identity, ips, ports)
    print(f'{identity} is online')
    votes = []
    get_votes(votes, length, player[identity], 3)
    print(f'{identity} has closed the voting')
    player[identity].setblocking(True)
    votes = np.array(votes)
    text.write(f'{identity} : {votes} \n')
    
    connect_before(player, identity, ips, ports, text)
    connect_after(player, identity, ips)

    charlie = connect_to_charlie(ip_charlie, port_charlie)
    text.write(f'{identity} : Player {identity} is now connected to Charlie \n')
    print(f'{identity} is now connected to charlie')

    votes = evaluate(identity, charlie, player, length, votes)
    print(f'{identity} is now evaluating the MPC protocol')
    text.write(f'{identity} : {votes} \n')
    text.close()
    player[identity].close()
    print(f'{identity}s server is now closed')

