def primes(limit):
    if limit < 2:
        return []
    
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\0' * len(sieve[i*i::i])
    
    return (i for i, is_prime in enumerate(sieve) if is_prime)


def is_prime(n):
    if n < 2:
        return False
    if n in {2, 3}:
        return True
    if n % 2 == 0:
        return False
        
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def prime_generator():
    yield 2
    sieve = {}
    q = 3
    
    while True:
        p = sieve.pop(q, None)
        if p is None:
            sieve[q*q] = q
            yield q
        else:
            x = q + 2*p
            while x in sieve:
                x += 2*p
            sieve[x] = p
        q += 2
