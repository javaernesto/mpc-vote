import socket
import ssl
import asyncio
import sys
import os
import pickle
import numpy as np

from OpenSSL import crypto
from typing import List

import config
import protocol

# Cert and key files for S2
crtfile ='auditeur.crt'
key_file ='auditeur.key'
cafile = 'mpyc_ca.crt'

# Set up addresses and ports
hostname = "Auditeur"
port = 23213
nbVotants = 1
data = 0
pubkeys = []
didvote = []
dico_a = dict()
myShares = {'x': 0, 'y': 0, 'z': 0}

# Test
count_eda, count_tri = 0, 0

async def handler(reader, writer, context):

	global data

	while True :
		pub = writer.get_extra_info('ssl_object')
		der = pub.getpeercert(binary_form=True)
		crtObj = crypto.load_certificate(crypto.FILETYPE_ASN1, der)
		pubKeyObject = crtObj.get_pubkey()
		pubKeyString = crypto.dump_publickey(crypto.FILETYPE_PEM, pubKeyObject)
		
		if pubKeyString in pubkeys:
			print("Allowed")
			didvote.append(pubKeyString)
		else:
			print("Not allowed")
			break
	
		print("Closing")
		writer.close()
		break


def toBits(x: int):
	''' Return list of bits of `x` '''

	return [int(x) for x in '{:0{size}b}'.format(x, size=config.BIT_NUM)]

def getEda():
	''' Generate edaBits for both players S1 and S2 '''

	# Generate random int in range [0, SIZE_OF_INT) (twice)
	rr = np.random.randint(0, config.SIZE_OF_INT, dtype=int)
	r = protocol.distribute(rr)
	ss = np.random.randint(0, config.SIZE_OF_INT, dtype=int)
	s = protocol.distribute(ss)

	# Split in bits
	bb = toBits(rr)
	b = protocol.distribute(bb, mod=2)

	return (r, b, s)

def getTriple(mod=config.SIZE_OF_INT):
	''' Generate multiplication triple '''

	aa = np.random.randint(0, mod, dtype=int)
	bb = np.random.randint(0, mod, dtype=int)
	cc = aa * bb

	a = protocol.distribute(aa, mod=mod)
	b = protocol.distribute(bb, mod=mod)
	c = protocol.distribute(cc, mod=mod)

	return (a, b, c)

def get_public_keys(num_voters: int):
	''' Get public key from client '''

	for j in range(1, num_voters + 2):
		file_path = os.path.join(os.getcwd(), 'Party_{}.crt').format(j - 1)
		f = open(file_path,'r')
		cert = f.read()
		crtObj = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
		pubKeyObject = crtObj.get_pubkey()
		pubKeyString = crypto.dump_publickey(crypto.FILETYPE_PEM,pubKeyObject)
		pubkeys.append(pubKeyString)

def accept(context: ssl.SSLSocket) -> list:
	''' Accept connections from S1 and S2 '''

	# Empty list that will contain the SSLSockets of both S1 and S2
	Conns = []

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM,0) as sock:
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(('localhost', config.port_audit))
		sock.listen(10)
		ssock = context.wrap_socket(sock, server_side=True)

	for i in {0, 1}:
		conn, addr = ssock.accept()
		print("Connection with", addr)
		Conns.append(conn)

	return Conns

def handle(connections: List[ssl.SSLSocket]) -> None:
	''' 
	Handle connections of both S1 and S2.\\
	Two counters are set for distributing triples and edaBits.
	Each time a counter reaches 2, generate triple or edaBits and send to S1 and
	S2.
	'''

	c_eda, c_tri = 0, 0
	open_compare = 0
	while True:
		try:
			for i in {0, 1}:
				data = protocol.recv_int(connections[i])
				print("dtype", type(data))
				if data == 'eda':
					c_eda += 1
				if data == 'tri':
					c_tri += 1
				if isinstance(data, int):
					print("Received comparison shares")
					open_compare += data
			if (c_eda == 2):
				print("Send edaBits")
				r, bits, rr = getEda()
				for i in {0, 1}:
					protocol.send_int(connections[i], [r[i], bits[i], rr[i]])
				c_eda = 0
			elif (c_tri == 2):
				print("Send triples")
				a, b, c = getTriple()
				for i in {0, 1}:
					protocol.send_int(connections[i], [a[i], b[i], c[i]])
				c_tri = 0
		except KeyboardInterrupt:
			print("\nExiting...")
			for i in {0, 1}:
				connections[i].close()
			break

	print("The sign of {x + y + z} is", open_compare)

async def main():

	# Create SSL context for communication with C
	get_public_keys(nbVotants)
	context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
	context.load_cert_chain(crtfile, keyfile=key_file)
	context.load_verify_locations(cafile = cafile)
	context.verify_mode = ssl.CERT_REQUIRED

	# Start server (no asyncio)
	connections = accept(context)
	handle(connections)
	await asyncio.sleep(0.1)

	# Start server and listen for connections
	# await asyncio.start_server(lambda r, w : handler(r, w, context),\
	# 						   'localhost', port, ssl=context)
	# await asyncio.sleep(50)

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
