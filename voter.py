from threading import Thread
import socket
import json
import sys

from common import *

# Define list of threads for voters
voters = []

def socket_send(vote: svote, address, port, buffer_size=2048):
    '''
    Sends one individual message to a server, then closes the connection.
    The message should be of type svote.

    param vote:    svote to be transmitted to one of the players
    param address: address of the player (in our case, localhost)
    param ports:   port of one of the players
    '''

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        soc.connect((address, port))
        print("Connected to server.")
    except socket.error as e:
        print(str(e))

    while True:
        b = {"00001": vote.data.tolist()}
        s = json.dumps(b)
        soc.send(str.encode(s))
        print("Voter sent a message to " + address + " : " + str(port))

        
        resp = soc.recv(buffer_size)
        if not resp:
            print("No data")
            break
        
        print("Received data from the client: {}".format(resp.decode('utf-8')))
        break

    soc.shutdown(socket.SHUT_RDWR)
    soc.close()
    print("Socket is closed.")

def send(vote: cvote, address, ports: tuple, buffer_size=2048):
    '''
    Sends the vote to the two verifiers (players) as two separate svotes (shares) after applying
    the method getShares().

    param vote:    cvote that is to be transmitted as two separate shares
    param address: address of the players (in our case, localhost)
    param ports:   port of both players (must be a tuple)
    '''

    # Unpacking of shares and ports
    a, b = vote.getShares()
    pAlice, pBob = ports

    # Sending each svote to the players
    socket_send(a, address, pAlice)
    socket_send(b, address, pBob)
    

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
        send(myVote, address, ports)
    

if __name__ == '__main__':
    main()