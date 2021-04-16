import protocols
import launch


class Function(protocols.Protocols):
    def __init__(self, identity, charlie, player, length):
        super().__init__(identity, charlie, player, length)

    # Fonction qui calcul x^5
    def function(self, x, mod):
        y = self.mult(x, x, mod)
        for i in range(3):
            y = self.mult(y, x, mod)
        self.close_connexion_with_charlie()
        return y


def main():
    a, b, c = 5555,5550,5552 #np.random.randint(1001, 10000), np.random.randint(1001, 10000), np.random.randint(1001, 10000)
    print(a, b, c)
    mpc = launch.Mpc()
    mpc.add_player('provider', 'localhost', a)
    mpc.add_player('alice', 'localhost', b)
    mpc.add_player('bob', 'localhost', c)
    mpc.start()


if __name__ == '__main__':
    main()
