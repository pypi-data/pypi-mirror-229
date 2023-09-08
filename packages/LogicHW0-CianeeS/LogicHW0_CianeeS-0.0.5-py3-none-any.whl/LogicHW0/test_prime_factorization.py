"""
Cianee Sumowalt
Logic and Computation
Professor McTague
1 September 2023

"""

def prime_factorization(n):
    factors = []
    index = 2
    while index <= n:
        if n % index == 0:
            factors.append(index)
            n = n // index
        else:
            index += 1
    return factors

if __name__ == '__main__':
    while True:
        user_input = int(input('> '))
        print(prime_factorization(user_input))