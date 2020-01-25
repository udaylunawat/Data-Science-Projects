'''
Created on 22-Jun-2019

@author: Uday
'''
#3 Write a program to find out the prime factors of a number. Example: prime factors of 56 - 2, 2, 2, 7
prime = [2,3,5,7,9,11,13,17,19,23]

lst = []
def pf(n):
    for i in prime:
        if n % i == 0:
            x = n/i
            lst.append(i)
            pf(x)
            return lst
    
print(pf(300))