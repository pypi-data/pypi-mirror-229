"""
Cianee Sumowalt
Logic and Computation
Professor McTague
1 September 2023

"""
    
def is_prime(n):
    for i in range(2, n):
        if n == 1:
            return False
        if n % i == 0:
            return False
    return True

if __name__ == "__main__":
    while True:
        user_input = int(input('> '))
        print(is_prime(user_input))