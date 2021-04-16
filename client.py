import socket
import pickle
import numpy as np


def generate_vote(candidates_number):
    index = np.random.randint(0, candidates_number)
    vector = np.zeros(candidates_number)
    vector[index] = 1
    return vector


def share(x, mod):
    x_0 = np.random.randint(0, mod, x.shape)
    x_1 = (x-x_0) % mod
    return x_0.tolist(), x_1.tolist()


def connect(ips, ports):
    player = []
    for j in range(len(ips)):
        player.append(socket.socket())
        player[j].connect((ips[j], ports[j]))
    return player


def send_vote(vote, player):
    for j in range(len(player)):
        player[j].send(pickle.dumps(vote[j]))
        player[j].close()


def main(ips, ports):
    text = open('client.txt', 'w')
    for i in range(5):
        player = connect(ips, ports)
        vote = np.random.randint(0, 10, 5)  # generate_vote(5)
        text.write(f'{vote.tolist()} \n')
        vote = share(vote, 100000)
        send_vote(vote, player)
        print("A client has just voted")
    text.close()

