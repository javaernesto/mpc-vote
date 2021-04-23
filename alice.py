import socket
import os
from _thread import start_new_thread
import json

from common import *

# Vote vector (will contain all the votes in a dict format)
votes = []

# The function called by the server to handle each client as a thread
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

def main():

	# Setting up the server
	ServerSideSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ServerSideSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# We set a time of 10 seconds for the election
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
			print("Waiting for Bob's vector")
			while True:
				# Alice asks Bob for his vector
				try:
					# We wait one second for Bob's vector
					ServerSideSocket.settimeout(1.0)
					bob, address = ServerSideSocket.accept()
					print('Connected to: ' + address[0] + ':' + str(address[1]))
					start_new_thread(multi_threaded_client, (bob, ))
				# When the timer is reached again, Alice sums the votes and recovers the results
				except socket.timeout:
					# The last item of 'votes' contains the voted sent by Bob.
					# Therefore we must sum all but the last of Alice's votes to get Alice's vector
					myVotes = sum_votes(votes[:-2], -2)
					bobVote = svote(np.array(votes[-1]['vote']), -1)
					print("My votes: ", myVotes)
					print("Bob's votes: ", bobVote)
					print("Election results: ", myVotes + bobVote)
					break
			break
	ServerSideSocket.close()

if __name__ == "__main__":
	main()

	
