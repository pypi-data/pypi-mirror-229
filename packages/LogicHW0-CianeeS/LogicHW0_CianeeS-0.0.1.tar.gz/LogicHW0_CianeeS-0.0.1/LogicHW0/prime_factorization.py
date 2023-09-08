"""
Cianee Sumowalt
Logic and Computation
Professor McTague
1 September 2023

"""


from prime_factorization import PrimeFactorization

class PrimeFactorization:
    def __init__(self,n):
        self.n = n
    def calculate_factorization(n):
        factors = []
        index = 2
        while index <= n:
            if n % index == 0:
                factors.append(index)
                n = n // 1
            else: 
                index += 1
        return factors


if __name__ == '__main__':
    while True:
        user_input = int(input('> '))
        factors = PrimeFactorization(user_input)
        print (factors.calculate_factorization())
