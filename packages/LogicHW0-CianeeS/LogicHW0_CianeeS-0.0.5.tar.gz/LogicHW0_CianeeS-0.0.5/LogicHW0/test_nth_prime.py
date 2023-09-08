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

def nth_prime(n):
    count = 0
    num = 2
    while True:
        if is_prime(num):
            count += 1
            if count == n:
                return num
        num += 1

if __name__ == '__main__':
    while True:
        user_input = int(input('> '))
        print(nth_prime(user_input))