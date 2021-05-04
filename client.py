import socket
import pickle
import numpy as np


def generate_vote(candidates_number):
    index = np.random.randint(0, candidates_number)
    vector = np.zeros(candidates_number)
    vector[index] = 1
    return vector


def secret_share(x, mod, num_players):
    x = np.array(x) % mod
    print(x)
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
        player[j].send(pickle.dumps(message))
        player[j].close()


def main(ips, ports, mod, precision):
    text = open('client.txt', 'w')
    player = connect(ips, ports)
    vote = np.random.uniform(-10, 10, (4, 3, 2))
    print(vote)
    vote = vote*(10**precision) # generate_vote(5)
    vote = np.floor(vote).astype(int)
    text.write(f'{vote} \n')
    vote = secret_share(vote, mod, len(ips))
    send_vote(vote, player)
    print("A client has just voted")
    text.close()
    

