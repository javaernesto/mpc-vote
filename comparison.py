''' 
The following algorithms are detailled in the following papers:

[1] https://www1.cs.fau.de/filepool/publications/octavian_securescm/smcint-scn10.pdf
[2] https://www1.cs.fau.de/filepool/publications/octavian_securescm/SecureSCM-D.9.2.pdf
'''

import numpy as np

from common import *

class bit(object):
    ''' Binary object. '''

    def bit_xor(self, other):
        ''' 
        XOR in binary circuits.
        param self/other: 0 or 1
        '''
        return self ^ other

    def bit_and(self, other):
        '''
        AND in binary circuits.
        param self/other: 0 or 1 
        '''
        return self & other

    def bit_not(self):
        '''
        NOT in binary circuits.
        '''
        return ~self

    def half_adder(self, other):
        '''
        Half adder in binary circuits.
        param self/other: 0 or 1
        '''
        return self ^ other, self & other

    def carry_out(self, a, b):
        s = a ^ b
        return a ^ (s & (self ^ a))

def getBits(a: int):
    '''
    Returns the list of bits and the bit lenght of integer 'a'
    '''

    sb = bin(a)
    k = len(b) - 2 # We remove the '0b' prefix in string 'b'
    b = [int(sb[i], 2) for i in range(k)]

    return b, k

def carry(p: tuple, g: tuple):
    '''
    Carry propagation (operator o):
    return (r, s) = (p_2, g_2)o(p_1, g_1) = (p_1 & p_2, g_2 | (p_2 & g_1))
    '''

    if p is None:
        return g
    if g is None:
        return p
    r = g[0] & p[0]
    s = (g[0] & p[1]) + g[1]
    return r, s

def CarryOutAux(d: list, k: int)
    '''
    param d: ([d_k]_B, ..., [d_1]_B), where [a]_B = ([a_l], ..., [a_1])
    '''

    u = []
    if k > 1:
        for i in range(k//2):
            u_i = carry(d[2*i], d[2*i-1])
            u.append(u_i)
        return CarryOutAux(u[::-1], k//2)
    else:
        return d

def CarryOutCin(a: list, b: list, c: int):
    '''
    param a: ([a_k], ..., [a_1])\\
    param b: ([b_k], ..., [b_1])\\
    param c: public carry-in bit
    '''

    assert len(a) == len(b)
    k = len(a)
    u = []
    for i in range(k):
        u_i = (a[i] + b[i] - 2*a[i]*b[i], a[i]*b[i])
        u.append(u_i)
    
    d = CarryOutAux(u[::-1], k)
    p, g = d

    return g

def BitLT(a: int, b: list):
    '''
    return [a ?< b]

    param a: public k-bit int\\
    param b: bit-wise shared [b] = ([b_k], ..., [b_1])
    '''

    aBits, k = getBits(a)
    assert k = len(b)
    u = []
    for i in range(k):
        u_i = 1 - b[i]
    s = 1 - CarryOutCin(aBits[::-1], u[::-1], 1)

    return s

def Mod2m(a: int, k: int, m: int, kapp: int):
    '''
    Protocol Mod2m computes y = x mod 2^m for any x in [-2^(k-1), 2^(k-1) - 1] and 0 < m < k.

    param a:     [a] shared int\\
    params k, m: public integers
    '''

    b = 1<<(k-1) + a
    rr = []

    for i in range(m):                     # 1 round, m inv, m exp
        r_i = np.random.randint(0, P)
        rr.append(r_i)
    rp = sum([(2**i) * r_i for r_i in rr]) # This is the shared value in field of 'r'
    rr = r[::-1]                           # This is the bit-wise shared value of 'r'
    u = np.random.randint(0, k + kappa - m)
    r = (2**m) * u + rp

    c = b + r # Here we should open        # 1 round, 1 inv
    cc = c % (2**m)
    v = BitLT(cc, rr)                      # log(m) round, 2m - 2 inv
    bb = cc - rp + v * (2**m)

    return bb

def Trunc(a: int, k: int, m: int):
    '''
    Protocol Trunc computes floor(x / 2**m) = (x - (x mod 2**m)) * 2**(-m) for any
    x in [-2^(k-1), 2^(k-1) - 1] and 0 < m < k. Equivalent  to cutting off
    the m least significant bits of the binary representation of x

    param a:     [a] shared int\\
    params k, m: public integers
    '''

    aa = Mod2m(a, k, m)
    d = (a - aa) * ((P + 1)/2)**m # Recall that 2^-1 = (P + 1)/2

    return d


def main():
        a = [0, 1, 1, 1, 1, 0]
        b = [0, 0, 0, 1, 0, 1]
        kappa = 2
        print(carry(b,a))
        print(CarryOutAux([a, b], kappa))

if __name__ == '__main__':
    main()