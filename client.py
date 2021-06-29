import socket
import ssl
import os
import time
import os.path
import pickle
import numpy as np

from threading import Thread

import config
import protocol

# Cert and key files for C (client)
crtfile = 'Party_2.crt'
key_file = 'Party_2.key'
cafile = 'mpyc_ca.crt'

# Set up ports
port = 11662
host = 'localhost'
hostname_c1 = "MPyC party 0"
hostname_c2 = "MPyC party 1"

def send_compteur(port: int, vecteur, context, hostname: str):
    ''' Send individual share to S1 or S2 '''

    # Setup SSL context
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    conn = context.wrap_socket(s, server_side=False, server_hostname=hostname)
    conn.connect(('localhost', port))
    
    print("Connexion établie avec le serveur :{}".format(conn.getpeername()))
    conn.send(pickle.dumps(vecteur))

def send_x(crtfile: str, key_file: str):
    ''' Send shares of x to both servers S1 and S2 '''

    # Setup SSL context
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_cert_chain(crtfile, keyfile=key_file)
    context.load_verify_locations(cafile=cafile)
    context.verify_mode = ssl.CERT_REQUIRED

    # Generate secret and send shares to S1 and S2
    x = protocol.generer_x()
    x_1, x_2 = protocol.distribute(x)
    send_compteur(config.port_compteur_1_v, x_1, context, hostname_c1)
    print("On a envoyé la part", x_1)
    send_compteur(config.port_compteur_2_v, x_2, context, hostname_c2)
    print("On a envoyé la part", x_2)

if __name__ == "__main__":

    path = os.getcwd()

    print("Client")
    voter = Thread(target=send_x,\
                   args=(os.path.join(path, f'Party_2.crt'),\
                         os.path.join(path, f'Party_2.key')))
    voter.start()
    voter.join()
        
