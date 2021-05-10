import sys
import argparse
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

async def to_vote(sec_c: secint, num_choice: int):
    ''' Individual vote for one candidate (0 <= `c` < `num_choice`) '''

    vote = [0] * num_choice
    c = await mpc.output(sec_c)
    assert (0 <= c) and (c < num_choice), "Your vote for {} is not valid".format(c)
    vote[c] = 1
    sec = list(map(secint, vote))
    
    return sec

async def elect(num_choice: int, num_voters: int) -> list:
    ''' Do the election. Repeat randomly `num_voters` times a vote '''

    votes = []

    for i in range(num_voters):
        sec_c = randint(secint, 0, num_choice - 1)
        vote = await to_vote(sec_c, num_choice)
        votes.append(vote)

    assert len(votes) == num_voters
    votes_sum = [secint(0)] * num_choice
    for vote in votes:
        votes_sum = mpc.vector_add(votes_sum, vote)

    return votes, votes_sum   

async def reveal(num_choice: int, num_voters: int) -> list:
    ''' Reveals the result of the election (as a vector containing each number of votes by coordinate) '''
    
    _, res = await elect(num_choice, num_voters)
    Results = await mpc.output(res)
    print("Election results: ", Results)

    return Results

async def most_voted(num_choice: int, num_voters: int) -> list:
    ''' Returns the position of the most voted candidate '''

    _, mv = await elect(num_choice, num_voters)
    i, _ = mpc.argmax(mv)
    k = await mpc.output(i)
    winner = [0] * num_choice
    winner[k] = 1
    print("Winner results  : ", winner)

    return winner
    
def setup():
    ''' Setups the election '''

    parser = argparse.ArgumentParser()

    group = parser.add_argument_group('Election configuration')
    group.add_argument('-v', '--voters', type=int, help='Set the number of voters for the election')
    group.add_argument('-c', '--choices', type=int, help='Set the number of choices for the election')

    args = parser.parse_args()

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
        
if __name__ == '__main__':

    # Config election parameters
    num_choice, num_voters = setup()

    # Start Runtime
    mpc.run(mpc.start())

    # Do election
    mpc.run(elect(num_choice, num_voters))
    mpc.run(reveal(num_choice, num_voters))
    mpc.run(most_voted(num_choice, num_voters))

    # End Runtime
    mpc.run(mpc.shutdown())
