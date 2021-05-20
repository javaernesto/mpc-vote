import sys
import argparse
import json

import numpy as np

try:
	from mpyc.runtime import mpc
	from mpyc.random import randint
except ImportError:
	print("Error importing MPyC...")
	print("Please visit https://github.com/lschoe/mpyc for installing MPyC")
	sys.exit(1)
   
# MPC params
m = len(mpc.parties)
mpc.threshold = 0       # No secrecy

# MPC types
secint = mpc.SecInt(64)

class ElectionManager:
	''' Class for keeping track of all the election parameters set during setup. Function setup()
		will return an instance of this class.
	'''

	def __init__(self, num_choice: int, num_voters: int, res: bool, win: bool, filename=None):
		''' Init params of the election '''
		self.num_choice = num_choice
		self.num_voters = num_voters
		self.res = res
		self.win = win
		self.filename = filename

	def __str__(self):
		''' Allows to represent the params of the election '''
		a = "Launching election with the following parameters:\n"
		b = "Number of choices = 5 (default)\n" if self.num_choice == 5 else "Number of choices = {}\n".format(self.num_choice)
		c = "Number of voters = 10 (default)\n" if self.num_voters == 10 else "Number of voters  = {}\n".format(self.num_voters)
		d = "Show results = True (default)" if self.res else "Show winner = True"
 
		return a + b + c + d


def setup():
	''' Setups the election '''

	parser = argparse.ArgumentParser()

	group = parser.add_argument_group('Election configuration')
	group.add_argument('-v', '--voters', metavar='V', type=int, help='Set the number of voters for the election')
	group.add_argument('-c', '--choices', metavar='C', type=int, help='Set the number of choices for the election')
	group.add_argument('--read-file', metavar='FILE', type=str, help='Provide file containing the votes')

	group = parser.add_argument_group('Results configuration')
	group.add_argument('--winner', action='store_true', default=False, help='Show only the winner of the election')

	args = parser.parse_args()

	# Parsing errors handling
	if args.read_file and (args.voters or args.choices):
		print("Error parsing config: --read-file and -v | -c are mutually exclusive")
		sys.exit(2)

	if args.voters:
		num_voters = args.voters
	else:
		num_voters = 10
	if args.choices:
		num_choice = args.choices
	else:
		num_choice = 5
	if args.winner:
		res, win = False, True
	else:
		res, win = True, False

	if args.read_file:
		filename = args.read_file
		with open(filename, 'r') as f:
			content = f.read().splitlines()
		# Check all votes have the same length
		num_choice = len(json.loads(content[0]))
		assert all(len(json.loads(line)) == num_choice for line in content[1:]), "Bad votes file. Try again"
		# Check number of votes
		num_voters = len(content)
		# No random or input
		ran, inp = False, False

		return ElectionManager(num_choice, num_voters, res, win, filename)

	return ElectionManager(num_choice, num_voters, res, win, None)

# Config election parameters
em = setup()
print(em)

def write_votes_to_file(filename: str) -> None:
	''' Writes a designated number of random votes into file '''

	with open(filename, 'w') as f:
		for _ in range(em.num_voters):
			vote = [0] * em.num_choice
			c = np.random.randint(0, em.num_choice)
			vote[c] = 1
			vote = json.dumps(vote)
			f.write(vote + '\n')

async def read_votes_from_file(filename: str) -> list:
	''' Reads the votes from a file and returns a list of secret votes and the secret sum of these votes '''

	sec_votes = []

	with open(filename, 'r') as f:
		content = f.read().splitlines()

	for line in content:
		line = json.loads(line)
		sec_vote = list(map(secint, line))
		sec_votes.append(sec_vote)

	assert len(sec_votes) == em.num_voters
	votes_sum = [secint(0)] * em.num_choice
	for sec_vote in sec_votes:
		votes_sum = mpc.vector_add(votes_sum, sec_vote)

	return sec_votes, votes_sum
		
async def to_vote(sec_c: secint) -> list:
	''' Individual vote for one candidate (0 <= `sec_c` < `num_choice`) '''

	vote = [0] * em.num_choice
	c = await mpc.output(sec_c)
	# assert (0 <= c) and (c < num_choice), "Your vote is not valid"
	vote[c] = 1
	sec = list(map(secint, vote))
	sec_vote = mpc.input(sec, senders=mpc.pid)
	
	return sec_vote

async def elect_input() -> list:
	''' Do the election. Asks for input for `num_voters` voters. 
		The input should be a number between 0 and `num_choice` - 1.
	'''

	votes = []
	print("Welcome to the election.")
	print("To vote, please enter a number between 0 and {}".format(em.num_choice - 1))

	if mpc.pid == 0:
		for i in range(em.num_voters):
			c = int(input('Enter your vote here -> '))
			vote = [0] * em.num_choice
			vote[c] = 1
			# vote = list(map(secint, vote))
			vote = [secint(v) for v in vote]
			# sec_vote = mpc.input(vote)[mpc.pid]
			sec_vote = mpc.input(vote, senders=mpc.parties[1:])
			for i in range(1, m):
				print(type(sec_vote[i]))
				await mpc._send_message(i, bytes(sec_vote[i]))
	else:
		sec_vote = await mpc._receive_message(0)
		votes.append(sec_vote)
	
	# for i in range(em.num_voters):
	# 	c = int(input('Enter your vote here -> '))
	# 	vote = [0] * em.num_choice
	# 	vote[c] = 1
	# 	# vote = list(map(secint, vote))
	# 	vote = [secint(v) for v in vote]
	# 	# sec_vote = mpc.input(vote)[mpc.pid]
	# 	sec_vote = mpc.input(vote)
	# 	votes.append(sec_vote[mpc.pid])

	assert len(votes) == em.num_voters
	votes_sum = [secint(0)] * em.num_choice
	for vote in votes:
		votes_sum = mpc.vector_add(votes_sum, vote)

	return votes, votes_sum   

def distribute(vote: np.ndarray) -> list:
	''' Creates m shares of the vote, one for each player '''
	
	shares = [0] * m

	for i in range(1, m):
		s = np.random.randint(size=em.num_choice)
		shares[i] = s

	s = np.zeros(em.num_choice, dtype=int)
	for p in shares[1:]:
		s = (p + s)
	shares[0] = (vote - s)
	
	return shares

async def elect_split() -> list:
	''' Do the election by spliting the votes before sending them to the parties '''

	vote = [0] * em.num_choice
	c = np.random.randint(0, em.num_choice, dtype=int)
	vote[c] = 1

	# Apply mask
	shares = distribute(vote)
	sec_votes = [list(map(secint, share)) for share in shares]
	sec_votes = await mpc.input(sec_votes)

	# Sum all votes
	assert len(sec_votes) == em.num_voters
	votes_sum = [secint(0)] * em.num_choice
	for sec_vote in sec_votes:
		votes_sum = mpc.vector_add(votes_sum, sec_vote)

	return sec_votes, votes_sum   

async def elect_random() -> list:
	''' Do the election. Repeat randomly `num_voters` times a vote '''

	votes = []

	for i in range(em.num_voters):
		sec_c = randint(secint, 0, em.num_choice - 1)
		vote = await to_vote(sec_c)
		votes.append(vote)

	assert len(votes) == em.num_voters
	votes_sum = [secint(0)] * em.num_choice
	for vote in votes:
		votes_sum = mpc.vector_add(votes_sum, vote)

	return votes, votes_sum   

async def reveal_votes(sec_vec: list) -> list:
	''' Reveals the result of the election (as a vector containing each number of votes by coordinate) '''
	
	Results = await mpc.output(sec_vec)
	print("Election results: ", Results)

	return Results

async def most_voted(sec_vec: list) -> list:
	''' Reveals the position of the most voted candidate '''

	i, _ = mpc.argmax(sec_vec)
	k = await mpc.output(i)
	winner = [0] * em.num_choice
	winner[k] = 1
	print("Winner results: ", winner)

	return winner
		 
if __name__ == '__main__':

	# Start Runtime
	mpc.run(mpc.start())
	# print("Connected to", mpc.parties[mpc.pid].host, ":", mpc.parties[mpc.pid].port)

	# Do election
	if em.filename:
		_, sec_vec = mpc.run(read_votes_from_file(em.filename))
		if em.res:
			mpc.run(reveal_votes(sec_vec))
		if em.win:
			mpc.run(most_voted(sec_vec))
	else:
		_, sec_vec = mpc.run(elect_input())
		if em.res:
			mpc.run(reveal_votes(sec_vec))
		if em.win:
			mpc.run(most_voted(sec_vec))

	# Test
	# print("Parties", mpc.parties)
	# print("Threshold", mpc.threshold)
	# print("Options", mpc.options)
	# print("PID", mpc.pid)
	# print("Loop", mpc._loop)
	# print("Program Counter", mpc._program_counter)
	# print("Program Counter Level", mpc._pc_level)
	
	# End Runtime
	mpc.run(mpc.shutdown())
