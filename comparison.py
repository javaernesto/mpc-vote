''' 
Implementation of bit-wise and arithmetics algorithms in MPC. The main topics covered are:
- Truncation
- Integer comparison
- Bit decomposition

The following algorithms are detailled in the following papers:

[1] https://www1.cs.fau.de/filepool/publications/octavian_securescm/smcint-scn10.pdf
[2] https://www1.cs.fau.de/filepool/publications/octavian_securescm/SecureSCM-D.9.2.pdf
'''

import numpy as np
import math

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
    k = len(sb) - 2 # We remove the '0b' prefix in string 'b'
    b = [int(sb[i], 2) for i in range(2, k + 2)]

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

def CarryOutAux(d: list, k: int):
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
        return d[0]

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
    print(k)
    print(len(b))
    assert k == len(b)
    u = []
    for i in range(k):
        u_i = 1 - b[i]
        u.append(u_i)
    s = 1 - CarryOutCin(aBits[::-1], u[::-1], 1)

    return s

def Mod2m(a: int, k: int, m: int, kappa: int):
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
    rr = rr[::-1]                          # This is the bit-wise shared value of 'r'
    u = np.random.randint(0, k + kappa - m)
    r = (2**m) * u + rp

    c = b + r # Here we should open        # 1 round, 1 inv
    cc = c % (2**m)
    print("cc = ", c)
    v = BitLT(cc, rr)                      # log(m) round, 2m - 2 inv
    bb = cc - rp + v * (2**m)

    return bb

def LSB(a: int, k: int, kappa: int):
    '''
    Extraction of the least significant bit. We compute y = x mod 2 for x in [-2^(k-1), 2^(k-1) - 1]

    param a:     [a] shared int\\
    param k:     public integer\\
    param kappa: security parameter
    '''

    b = np.random.randint(0, 2)                   # 1 round, 1 inv, 1 exp
    r = np.random.randint(0, k + kappa - 1)
    c = 2**(k-1) + a + 2*r + b_1      # 1 round, 1 inv (here we should open)
    a_0 = (c & 1) + b - 2*(c & 1)*b_0

    return a_0

def Trunc(a: int, k: int, m: int, kappa: int):
    '''
    Protocol Trunc computes floor(x / 2**m) = (x - (x mod 2**m)) * 2**(-m) for any
    x in [-2^(k-1), 2^(k-1) - 1] and 0 < m < k. Equivalent  to cutting off
    the m least significant bits of the binary representation of x

    param a:     [a] shared int\\
    params k, m: public integers
    '''

    aa = Mod2m(a, k, m, kappa)
    d = (a - aa) * ((P + 1)/2)**m # Recall that 2^-1 = (P + 1)/2

    return d

def LTZ(a: int, k: int, kappa: int):
    '''
    Less Than Zero Protocol. We compute s = (x ?< 0) for any x in [-2^(k-1), 2^(k-1) - 1]
    and return [s]

    param a: [a] shared int\\
    param k: public integer\\
    param kappa: security parameter
    '''

    s = Trunc(a, k, k - 1, kappa)

    return s

def main():
        # a = [0, 1, 1, 1, 1, 0]
        # b = [0, 0, 0, 1, 0, 1]
        # kappa = 2
        
        a = 512 - 13
        b = 13
        kappa = 2

        s1 = LTZ(a, 10, kappa)
        s2 = LTZ(b, 10, kappa)

        print(s1, ", ", s2)
        print(s1 + s2)

if __name__ == '__main__':
    main()