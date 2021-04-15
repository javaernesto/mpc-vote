from threading import Thread
import socket
import json
import sys

from common import *

def send(vote: cvote, client: int, address, ports: tuple, buffer_size=2048):
    '''
    Sends the vote to the two verifiers (players) as two separate svotes (shares) after applying
    the method getShares().

    param vote:    cvote that is to be transmitted as two separate shares
    param client:  id of the client (can be a public key or a certificate)
    param address: address of the players (in our case, localhost)
    param ports:   port of both players (must be a tuple)
    '''

    # Check if cvote is valid

    # Unpacking of shares and ports
    a, b = vote.getShares()
    pAlice, pBob = ports

    # Sending each svote to the players
    socket_send(a, client, address, pAlice)
    socket_send(b, client, address, pBob)
    

def main():
    # Address and ports of players
    address = "localhost"
    ports = (2004, 2005)

    # We send the vote to both players
    n = int(sys.argv[1])
    for i in range(n):
        j = np.random.randint(0, num_choice)
        v = np.zeros(num_choice, dtype=int)
        v[j] = 1
        myVote = cvote(v) 
        send(myVote, i + 1, address, ports)

if __name__ == '__main__':
    main()