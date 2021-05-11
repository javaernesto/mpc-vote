import sys
import argparse
import json
import numpy as np

try:
    from mpyc.runtime import mpc
    from mpyc.random import randint
except ImportError:
    print("Error importing MPyC...")
    print("Please visit https://www.win.tue.nl/~berry/mpyc/ for installing MPyC")
    sys.exit(1)
   
# MPC params
m = len(mpc.parties)
mpc.threshold = 0

# MPC types
secint = mpc.SecInt(64)

def setup():
    ''' Setups the election '''

    parser = argparse.ArgumentParser()

    group = parser.add_argument_group('Election configuration')
    group.add_argument('-v', '--voters', type=int, help='Set the number of voters for the election')
    group.add_argument('-c', '--choices', type=int, help='Set the number of choices for the election')
    group.add_argument('--read-file', type=str, help='Provide file contatining the votes')

    args = parser.parse_args()

    if args.read_file:
        filename = args.read_file
        with open(filename, 'r') as f:
            content = f.read().splitlines()
        # Check all votes have the same length
        assert all(len(line) == len(line[0]) for line in content[1:])
        num_choice = len(json.loads(content[0]))
        # Check number of votes
        num_voters = len(content)

        return num_choice, num_voters

    if args.voters:
        num_voters = args.voters
        print("Setting number of voters to {}".format(num_voters))
    else:
        num_voters = 10
        print("Setting number of voters to default = {}".format(num_voters))
    if args.choices:
        num_choice = args.choices
        print("Setting number of choices to {}".format(num_choice))
    else:
        num_choice = 5
        print("Setting number of choices to default = {}".format(num_choice))

    return num_choice, num_voters

# Config election parameters
num_choice, num_voters = setup()

def write_votes_to_file(filename: str) -> None:
    ''' Writes a designated number of random votes into file '''

    with open(filename, 'w') as f:
        for _ in range(num_voters):
            vote = [0] * num_choice
            c = np.random.randint(0, num_choice)
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

    assert len(sec_votes) == num_voters
    votes_sum = [secint(0)] * num_choice
    for sec_vote in sec_votes:
        votes_sum = mpc.vector_add(votes_sum, sec_vote)

    return sec_votes, votes_sum
        

async def to_vote(sec_c: secint) -> list:
    ''' Individual vote for one candidate (0 <= `sec_c` < `num_choice`) '''

    vote = [0] * num_choice
    c = await mpc.output(sec_c)
    assert (0 <= c) and (c < num_choice), "Your vote is not valid"
    vote[c] = 1
    sec = list(map(secint, vote))
    
    return sec

async def elect() -> list:
    ''' Do the election. Repeat randomly `num_voters` times a vote '''

    votes = []

    for i in range(num_voters):
        sec_c = randint(secint, 0, num_choice - 1)
        vote = await to_vote(sec_c)
        votes.append(vote)

    assert len(votes) == num_voters
    votes_sum = [secint(0)] * num_choice
    for vote in votes:
        votes_sum = mpc.vector_add(votes_sum, vote)

    return votes, votes_sum   

async def reveal_votes() -> list:
    ''' Reveals the result of the election (as a vector containing each number of votes by coordinate) '''
    
    _, res = await elect()
    Results = await mpc.output(res)
    print("Election results: ", Results)

    return Results

async def most_voted() -> list:
    ''' Reveals the position of the most voted candidate '''

    _, mv = await elect()
    i, _ = mpc.argmax(mv)
    k = await mpc.output(i)
    winner = [0] * num_choice
    winner[k] = 1
    print("Winner results  : ", winner)

    return winner
         
if __name__ == '__main__':

    # Start Runtime
    mpc.run(mpc.start())

    # Do election
    # write_votes_to_file('votes.txt')
    mpc.run(elect())
    # mpc.run(read_votes_from_file('votes.txt'))
    # mpc.run(reveal_votes())
    mpc.run(most_voted())

    # End Runtime
    mpc.run(mpc.shutdown())
