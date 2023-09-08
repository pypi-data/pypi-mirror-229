"""
Cianee Sumowalt
Logic and Computation
Professor McTague
1 September 2023

"""

class nth_prime:
    def __init___(self):
        self.primes = [2]

    def is_prime(self):
         for i in range(2,self.n):
            if self.n%i == 0:
                return False
         if self.n == 1:
            return False
         return True
    def next_prime(n):
        count = 0 
        num = 2
        while True:
            if n.is_prime(n):
                count +=1
                if count == n:
                    return num
            num +=1


if __name__ == "__main__":

    while True:
        user_input = int(input('> '))
        prime = nth_prime(user_input)
        print (prime.next_prime())
