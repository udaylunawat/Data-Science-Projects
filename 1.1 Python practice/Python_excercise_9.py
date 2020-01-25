'''
Created on 22-Jun-2019

@author: Uday
'''
#9. Write a function sumPdivisors() that finds the sum of proper divisors of a number. Proper
# divisors of a number are those numbers by which the number is divisible, except the
# number itself. For example proper divisors of 36 are 1, 2, 3, 4, 6, 9, 18


def sumPdivisors(n):
    z = []
    for i in range(n-1,0,-1):
        if n % i == 0:
            z.append(i)
    return sum(z)
sumPdivisors(36)


    