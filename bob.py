import socket
import os
from _thread import start_new_thread
import json

from common import *

# Init votes
votes = []

ServerSideSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ServerSideSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

while True:
    try:
        Client, address = ServerSideSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        start_new_thread(multi_threaded_client, (Client, ))
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount))
    except socket.timeout:
        print("The vote is over")
        print("Sending my vector to Alice")
        myVotes = sum_votes(votes)
        socket_send(myVotes, -1, host, 2004)
        break
ServerSideSocket.close()