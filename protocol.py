import socket
import pickle
import ssl
import numpy as np

from typing import Union

import config

class Proto:
	'''
	Class for MPC protocol. Each player creates an instance of this class in his
	file, and can then use MPC protocols on his shares. Communication between
	players and audit are set in __init__ method
	'''

	def __init__(self, context, id: int):
		''' 
		Connect to other server (S1 or S2). 
		If Player is S0, he will be the server between S0 and S1 (for outputing
		shares, basically). 
		If Player is S1, he will connect to the connection created by S0
		'''

		# Each player has an id for determinig who will be server and who will
		# be the client
		self.id = id

		if (id == 0):
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM,0) as sock:
				sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				# sock.setblocking(False)
				sock.bind(('localhost', config.port_compteur_1_c))
				sock.listen(10)
				with context.wrap_socket(sock, server_side=True) as ssock:
					conn, _ = ssock.accept()
			self.conn = conn
			print("Connected to S2")
		elif (id == 1):
			s = socket.socket(socket.AF_INET,socket.SOCK_STREAM, 0)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			# s.setblocking(False)
			conn = context.wrap_socket(s, server_side=False,\
									server_hostname=config.hostname)
			conn.connect(('localhost', config.port_compteur_1_c))
			self.conn = conn
			print("Connected to S1")

		# Conect to audit
		ss = socket.socket(socket.AF_INET,socket.SOCK_STREAM, 0)
		ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		ss.setblocking(True)
		aud = context.wrap_socket(ss, server_side=False)
		aud.connect(('localhost', config.port_audit))
		self.aud = aud
		print("Connected to A")

	def output(self, share: int) -> int:
		''' Output value of share. Exchanges shares and return open value '''

		if (self.id == 0):
			msg = recv_int(self.conn)
			print("Recv share")
			send_int(self.conn, share)
			print("Output of share")
		elif (self.id == 1):
			send_int(self.conn, share)
			print("Sent share")
			msg = recv_int(self.conn)
			print("Output of share")

		return msg + share		

	def reqEda(self) -> tuple:
		''' 
		Request edaBits to Audit
		:returns triple (r, bits, rr), 
				 r, rr:  random in [0, SIZE_OF_INT)
				 bits: bit decomposition of r
				 
		'''

		send_int(self.aud, 'eda')
		r, b, rr = recv_int(self.aud)
		# print(type(r), r)
		# print(type(b), b)
		# print(type(rr), rr)

		return (r, b, rr)

	def mul(self, x: int, y:int, mod=config.SIZE_OF_INT) -> int:
		''' 
		MPC multiplication of shares `x` and `y` 
		(see protocol in https://eprint.iacr.org/2012/642.pdf, paragraph 2)
		:returns share z = x * y
		'''
		send_int(self.aud, "tri")
		# print("Req triple")
		a, b, c = recv_int(self.aud)
		# print("Received triple", a, b, c)

		d_1 = (x - a) % mod
		e_1 = (y - b) % mod
		d = self.output(d_1)
		e = self.output(e_1)
		z = (c + d * b + e * a + e * d) % mod

		return z
	
	def Mod2m(self, a: int, m: int, k=config.BIT_NUM) -> int:
		''' 
		Computes `a mod 2^m`.
		(see https://core.ac.uk/download/pdf/187535829.pdf, Protocol 3.2)
		:returns a share of the result `a mod 2^m`
		'''

		r, b, rr = self.reqEda()

		c_1 = (1 << (k - 1)) + a + (rr >> m) + r
		c = self.output(c_1)
		cc = c % (1 << m)
		u = self.LTBits(cc, b)
		aa = cc - r + (u >> m)

		return aa

	def Trunc(self, a: int, m: int, k=config.BIT_NUM) -> int:
		'''
		Truncates `m` bits of the share `a`
		(see https://core.ac.uk/download/pdf/187535829.pdf, Protocol 3.3)
		:returns share [d] = Trunc([a], m)
		'''

		aa = self.Mod2m(a, m, k=k)
		d = (a - aa) >> m

		return d

	def LTZ(self, a: int) -> int:
		'''
		Returns share of (a < 0)
		(see https://core.ac.uk/download/pdf/187535829.pdf, Protocol 3.6)
		:returs [a < 0] ? 1 : 0
		'''

		c = self.Trunc(a, config.BIT_NUM - 1)

		return c

	def PrefixOR(self, x: int, y: int) -> int:
		'''
		MPC OR gate
		:returns share [z] = [x] | [y]
		'''

		z = (x + y) % 2
		m = self.mul(x, y, mod=2) 

		return (z + m) % 2

	def LTBits(self, R: int, x: list) -> tuple:
		''' 
		Protocol for comparison between a secret input shared bitwise and a 
		public value (see https://eprint.iacr.org/2021/119 Fig. 3 for details)
		'''

		m = len(x)
		y, w = [0] * m, [0] * m
		z = [0] * (m + 1)

		# Range from m - 1 to 0
		i = m - 1
		while i >= 0:
			y[i] = x[i] ^ (R >> i & 1)
			print("Step ", i)
			z[i] = self.PrefixOR(y[i], z[i+1])
			w[i] = z[i] - z[i+1]
			i -= 1

		b = sum([(R >> i & 1) * w[i] for i in range(m)])
		
		return 1 - b

	def audit(self, share: int) -> None:
		''' Handle all communication with audit (for comparison protocols) '''

		# protocol.send_int(p.aud, 'tri')
		# a = protocol.recv_int(p.aud)
		# print('tri', type(a), a)
		# a = protocol.recv_int(p.aud)
		# print('tri', type(a), a)
		# a = protocol.recv_int(p.aud)
		# print('tri', type(a), a)
		# p.reqEda()
		# print("Mul")
		# z = p.mul(3, 5)
		# print(z)
		c = self.LTZ(share)
		print(c)
		send_int(self.aud, c)
		# b = p.PrefixOR(0, 1)
		# print(b)

def send_int(s: socket.socket, x: int):
	''' Send int `x``through socket `s` '''

	data = pickle.dumps(x)
	s.send(data)

def recv_int(s: socket.socket):
	''' Receive int through socket `s` '''

	# Listen for incomming data
	while True:
		data = s.recv(config.SIZE_OF_INT)
		if not data:
			break
	
		msg = pickle.loads(data)
		if isinstance(msg, list):
			msg = np.array(msg)

		return msg

def generer_x() -> int:
	''' Generate random secret in [-SIZE_OF_INT, SIZE_OF_INT) '''

	return (np.random.randint(0, config.SIZE_OF_INT << 1, dtype=int))

def distribute(x: Union[int, np.ndarray], mod=config.SIZE_OF_INT) -> tuple:
	''' Create two shares of secret int `x` (modulo `mod`)'''

	mask = None

	if isinstance(x, int):
		mask = np.random.randint(0, mod, dtype=int)
	
	if isinstance(x, list):
		x = np.array(x)
	
	if isinstance(x, np.ndarray) or isinstance(x, list):
		n = len(x)
		mask = np.random.randint(0, mod, dtype=int, size=n)

	return ((x - mask) % mod, mask)

