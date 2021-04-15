import socket
import os
from _thread import start_new_thread
import json

from common import *

# Vote vector (will contain all the votes in a dict format)
votes = []

# Setting up the server
ServerSideSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ServerSideSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# We set a time of 10 seconds for the election
ServerSideSocket.settimeout(10.0)

host = 'localhost'
port = 2005
ThreadCount = 0
try:
    ServerSideSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Socket is listening...')
ServerSideSocket.listen(5)

# The function called by the server to handle each client as a thread
def multi_threaded_client(connection, buffer_size=2048):

    while True:
        data = connection.recv(buffer_size)
        if not data:
            break
        # response = 'Server message: ' + data.decode('utf-8')      
        # connection.sendall(str.encode(response))
        vote = json.loads(data)
        votes.append(vote)
        print("I have received: ", vote)
    connection.close()

# Doing the election
while True:
    try:
        Client, address = ServerSideSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        start_new_thread(multi_threaded_client, (Client, ))
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount))
    # When timer is reached, we begin counting the votes
    except socket.timeout:
        print("The vote is over")
        print("Sending my vector to Alice")
        # Bob's id is -1 (all the other ids are positive)
        myVotes = sum_votes(votes, -1)
        socket_send(myVotes, host, 2004)
        break
ServerSideSocket.close()