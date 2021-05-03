from typing import *
import sys

from mpi4py import MPI
import numpy as np

from common import num_choice, P

def sum_votes(votes_array: list):
    ''' Sums the votes (modulo P) contained in votes_array '''

    # Init
    n = len(votes_array)
    myVote = np.zeros(num_choice, dtype=int)

    # We sum all of our votes
    for i in range(0, n):
        for j in range(num_choice):
            myVote[j] = (myVote[j] + votes_array[i][j]) % P

    return myVote

def getShares(vote):
    ''' Get shares for both checkers from the vote '''

    # Creation of mask (because players=2)
    mask = np.random.randint(P, size=num_choice)

    # Creation of shares
    a = np.zeros(num_choice, dtype=int)
    for i in range(num_choice):
        a[i] = (vote[i] - mask[i]) % P

    return (a, mask)

def send_all(mpi_comm, myVote):
    ''' Broadcasts vote from mpi_comm to every other player '''

    rank = mpi_comm.Get_rank()
    size = mpi_comm.Get_size()

    for i in range(size):
        if i != rank:
            mpi_comm.Isend([myVote, MPI.INT], dest=i)
            otherVote = np.empty(num_choice, dtype=int)
            mpi_comm.Irecv([otherVote, MPI.INT], source=rank)

def count_votes(myVote, mpi_comm):
    '''
    Counts vote at the end of election. Each player sends the other player his vector
    and they both print the result of the election

    param myVote:   the vote from the player
    param mpi_comm: the MPI communicator of the other player
    '''

    # This code blocks because Bcast() is blocking and checker 0 never receives from 1
    # rank = mpi_comm.Get_rank()

    # mpi_comm.bcast(myVote, root=rank)
    # if rank == 0:
    #     otherVote = np.empty(num_choice, dtype=int)
    #     mpi_comm.Bcast(otherVote, root=1)
    # elif rank == 1:
    #     otherVote = np.empty(num_choice, dtype=int)
    #     mpi_comm.Bcast(otherVote, root=0)
    
    # result = sum_votes([myVote, otherVote])
    # print("Results from {}: {}".format(rank, result))

    if mpi_comm.Get_rank() == 0:
        mpi_comm.Isend([myVote, MPI.INT], dest=1)
        otherVote = np.empty(num_choice, dtype=int)
        mpi_comm.Recv([otherVote, MPI.INT], source=1)
        result = sum_votes([myVote, otherVote])
        print("Results: {}".format(result))
    elif mpi_comm.Get_rank() == 1:
        mpi_comm.Isend([myVote, MPI.INT], dest=0)
        otherVote = np.empty(num_choice, dtype=int)
        mpi_comm.Recv([otherVote, MPI.INT], source=0)
        result = sum_votes([myVote, otherVote])
        print("Results: {}".format(result))

# Main routine
def main():

    # Get MPI communicator, rank and world size
    mpi_comm = MPI.COMM_WORLD
    mpi_size = mpi_comm.Get_size()
    mpi_rank = mpi_comm.Get_rank()

    # If only one process, exit
    if mpi_size == 1:
        print("Only one task in your MPI program!")
        print("Aborting...")
        return 1

    # Call the functions (rank 0 and 1 correspond to Alice and Bob)
    if mpi_rank == 0 or mpi_rank == 1: # Alice or Bob
        return mpi_check(mpi_comm)
    else: # Voters
        return mpi_voter(mpi_comm)

# Code for Alice
def mpi_check(mpi_comm):
    '''
    Gathers votes from every voter (rank >= 2) and then waits for the other checker's vector.
    Then count the votes and prints the results of the election.

    param mpi_comm: the MPI communicator
    '''

    # Declare empty list to gather votes
    votes_array = []

    # We receive each vote individually
    mpi_size = mpi_comm.Get_size()
    for i in range(2, mpi_size): # We iterate the voters (i.e. rank >= 2)
        vote = np.empty(num_choice, dtype=int)
        mpi_comm.Recv([vote, MPI.INT], source=i)
        print("Checker {} received vote from voter {}: {}".format(mpi_comm.Get_rank(), i, vote))
        votes_array.append(vote)

    # Check if we have received every vote (except for Bob)
    if len(votes_array) != mpi_size - 2:
        print("ERROR! The MPI world has {} voters, but we have only gathered {} votes.".format(mpi_size - 2, len(votes_array)))
        return 1

    # Sum checker's votes and print them
    myVote = sum_votes(votes_array)
    print("Checker {} vector: {}".format(mpi_comm.Get_rank(), myVote))

    # Count the votes and print the result of the elections
    count_votes(myVote, mpi_comm)

def mpi_voter(mpi_comm):
    '''
    Creates random votes a obtains shares for both checkers and sends them.

    param mpi_comm: the MPI communicator
    '''

    # We create a random vote 
    j = np.random.randint(0, num_choice)
    vote = np.zeros(num_choice, dtype=int)
    vote[j] = 1

    # Get shares for sending to Alice and Bob
    a, b = getShares(vote)

    # On envoie 'a' à Alice, et 'b' à Bob
    mpi_comm.Send([a, MPI.INT], dest=0)
    mpi_comm.Send([b, MPI.INT], dest=1)

if __name__ == '__main__':
    sys.exit(main())