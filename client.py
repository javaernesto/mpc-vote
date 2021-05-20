import socket
import json
import numpy as np


def generate_vote(candidates_number):
    index = np.random.randint(0, candidates_number)
    vector = np.zeros(candidates_number)
    vector[index] = 1
    return vector


def secret_share(x, mod, num_players):
    shares = []
    for i in range(num_players):
        shares.append(np.random.randint(0, mod, x.shape).tolist())
    shares[0] = ((x - np.sum(shares, 0) + np.array(shares[0])) % mod).tolist()
    return shares


def connect(ips, ports):
    player = []
    for j in range(len(ips)):
        player.append(socket.socket())
        player[j].connect((ips[j], ports[j]))
    return player


def send_vote(vote, player):
    for j in range(len(player)):
        message = vote[j]
        message = json.dumps(message)
        player[j].sendall(bytes(message, encoding="utf-8"))
        player[j].close()


def main(ips, ports, mod, precision, numbers_size):
    text = open('client.txt', 'w')
    player = connect(ips, ports)
    vote = np.array([[1.25, 0.5, 2, -3.5], [-2.5, 5, -2, -0.75]])
    vote = np.floor(vote * 2**precision).astype(int)
    print(mod)
    #print('\n x', vote)
    #print('x^3', vote**3)
    text.write(f'{vote} \n')
    vote = secret_share(vote, mod, len(ips))
    send_vote(vote, player)
    print("A client has just voted")
    text.close()