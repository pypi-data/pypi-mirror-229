"""
Cianee Sumowalt
Logic and Computation
Professor McTague
1 September 2023

"""
    
class is_prime:

    def __init__(self,n):
        self.n = n
    def is_prime(self):
         for i in range(2,self.n):
            if self.n%i == 0:
                return False
         if self.n == 1:
            return False
         return True

if __name__ == "__main__":

    while True:
        user_input = int(input('> '))
        num = is_prime(user_input)
        print (num.is_prime())