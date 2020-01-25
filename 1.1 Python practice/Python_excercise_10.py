'''
Created on 22-Jun-2019

@author: Uday
'''
#10. A number is called perfect if the sum of proper divisors of that number is equal to the
# number. For example 28 is perfect number, since 1+2+4+7+14=28. Write a program to
# print all the perfect numbers in a given range

from Python_excercise_9 import sumPdivisors
def perfdiv(n):
    z = []
    for i in range(n+1):
        if sumPdivisors(i) == i:
            z.append(i)
    return z

print(perfdiv(10000))
            
        


    