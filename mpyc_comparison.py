import sys
import socket
import json
import numpy as np
import time
from threading import Thread
from typing import Any

m = int(sys.argv[1])
num_choice = 5
num_voters = 10
P = 2147565569

def distribute(a: list) -> list:

	shares = [0] * m
	if isinstance(a, int):
		a = [a]

	for i in range(1, m):
		s = np.random.randint(P, size=len(a))
		shares[i] = s

	s = np.zeros(len(a), dtype=int)
	for p in shares[1:]:
		s = (p + s) % P
	shares[0] = (a - s) % P
	
	return shares

def reconstruct(a: list):

	s = 0
	for p in a:
		s = (s + p) % P
		
	return s

def socket_send(vote: dict, address: str, port: int, buffer_size=2048):
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
	
	if isinstance(vote, str):
		s = json.dumps(vote)
	else:	
		vote_dict = {'id': 'vote', 'val': vote.tolist()}
		s = json.dumps(vote_dict)

	soc.send(str.encode(s))
	print("Sent a message to " + address + " : " + str(port))

	# soc.shutdown(socket.SHUT_RDWR)
	soc.close()

def listen_thread(conn: socket.socket, data: list, buffer_size=2048):

	mess = conn.recv(buffer_size)
	if not mess:
		time.sleep(0.1)
	else:
		mess = json.loads(mess)
		data.append(mess)

def check_integrity(data: list) -> bool:

	return all(el == data[0] for el in data)

def getTriples(size=num_choice):
		''' Creates multiplication triple '''

		aa = np.random.randint(0, P, size=size)
		bb = np.random.randint(0, P, size=size)
		cc = (aa * bb) % P
		a = distribute(aa)
		b = distribute(bb)
		c = distribute(cc)
		
		return a, b, c

class MessageExchanger:

	def __init__(self, peer_id: int, addr: tuple):
		# Setting up the players
		self.soc = soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# We set a time of 10 seconds for the election
		# ServerSideSocket.settimeout(10.0)

		try:
			soc.bind(addr)
		except socket.error as e:
			print(str(e))

		print('Player {} is ready'.format(peer_id))
		soc.listen(5)

		while True:
			soc.accept()

class Player:

	def __init__(self, pid: int, addr: tuple):
		self.pid = pid
		self.addr = addr
		self.protocol = None
		self.buf = []

class Runtime:

	def __init__(self, id: int, players: list):
		self.id = id
		self.players = players
		self.M = len(players)
		self.prov = Player(id, ('localhost', 2000))

	def start(self):

		def start_provider():
			# Setting up the provider
			ServerSideSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			ServerSideSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			# We set a time of 10 seconds for the election
			# ServerSideSocket.settimeout(10.0)

			try:
				ServerSideSocket.bind(self.prov.addr)
			except socket.error as e:
				print(str(e))

			print('MPC provider is ready')
			ServerSideSocket.listen(5)

			data = []
			while True:
				conn, addr = ServerSideSocket.accept()
				threads = []
				for i in range(m):
					listen_thread(conn, data)
				# 	t = Thread(target=listen_thread, args=(conn, data))
				# 	threads.append(t)
				# 	t.start()
				# for t in threads:
				# 	t.join()

				if len(data) == m:
					assert check_integrity(data), "Received messages do not match!"

					if data[0] == 'triple':
						print("Sending triples")
						a, b, c = getTriples()
						for i in range(m):
							t_dict = {'id': 'triple', 'a': a[i].tolist(), 'b': b[i].tolist(), 'c': c[i].tolist()}
							self.bcast(t_dict, self.players[i])

				print(data)
				conn.close()


		def start_player(p: Player):
			# Setting up the players
			PlayerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			PlayerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			# We set a time of 10 seconds for the election
			# ServerSideSocket.settimeout(10.0)

			try:
				PlayerSocket.bind(p.addr)
			except socket.error as e:
				print(str(e))

			print('Player {} is ready'.format(p.pid))
			p.protocol = PlayerSocket
			PlayerSocket.listen(5)

			while True:
				conn, addr = PlayerSocket.accept()
				data = conn.recv(2048)
				data = json.loads(data)
				if not data:
					pass
				if data['id'] == 'triple':
					a, b, c = data['a'], data['b'], data['c']
					a, b, c = np.array(a), np.array(b), np.array(c)
					p.buf.extend((a, b, c))
				if data['var']:
					self.buf[-1]['var'] = (self.buf[-1]['var'] + data['var']) % P	

		Threads = []

		prov = Thread(target=start_provider)
		prov.start()

		for p in self.players:
			t = Thread(target=start_player, args=(p, ))
			Threads.append(t)

		for t in Threads:
			t.start()

		return prov, Threads

	def bcast(self, mess: dict, receivers=None):

		if receivers:
			to_send = [receivers] if not isinstance(receivers, list) else receivers
		else:
			to_send = list(set().union(self.players, [self.prov]))

		for p in to_send:

			soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			try:
				soc.connect(p.addr)
				print("Connected to player {}".format(p.pid))
			except socket.error as e:
				print(str(e))
			
			mess = json.dumps(mess)
			soc.send(str.encode(mess))
			# print("Sent a message to " + address + " : " + str(port))

			soc.close()

	def gather(self, obj: str):
		for p in self.players:
			self.bcast(self.p.buf[-1][obj])


	def mul(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:

		for p in self.players:
			self.bcast('triple', self.prov)
		time.sleep(0.5)
		for p in self.players:
			a, b, c = p.buf[-1]
	
def send(vote: dict, address: str, ports: tuple, buffer_size=2048):
	'''
	Sends the vote to the two verifiers (players) as two separate svotes (shares) after applying
	the method getShares().

	param vote:    cvote that is to be transmitted as two separate shares\\
	param client:  id of the client (can be a public key or a certificate)\\
	param address: address of the players (in our case, localhost)\\
	param ports:   port of both players (must be a tuple)
	'''
	
	# Unpacking of shares and ports
	a, b = distribute(vote)
	pAlice, pBob = ports

	# Sending each svote to the players
	socket_send(a, address, pAlice)
	socket_send(b, address, pBob)

def send_votes():
	# Address and ports of players
	address = "localhost"
	ports = (2001, 2002)

	# For now, we choose randomly the voter's choice
	for i in range(num_voters):
		j = np.random.randint(0, num_choice)
		v = np.zeros(num_choice, dtype=int)
		v[j] = 1
		send(v, address, ports)

if __name__ == '__main__':

	Players = [Player(1, ('localhost', 2001)), Player(2, ('localhost', 2002))]

	# mpc = Runtime(0, Players)

	# mpc.start()
	# time.sleep(0.5)

	# send_votes()

	# a = np.array([1, 0])
	# b = np.array([1, 1])

	# mpc.mul(a, b)

	socket_send('[1, 0, 1, 0, 1]', 'localhost', 8888)

	a = [1, 2]
	s = distribute(a)
	ss = reconstruct(s)