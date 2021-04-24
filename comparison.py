''' 
The following algorithms are detailled in the following papers:

[1] https://www1.cs.fau.de/filepool/publications/octavian_securescm/smcint-scn10.pdf
[2] https://www1.cs.fau.de/filepool/publications/octavian_securescm/SecureSCM-D.9.2.pdf
'''

def carry(p: tuple, g: tuple, compute_p=True):
    '''
    Carry propagation (operator o):
    return (p,g) = (p_2, g_2)o(p_1, g_1) = (p_1 & p_2, g_2 | (p_2 & g_1))
    '''

    if p is None:
        return g
    if g is None:
        return p
    r = 0
    if compute_p:
        r = g[0] & p[0]
    s = (g[0] & p[1]) + g[1]
    return (r, s)


def main():
        a = [0, 1, 1, 1, 1, 0]
        b = [0, 0, 0, 1, 0, 1]
        kappa = 2
        print(carry(b,a))
        print(CarryOutAux([a, b], kappa))

if __name__ == '__main__':
    main()