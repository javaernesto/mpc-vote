import numpy as np
import socket
import json

# Define parameters of the election
num_choice = 5

# Different choices of prime P for different bit lengths
P_VALUES = { 32:  2147565569, \
			 64:  9223372036855103489, \
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

	def __init__(self, data, id=None, size=num_choice):
		'''
		param id;   id of the person issuing the vote (can be a cert key, a public key, ...)\\
		param data: data of the vote (for example a list or numpy array object)\\
		param c:    number of choices, i.e. size of the vector cvote
		'''

		self.data = data
		self.id = id
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
		aa, b = np.zeros(num_choice, dtype=int), svote(mask, self.id)
		for i in range(num_choice):
			aa[i] = (self.data[i] - mask[i]) % P
		a = svote(aa, self.id)

		return (a, b)

	def todict(self):
		''' Converts cvote to dict type (readable by JSON, therefore numpy array is casted to list)'''

		vote_dict = {'id': self.id, 'vote': self.data.tolist()}

		return vote_dict

class svote(cvote):
	''' 
	Object secret vote created from clear vote. It inherits properties of cvote but is masked.
	For now it only inherits the properties of cvote, but we eventually add properties only for svote.
	'''

def socket_send(vote: svote, address: str, port: int, buffer_size=2048):
	'''
	Sends one individual message to a server, then closes the connection.
	The message should be of type svote.

	param vote:    svote to be transmitted to one of the players\\
	param client:  id of the client (can be a public key or a certificate)\\
	param address: address of the player (in our case, localhost)\\
	param port:    port of one of the players
	'''

	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		soc.connect((address, port))
		print("Connected to server.")
	except socket.error as e:
		print(str(e))
	
	vote_dict = vote.todict()
	s = json.dumps(vote_dict)
	soc.send(str.encode(s))
	print("Sent a message to " + address + " : " + str(port))

	soc.shutdown(socket.SHUT_RDWR)
	soc.close()

def sum_votes(votes: list, id=None):
	'''
	Sums the svotes or cvotes received modulo P

	param votes: a list of dicts, each containing the voter key and his svote
	'''

	total = np.zeros(num_choice, dtype=int)

	for i in range(len(votes)):
		for j in range(num_choice):
			total[j] = (total[j] + np.array(votes[i]['vote'])[j]) % P

	return svote(total, id)

def check_voters(a: list, b: list):
	''' 
	Checks if the two lists of votes have the same voters id. Returns the intersection of a and b.

	param a: a list of svotes (as dicts)
	param b: a list of svotes (as dicts)
	'''

	# We make a copy of a and b
	aa = a[:]
	bb = b[:]

	# We extract the id of each voter (a_ids and b_ids of type 'set')
	a_ids = {x['id'] for x in a}
	b_ids = {y['id'] for y in b}

	# Compute the intersection of the ids
	i_ids = a_ids & b_ids

	# We iterate the lists and remove the votes that are not in the intersection
	for x in aa:
		if x['id'] not in i_ids:
			aa.remove(x)
	for y in bb:
		if y['id'] not in i_ids:
			bb.remove(y)
	
	return (aa, bb)

class Party:
	''' Information about a party in the MPC protocol. '''

	__slots__ = 'pid', 'host', 'port'

	def __init__(self, pid, host=None, port=None):
		''' Initialize a party '''
		self.pid = pid
		self.host = host
		self.port = port

	def __repr__(self):
		''' String representation of the party. '''
		if self.host is None:
			return f'<Party {self.pid}>'

		return f'<Party {self.pid}: {self.host}:{self.port}>'

# Testing
# if __name__ == "__main__":
