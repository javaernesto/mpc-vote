import socket
import os
from _thread import start_new_thread
import json

from common import *

# Vecteur de votes
votes = []

ServerSideSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ServerSideSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ServerSideSocket.settimeout(10.0)
host = 'localhost'
port = 2004
ThreadCount = 0
try:
    ServerSideSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Socket is listening...')
ServerSideSocket.listen(5)

def multi_threaded_client(connection, buffer_size=2048):

    while True:
        data = connection.recv(buffer_size)
        if not data:
            break
        vote = json.loads(data)
        votes.append(vote)
        if vote['id'] == -1:
            print("Welcome Bob")
            print("Bob sent ", vote)
            votes.append(vote)
            break

        print("I have received: ", vote)
    connection.close()

while True:
    try:
        Client, address = ServerSideSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        start_new_thread(multi_threaded_client, (Client, ))
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount))
    except socket.timeout:
        print("The vote is over")
        print("Waiting for Bob's vector")
        while True:
            try:
                bob, address = ServerSideSocket.accept()
                print('Connected to: ' + address[0] + ':' + str(address[1]))
                start_new_thread(multi_threaded_client, (bob, ))
            except socket.timeout:
                myVotes = sum_votes(votes[:-2])
                bobVote = svote(np.array(votes[-1]['vote']))
                print("My votes: ", myVotes)
                print("Bob's votes: ", bobVote)
                print("Election results: ", myVotes + bobVote)
                break
        break
ServerSideSocket.close()