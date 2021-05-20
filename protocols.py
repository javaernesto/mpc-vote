import numpy as np
import json
from multiprocessing import Process, Manager
import math
import ast


class Protocols:
    def __init__(self, identity, charlie, player, length, modulo, numbers_size, precision):
        self.identity = identity
        self.charlie = charlie
        self.player = player
        self.length = length
        self.modulo = modulo
        self.numbers_size = numbers_size
        self.precision = precision

    def add(self, x, y, mod):
        z = x + y
        return z

    def subs(self, x, y, mod):
        z = x - y
        return z

    def add_const(self, x, k, mod):
        if self.identity == 0:
            return (x + k) % mod
        return x % mod

    def subs_const(self, x, k, mod):
        return self.add_const(self, x, -k, mod)

    def mult(self, x, y, mod):
        triple = json.dumps(['triple', mod, x.shape])
        self.charlie.sendall(bytes(triple, encoding="utf-8"))
        triple = self.charlie.recv(self.length)
        triple = eval(triple.decode("utf-8"))
        a, b, c = np.array(triple[0]), np.array(triple[1]), np.array(triple[2])
        d = self.subs(x, a, mod)
        e = self.subs(y, b, mod)
        message = [d.tolist(), e.tolist()]
        message = self.reconstruct(message, mod)
        d = message[0]
        e = message[1]
        z = self.add_const(c + d * b + e * a, e * d, mod)
        if mod != 2:
            z = self.truncate(z, mod)
        return z

    def truncate(self, x, mod):
        x = self.add_const(x, int(self.numbers_size), mod)
        pair = json.dumps(['pair', mod, 2**self.precision, self.numbers_size, x.shape])
        self.charlie.sendall(bytes(pair, encoding="utf-8"))
        pair = self.charlie.recv(self.length)
        pair = eval(pair.decode("utf-8"))
        r1, r2 = np.array(pair[0]), np.array(pair[1])
        r = 2**self.precision*r2+r1
        c = self.add(x, r, mod)
        message = self.reconstruct(c.tolist(), mod)
        c = message
        r1_ = (-r1) % mod
        c_ = c % 2**self.precision
        a_ = self.add_const(r1_, c_, mod)
        inverse = math.floor(((mod+1)/2)**self.precision) % mod
        d = ((x - a_) * inverse) % mod
        d = self.add_const(d, -int(self.numbers_size / 2 ** self.precision), mod)
        return d

    def reconstruct(self, x, mod):
        self.broadcast(x)
        y = self.receive_broadcast()
        y.append(x)
        return np.sum(y, 0) % mod

    def close_connexion_with_charlie(self):
        message = json.dumps('close')
        self.charlie.sendall(bytes(message, encoding="utf-8"))

    def broadcast(self, message):
        if type(message) != list:
            message = message.tolist()
        message = json.dumps(message)
        for i in range(len(self.player)):
            self.player[i].sendall(bytes(message, encoding="utf-8"))

    def receive_from(self, i, y):
        message = self.player[i].recv(self.length)
        a = eval(message.decode("utf-8"))
        y[i] = a

    def receive_broadcast(self):
        manager = Manager() # dans multiprocessing
        y = manager.list(['err']*len(self.player))
        processes = [Process(target=self.receive_from, args=(i, y,)) for i in range(len(self.player))]
        [processes[i].start() for i in range(len(self.player))]
        [processes[i].join() for i in range(len(self.player))]
        return y

    def bin_or(self, x, y):
        z = self.add(x, y, 2)
        m = self.mult(x, y, 2)
        return self.add(z, m, 2)

    # retourne c public < x secret si les deux sont en binaire
    def less_than(self, c, x):
        c = np.array(c, dtype="object")
        c_copy = np.copy(c)
        y = self.add_const(x, c_copy, 2)
        shape = list(c_copy.shape)
        final_shape = tuple(shape[:-1])
        y.shape = (np.prod(final_shape), shape[-1])
        y = y.transpose()
        z = y[-1]
        z.shape = (1, len(y[0]))
        w = z[0]
        w.shape = (1, len(y[0]))
        for i in range(len(y) - 1):
            z = np.insert(z, 0, self.bin_or(y[len(y) - i - 2], z[0]), axis=0)
            w = np.insert(w, 0, (z[0] + z[1]) % 2, axis=0)
        c_copy.shape = w.transpose().shape
        w = np.sum(w.transpose() * (1-c_copy), 1) % 2
        w.shape = final_shape
        return w

    def convert_from_bin(self, x, mod):
        eda = json.dumps(['eda', 1, 1, mod, x.shape])
        self.charlie.sendall(bytes(eda,encoding="utf-8"))
        eda = self.charlie.recv(self.length)
        eda = eval(eda.decode("utf-8"))
        r, r_bin = np.array(eda[0], dtype="object"), np.array(eda[1], dtype="object")
        r_bin.shape = x.shape
        y = self.reconstruct(self.add(x, r_bin, 2), 2)
        z = self.add_const(r - 2 * y * r, y, mod)
        return z

    # devrait retourner x secret < c publique dans l'anneau
    def rabbit_compare(self, x, c, mod):
        k = math.floor(math.log(mod, 2))+2
        eda = json.dumps(['eda', mod, k, mod, x.shape])
        self.charlie.sendall(str.encode(eda))
        eda = self.charlie.recv(self.length)
        eda = eda.decode("utf-8")
        eda = ast.literal_eval(eda)
        r, r_bin = np.array(eda[0], dtype="object"), np.array(eda[1], dtype="object")
        a = (x+r) % mod
        a = self.reconstruct(a, mod)
        b = (a - c) % mod
        b_bin = self.convert_to_bin(b, k)
        a_bin = self.convert_to_bin(a, k)
        # w1 = self.less_than(a_bin, r_bin) #on veut a<r
        # w2 = self.less_than(b_bin, r_bin) #on veut b<r
        w = self.less_than(np.concatenate((a_bin, b_bin)), np.concatenate((r_bin, r_bin)))  # on veut a<r et b<r
        w1 = w[:a_bin.shape[0]]
        w2 = w[a_bin.shape[0]:]
        w3 = b < (mod-c)
        w_bin = self.add_const(w1-w2, w3, 2)
        w_bin = self.add_const(-w_bin, 1, 2)
        w = self.convert_from_bin(w_bin, mod)
        return w

    @staticmethod
    def convert_to_bin(x, width):
        numbers = np.copy(x)
        length = np.prod(numbers.shape)
        original_shape = tuple(list(numbers.shape)+[width])
        numbers.shape = (1, length)
        numbers = numbers[0]
        array = [[int(b) for b in f'{num:0{width}b}'[::-1]] for num in numbers]
        array = np.array(array)
        array.shape = original_shape
        return array
