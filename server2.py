import socket
import ssl
import asyncio
import sys
import os
import pickle

from OpenSSL import crypto
from typing import List

import config
import protocol

# Cert and key files for S2
crtfile ='Party_1.crt'
key_file ='Party_1.key'
cafile = 'mpyc_ca.crt'

# Set up addresses and ports
hostname = "Party n 0"
nbVotants = 2
data = 0
pubkeys = []
didvote = []
dico_a = dict()
myShares = {'x': 0, 'y': 0, 'z': 0}

# Create SSL context for communication with C
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(crtfile,keyfile = key_file)
context.load_verify_locations(cafile = cafile)
context.verify_mode = ssl.CERT_REQUIRED

async def handle_client(reader, writer, data1):
	''' Handle incomming messages from client C '''

	global data
	pub_key_dico = ''

	while True :
		pub = writer.get_extra_info('ssl_object')
		der = pub.getpeercert(binary_form=True)
		crtObj = crypto.load_certificate(crypto.FILETYPE_ASN1, der)
		pubKeyObject = crtObj.get_pubkey()
		pubKeyString = crypto.dump_publickey(crypto.FILETYPE_PEM, pubKeyObject)
		if pubKeyString in pubkeys:
			if pubKeyString in didvote:
				print("Already voted")
				break
			else:
				print("Connexion acceptée de", writer.get_extra_info('peername'))
				# print(type(pubKeyString))
				print("Certificat commence par",\
					   pubKeyString.decode().split('\n')[1][:24])
				didvote.append(pubKeyString)
				pub_key_dico = pubKeyString
		else:
			print("Not allowed")
			break
		try:
			data1 = await reader.read(config.SIZE_OF_INT)
			writer.close()
		except asyncio.IncompleteReadError:
			print('Probleme de lecture')
			break
		
		data += pickle.loads(data1)
		dico_a[pub_key_dico] = pickle.loads(data1)
		print("Ma part de c :", pickle.loads(data1))
		myShares['x'] = pickle.loads(data1)
		writer.close()
		break

def compteur_exchange(port: int, context: ssl.SSLSocket, share: int) -> int:
	''' Echange share `share` between parties (S1 & S2) '''

	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM, 0)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	conn = context.wrap_socket(s, server_side=False, server_hostname=hostname)
	conn.connect(('localhost', port))
	protocol.send_int(conn, share)
	msg = protocol.recv_int(conn)
	conn.close()
	s.close()

	return msg
	
def get_public_keys(num_voters: int):
	''' Get public key from client '''

	for j in range(3, num_voters + 2):
		file_path = os.path.join(os.getcwd(), 'Party_{}.crt').format(j - 1)
		f = open(file_path,'r')
		cert = f.read()
		crtObj = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
		pubKeyObject = crtObj.get_pubkey()
		pubKeyString = crypto.dump_publickey(crypto.FILETYPE_PEM,pubKeyObject)
		pubkeys.append(pubKeyString)

async def main():

	print("Serveur 2")
	get_public_keys(nbVotants)

	# Start server and listen for connections
	await asyncio.start_server(lambda r, w : handle_client(r, w, data),\
							   'localhost', config.port_compteur_2_v, ssl=context)
	await asyncio.sleep(7.5)

	# Create SSL for communication with S1
	context_c = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
	context_c.load_cert_chain(crtfile, keyfile=key_file)
	context_c.load_verify_locations(cafile=cafile)
	context_c.verify_mode = ssl.CERT_REQUIRED
	
	# Create secret `z` and share it with S1 and receive share of `y`
	z = 130
	z_1, z_2 = protocol.distribute(z)
	myShares['z'] = z_2
	y_2 = compteur_exchange(config.port_compteur_1_c, context, z_1)	
	myShares['y'] = y_2

	print("Ma part de s1:", y_2)
	# print(myShares)

	b = myShares['x'] + myShares['y'] + myShares['z']
	print("Ma part de c + s1 + s2:", b)

	await asyncio.sleep(5)
	# print("Connexion à l'auditeur A")

	p = protocol.Proto(context, 1)
	p.audit(b)


if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())

