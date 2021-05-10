# mpc-vote

## MPC vote using Python sockets
For now, the votes are randomly created. Alice and Bob receive the votes and then Bob sends his vector to Alice, who then sums the two vectors

To run the code, open three terminals, and run in order:
```
python3 alice.py
python3 bob.py (in a separate terminal) 
python3 voter.py n (in a separate terminal)
```
where 'n' must be a integer greater or equal to 2 (representing the number of voters). The results will apears on Alice's terminal once the vote and the counting are complete.

## MPC vote using MPI (Message Parsing Interface)
To install MPI and use it in Python, open a terminal and run:
```
pip install mpi4py
```
Then you can run the file `mpi_vote.py` with 4 process (the 2 checkers and 2 voters), with the following:
```
mpirun -n 4 python3 mpi_vote.py
```

## MPC vote using MPyC
First you will need to install MPyC (Python package for secure multiparty computation) on each party's computer. For that, you can visit the [offical website of the project](https://www.win.tue.nl/~berry/mpyc/). After installing the package, you can launch the script `mpyc_vote.py`. There are **three ways** to do so:

1. **Launch the script locally on one computer** (with `m` parties).
For that, use the flag `'-M'` provided by MPyC to set the number of parties. For example, to launch the election locally on your computer with two parties (e.g. Alice and Bob), write:
```
python mpyc_vote.py -M 2
```

2. **Launch the script on one or more machines via the command line.** 
Use the flag `'-P'` followed by an address in the format `addr=host:port`. The party that will launch the script must leave its `host` field blank. For example, to launch the election with two parties on the same host, one can launch
```
python mpyc_vote.py -P :8888 -P localhost:8889
```
assuming the party launching the script will be listening on port 8888. In this same example, the other party should open another terminal window and write
```
python mpyc_vote.py -P localhost:8888 -P :8889
```

3. **Launch the script on one or more machines via configuration files** (INI files).
 Use the flag `'-C'` or `'--config'` followed by the name of a .ini file. The INI file must be placed in a folder `.config` in the same directory as the script `mpyc_vote.py`. Each party must have a INI file. Continuing with the above example, the first party must have a INI file called `Party_0.ini` that looks like this:
 ```
 [Party 0]
 host =
 port = 8888
 
 [Party 1]
 host = localhost
 port = 8889
 ```
 again with the `host` field of the party launching the script left blank. Then one can launch the script with the following instruction:
 ```
python mpyc_vote.py -C Party_0.ini
```
The other party should open a terminal window and launch the same instruction, this time with `Party_1.ini` written in an analogous fashion as `Party_0.ini`.

Once these configurations are set, you can past additional arguments such as the number of voters (with the flag `'-v'` or `'--voters'`) and the number of choices in the election (with the flag `'-c'` or `'--choices'`). The default parameters are set for a number of voters equal to 10 and a number of choices equal to 5.

As a final example, we illustrate how the launch an election locally on one computer with 2 parties, 100 voters, and 10 choices. Open a terminal and type:
```
python mpyc_vote.py -M 2 -v 100 -c 10
```
