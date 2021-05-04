import socket
import os
from _thread import start_new_thread
import json

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

	def send(self, data, other):
		'''	Sends data to other player (must be called after starting MPC runtime) '''

		soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		try:
			soc.connect((other.host, other.port))
			print("Player {} send data to player {}.".format(self.pid, other.pid))
		except socket.error as e:
			print(str(e))

		s = json.dumps(data)
		soc.send(str.encode(s))

		soc.shutdown(socket.SHUT_RDWR)
		soc.close()
		
	def recv(self, other, buffer_size=2048):
		''' Receives data from another player '''
		
		conn, addr = self.conn.accept()
		while True:
			bdata = conn.recv(buffer_size)
			if not bdata:
				break
			data = json.loads(bdata)
			print("Player {} received {} from player {}".format(self.pid, data, other.pid))

		conn.close()

	def sumVotes(self):
		''' Sums the votes received by the player '''

		total = np.zeros(num_choice, dtype=int)

		assert len(self.votes)
		for vote in self.votes:
			total = (total + np.array(vote['vote'])) % P

		return total
		
class mpc:
	'''
	MPC class for making interaction between players. In our case, we only use two players 
	(Alice and Bob), and later use Charlie that communicates with Alice and Bob 
	sending them triples, edaBits, ...
	'''

	def __init__(self, players: list):
		'''	Initializes the MPC runtime with number of players '''

		self.players = players

	def addPlayer(self, player: Player):
		'''	Adds a player (pid, host, port) to the MPC runtime '''

		self.players.append(player.info)

	def start(self, timeout=10):
		'''	Starts the MPC runtime '''

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

if __name__ == '__main__':
	Alice = Player(0, '137.194.183.66', 2004, 10)
	Bob = Player(1, '137.194.186.2', 2005, 10)
	
	Runtime = mpc([Alice, Bob])
	Runtime.start()

	Runtime.doElection()
	Runtime.gatherVotes()
	