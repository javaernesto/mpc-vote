import math
def find_next_prime(n):
    return find_prime_in_range(n, 2*n)

def find_prime_in_range(a, b):
    for p in range(a, b):
        for i in range(2, math.floor(math.sqrt(p))+1):
            if p % i == 0:
                break
        else:
            return p
    return None
