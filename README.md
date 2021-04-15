# mpc-vote

For now, the votes are randomly created. Alice and Bob receive the votes and then Bob sends his vector to Alice, who then sums the two vectors

To run the code, open three terminals, and run in order:
```
python3 alice.py
python3 bob.py (in a separate terminal) 
python3 voter.py n (in a separate terminal)
```
where 'n' must be a integer greater or equal to 2 (representing the number of voters). The results will apears on Alice's terminal one the vote and the counting are complete.
