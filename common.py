import protocols
import launch
import numpy as np
import time
import matplotlib.pyplot as plt


class Function(protocols.Protocols):
    def __init__(self, identity, charlie, player, length, modulo, numbers_size, precision):
        super().__init__(identity, charlie, player, length, modulo, numbers_size, precision)

    def function(self, x):
        y = x[0][1]
        x = x[0][0]
        z = self.mult(x, y, self.modulo)
        z = self.reconstruct(z, self.modulo)
        z = (((z + self.numbers_size) % self.modulo) - self.numbers_size)/2**self.precision
        if self.identity == 0:
            print(z)
            # print((((z+self.numbers_size/2) % self.modulo) - self.numbers_size/2)/(2**self.precision))
        self.close_connexion_with_charlie()
        return 0


def main():
    a, b, c, d, e = np.random.randint(1001, 10000), np.random.randint(1001, 10000), np.random.randint(1001, 10000), np.random.randint(1001, 10000), np.random.randint(1001, 10000)
    print(a, b, c, d, e)
    mpc = launch.Mpc()
    mpc.add_player('provider', 'localhost', a)
    mpc.add_player('alice', 'localhost', b)
    mpc.add_player('bob', 'localhost', c)
    mpc.add_player('eve', 'localhost', d)
    mpc.add_player('jane', 'localhost', e)
    mpc.start()


if __name__ == '__main__':
    main()
