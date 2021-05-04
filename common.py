import protocols
import launch
import numpy as np


class Function(protocols.Protocols):
    def __init__(self, identity, charlie, player, length, modulo, precision):
        super().__init__(identity, charlie, player, length, modulo, precision)

    def function(self, x):
        shape = x.shape
        a = np.array([self.modulo/2]*np.prod(shape)).astype(int)
        a.shape = shape
        t = self.rabbit_compare(x, a, self.modulo)
        self.close_connexion_with_charlie()
        z = self.reconstruct(t, self.modulo)
        return z


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
