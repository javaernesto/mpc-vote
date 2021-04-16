import numpy as np
import pickle


class Protocols:
    def __init__(self, identity, charlie, player, length):
        self.identity = identity
        self.charlie = charlie
        self.player = player
        self.length = length

    def add(self, x, y, mod):
        return (x + y) % mod

    def subs(self, x, y, mod):
        return (x - y) % mod

    def add_const(self, x, k, mod):
        if self.identity != 0:
            k = 0
        return (x + k) % mod

    def subs_const(self, x, k, mod):
        return self.add_const(self, x, -k, mod)

    def mult(self, x, y, mod):
        shape = pickle.dumps(['triple', mod, x.shape])
        self.charlie.send(shape)
        triple = self.charlie.recv(self.length)
        triple = pickle.loads(triple)
        a, b, c = np.array(triple[0]), np.array(triple[1]), np.array(triple[2])
        d = self.subs(x, a, mod)
        e = self.subs(y, b, mod)
        message = pickle.dumps([d.tolist(), e.tolist()])
        self.player.send(message)
        message = self.player.recv(self.length)
        message = pickle.loads(message)
        d = self.add(d, np.array(message[0]), mod)
        e = self.add(e, np.array(message[1]), mod)
        z = self.add_const(c + d * b + e * a, e * d, mod)
        return z

    def reconstruct(self, x, mod):
        message = pickle.dumps(x)
        self.player.send(message)
        message = self.player.recv(self.length)
        message = pickle.loads(message)
        return (message + x) % mod
    
    def close_connexion_with_charlie(self):
        message = pickle.dumps('close')
        self.charlie.send(message)

