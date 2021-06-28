import numpy as np

# Set elections parameters
N_VOTERS = 2
N_CHOICE = 5

# Set ports
port_compteur_1_v=11637
port_compteur_2_v=11638
port_compteur_1_c = 21636
port_audit = 23213

# Set hostnames
hostname = "Party n 0"

# Set public parameters (we must have p prime and p > N_VOTERS)
P = 17
BIT_NUM = 16
SIZE_OF_INT = 1 << BIT_NUM

# Set file names for Pickle
FILEC1 = "fileC1.txt"
FILEC2 = "fileC2.txt"