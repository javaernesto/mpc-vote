import socket
from _thread import start_new_thread
import json
import numpy as np

from common import *

def receiveVote(connection, votes, buffer_size=2048):
	''' Receives votes from connection and appends to 'votes' '''

	while True:
		data = connection.recv(buffer_size)
		if not data:
			break
		vote = json.loads(data)
		votes.append(vote)
		# votes.append(vote)

		print("I have received: ", vote)
	connection.close()

class Player:
	'''
	Player class for each MPC player. Initialized with a player id (pid), an address and a port.
	A player can send a message to another player or to every other player.
	'''

	def __init__(self, pid: int, host: str, port: int, timeout=None):
		'''	Initializes an MPC player '''

		self.pid  = pid
		self.host = host
		self.port = port
		self.info = {'pid': pid, 'host': host, 'port': port}
		self.votes = []

		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.conn.settimeout(timeout)

	def __str__(self):
		'''	Allows printing player info	'''

		return str(self.info)

	def sumVotes(self):
		''' Sums the votes received by the player '''

		total = np.zeros(num_choice, dtype=int)

		assert len(self.votes)
		for vote in self.votes:
			total = (total + np.array(vote['vote'])) % P

		return total
		
class Runtime:
	'''
	MPC class for making interaction between players. In our case, we only use two players 
	(Alice and Bob), and later use Charlie that communicates with Alice and Bob 
	sending them triples, edaBits, ...
	'''

	def __init__(self, players: list):
		'''	Initializes the MPC runtime with number of players '''

		self.players = players
		self.provider = Player(0,'localhost', 2000)

	def addPlayer(self, player: Player):
		'''	Adds a player (pid, host, port) to the MPC runtime '''

		self.players.append(player)

	def start(self, timeout=10):
		'''	Starts the MPC runtime '''

		# Start provider
		try:
			self.provider.conn.bind((provider.host, provider.port))
		except socket.error as e:
			print(str(e))

		print("Provider is connected...")
		self.provider.conn.listen()

		# Start players
		for player in self.players:

			try:
				player.conn.bind((player.host, player.port))
			except socket.error as e:
				print(str(e))

			print("Player {} is connected...".format(player.pid))
			player.conn.listen()
	
	def doElection(self):
		'''
		Does the election (without MPC). Each player receives a share of each client's vote.
		The client connections are managed with threads. When timeout is reached, the voting
		stops.
		'''

		for player in self.players:
			ThreadCount = 0
			while True:
				try: 
					client, address = player.conn.accept()
					print('Player {} connected to: '.format(player.pid) + address[0] + ':' + str(address[1]))
					start_new_thread(receiveVote, (client, player.votes))
					ThreadCount += 1
					print('Voter Number: ' + str(ThreadCount))
				except socket.timeout:
					print("len", len(player.votes))
					break
		print("The vote is over")

	def gatherVotes(self):
		''' Once the election is over, gather the votes '''
		
		total = np.zeros(num_choice, dtype=int)

		for player in self.players:
			print(player.sumVotes())
			total = (total + player.sumVotes()) % P

		print("Election results: ", total)
		return total

	def send(self, data, player):
		'''	Sends data to other player (must be called after starting MPC runtime) '''

		soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		try:
			soc.connect((player.host, player.port))
			print("Player {} send data to player {}.".format(self.pid, other.pid))
		except socket.error as e:
			print(str(e))

		s = json.dumps(data)
		soc.send(str.encode(s))

		soc.shutdown(socket.SHUT_RDWR)
		soc.close()
		
	def recv(self, player, buffer_size=2048):
		''' Receives data from another player '''
		
		conn, addr = player.conn.accept()
		while True:
			bdata = conn.recv(buffer_size)
			if not bdata:
				break
			data = json.loads(bdata)
			print("Player {} received {} from player {}".format(player.pid, data, other.pid))

		conn.close()
		return data

	def add(self, a: int, b: int, isConst=False):
		''' Secure addition of a and b '''

		if isConst:
			if player.pid == 1:
				return (a + b) % P
			return a % P
		else:	
			return (a + b) % P

	def sub(self, a: int, b: int, isConst=False):
		''' Secure addition of a and b '''

		if isConst:
			if player.pid == 1:
				return (a - b) % P
			return a % P
		else:	
			return (a - b) % P

	def getShares(self, x, size=num_choice):
		''' Creates shares for MPC players '''

		if type(x) != np.ndarray:
			x = np.array(x)

		shares = []
		for _ in range(len(self.players)):
			shares.append(np.random.randint(0, P, size=size))
		shares[0] = (x - np.sum(shares, 0) + shares[0]) % P

		return shares

	def getTriples(self, ize=num_choice):
		''' Creates multiplication triple '''

		aa = np.random.randint(0, P, size)
		bb = np.random.randint(0, P, size)
		cc = (a * b) % P
		a = self.getShares(aa)
		b = self.getShares(bb)
		c = self.getShares(cc)
		
		return a, b, c


	def mul(self, a: int, b: int):
		''' Secure multiplication of a and b '''

		aa, bb, cc = self.getTriples()

if __name__ == '__main__':
	Alice = Player(0, 'localhost', 2004, 10)
	Bob = Player(1, 'localhost', 2005, 10)
	
	mpc = Runtime([Alice, Bob])
	mpc.start()

	mpc.doElection()
	mpc.gatherVotes()
	