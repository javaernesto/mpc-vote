import numpy as np
import socket
import json

# Define parameters of the election
num_choice = 5
num_voters = 3

# Different choices of prime P for different bit lengths
P_VALUES = { 32: 2147565569, \
             64: 9223372036855103489, \
             128: 170141183460469231731687303715885907969, \
             192: 3138550867693340381917894711603833208051177722232017256453, \
             256: 57896044618658097711785492504343953926634992332820282019728792003956566065153, \
             512: 6703903964971298549787012499102923063739682910296196688861780721860882015036773488400937149083451713845015929093243025426876941405973284973216824503566337 }

P = P_VALUES[32]

# Define the objets used during the election

class cvote(object):
    '''
    Object clear vote consisting in a vector of zeroes with a one in position of vote.
    We can check is vote is valid, blank or null
    '''

    def __init__(self, data, size=num_choice):
        '''
        param data: data of the vote (for example a list or numpy array object) 
        param c:    number of choices, i.e. size of the vector cvote
        '''

        self.data = data
        self.size = size

    def __add__(self, other):
        '''
        Adds two cvotes (modulo P)
        '''

        s = np.zeros(num_choice, dtype=int)
        for i in range(num_choice):
            s[i] = (self.data[i] + other.data[i]) % P

        return cvote(s)

    def __sub__(self, other):
        '''
        Substracts two cvotes (modulo P)
        '''

        s = np.zeros(num_choice, dtype=int)
        for i in range(num_choice):
            s[i] = (self.data[i] - other.data[i]) % P

        return cvote(s)

    def __str__(self):
        '''
        Allows printing data
        '''

        return np.array_str(self.data)
        
    def isBlank(self):
        ''' Checks if the cvote is blank, i.e. all zeros '''

        if not(np.any(self.data)):
            isBlank = True  # Vote blank (all zeros)
        else:
            isBlank = False

        return isBlank

    def isValid(self):
        ''' Checks if the vote is valid, i.e. contains a one and remaining zeros or all zeros (blank) '''

        if self.isBlank():
            isValid = True  # Vote blank (all zeros)
        elif (np.count_nonzero(self.data == 0) == self.size - 1) and (1 in self.data):
            isValid = True # Vote valid (exactly n - 1 zeros and 1 one)
        else:
            isValid = False

        return isValid   

    def getShares(self, players=2, prime=P):
        ''' Gets shares (of type svote) from the clear vote '''

        # We have implemented the vote algorithm, thus players=2. For other type of MPC
        # protocols, we can change that value if we want

        # Assert vote is valid
        assert self.isValid(), "Your vote is not valid, try again."

        # Creation of mask (because players=2)
        mask = np.random.randint(P, size=num_choice)

        # Creation of shares
        aa, b = np.zeros(num_choice, dtype=int), svote(mask)
        for i in range(num_choice):
            aa[i] = (self.data[i] - mask[i]) % P
        a = svote(aa)

        return (a, b)

class svote(object):
    ''' Object secret vote created from clear vote. It inherits properties of cvote but is masked '''

    def __init__(self, data, size=num_choice):
        '''
        param data: masked data of the vote (for example a list or numpy array object) 
        param c:    number of choices, i.e. size of the vector svote
        '''

        self.data = data
        self.size = size

    def __add__(self, other):
        '''
        Adds two svotes (modulo P)
        '''

        s = np.zeros(num_choice, dtype=int)
        for i in range(num_choice):
            s[i] = (self.data[i] + other.data[i]) % P

        return svote(s)

    def __sub__(self, other):
        '''
        Substracts two svotes (modulo P)
        '''

        s = np.zeros(num_choice, dtype=int)
        for i in range(num_choice):
            s[i] = (self.data[i] - other.data[i]) % P

        return svote(s)

    def __str__(self):
        '''
        Allows printing data
        '''

        return np.array_str(self.data)

def socket_send(vote: svote, client: int, address, port: int, buffer_size=2048):
    '''
    Sends one individual message to a server, then closes the connection.
    The message should be of type svote.

    param vote:    svote to be transmitted to one of the players
    param client:  id of the client (can be a public key or a certificate)
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
    
    vote_dict = {"id":   client,
                 "vote": vote.data.tolist()}
    s = json.dumps(vote_dict)
    soc.send(str.encode(s))
    print("Sent a message to " + address + " : " + str(port))

    soc.shutdown(socket.SHUT_RDWR)
    soc.close()

def sum_votes(votes: list):
    '''
    Sums the svotes or cvotes received modulo P

    param votes: a list of dicts, each containing the voter key and his svote
    '''

    total = svote(np.zeros(num_choice, dtype=int))

    for i in range(len(votes)):
        total += svote(np.array(votes[i]['vote']))

    return total

def main():
    myVote = cvote(np.array([1, 0, 0, 0, 0]))
    myOtherVote = cvote(np.array([0, 1, 0, 0 ,0]))

    print("Test cvotes")
    print(myVote)
    print(myVote + myOtherVote)
    print("isValid: ", myVote.isValid())
    print("isBlank: ", myVote.isBlank())

    print("Test svotes")
    a, b = myVote.getShares()
    print(a)
    print(b)

if __name__ == '__main__':
    main()