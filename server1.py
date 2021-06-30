import socket
import ssl
import asyncio
import pickle
import sys
import os

from OpenSSL import crypto

import config
import protocol

# Cert and key files for S1
crtfile = 'Party_0.crt'
key_file = 'Party_0.key'
nbVotants = 2
cafile = 'mpyc_ca.crt'

# Initialize data and lists for storing shares
data = 0
vote = []
pubkeys = []
didvote = []
dico_a = {}
myShares = {'x': 0, 'y': 0, 'z': 0}

# Create SSL context for communication with C
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(crtfile, keyfile=key_file)
context.load_verify_locations(cafile=cafile)
context.verify_mode = ssl.CERT_REQUIRED

async def handle_client(reader, writer):
	''' Handle incomming messages from client C '''

	data = ''
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
			data = await reader.read(config.SIZE_OF_INT)
			# print(pickle.loads(data))
			writer.close()
		except asyncio.IncompleteReadError:
			print('Problème de lecture')
			break
		dico_a[pub_key_dico] = pickle.loads(data)
		print("Ma part de c :", pickle.loads(data))
		myShares['x'] = pickle.loads(data)
		break

def compteur_exchange(port: int, context: ssl.SSLSocket, share: int):
	''' Echange share `share` between parties (S1 & S2) '''

	# Setting SSL Socket
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM,0) as sock:
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(('localhost', port))
		sock.listen(10)
		with context.wrap_socket(sock, server_side=True) as ssock:
			conn, addr = ssock.accept()

	# Retrieving certificate public key
	file_path = os.path.join(os.getcwd(), 'Party_0.crt')
	f = open(file_path, 'r')
	cert = f.read()
	crtObj = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
	pubKeyObject = crtObj.get_pubkey()
	pubKeyString = crypto.dump_publickey(crypto.FILETYPE_PEM,pubKeyObject)
	print("Connexion acceptée de", addr)
	# On affiche les 24 premiers caractères du certificat
	print("Certificat commence par",\
		  pubKeyString.decode().split('\n')[1][:24])
	
	# S1 is server and S2 is client (when exchanging only btw S1 & S2)
	msg = protocol.recv_int(conn)
	protocol.send_int(conn, share)
	conn.close()
	sock.close()

	return msg

def get_public_keys(num_voters: int):
	''' Get public key for C '''
	
	for j in range(1, num_voters + 2):
		file_path = os.path.join(os.getcwd(), 'Party_{}.crt').format(j - 1)
		f = open(file_path, 'r')
		cert = f.read()
		crtObj = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
		pubKeyObject = crtObj.get_pubkey()
		pubKeyString = crypto.dump_publickey(crypto.FILETYPE_PEM, pubKeyObject)
		pubkeys.append(pubKeyString)

async def main():

	print("Serveur 1")
	get_public_keys(nbVotants)
	
	# Start server and listen for connections
	await asyncio.start_server(lambda r, w : handle_client(r, w), 'localhost',\
							   config.port_compteur_1_v, ssl=context)
	await asyncio.sleep(7.5)

	# Create secret `y` and share it with S2 and receive share of `z`
	y = -100
	y_1, y_2 = protocol.distribute(y)
	myShares['y'] = y_1
	z_1 = compteur_exchange(config.port_compteur_1_c, context, y_2)
	myShares['z'] = z_1

	print("Ma part de s2 :", z_1)
	# print(myShares)

	b = myShares['x'] + myShares['y'] + myShares['z']
	print("Ma part de c + s1 + s2 :", b)

	await asyncio.sleep(5)

	p = protocol.Proto(context, 0)
	p.audit(b)

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())

