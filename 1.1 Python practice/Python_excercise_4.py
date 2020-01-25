'''
Created on 22-Jun-2019

@author: Uday
'''
#4 Write a program to implement these formulae of permutations and combinations.
#Number of permutations of n objects taken r at a time: p(n, r) = n! / (n-r)!. 
#Number of combinations of n objects taken r at a time is: c(n, r) = n! / (r!*(n-r)!) = p(n,r) / r!

def fact(n):
    x = 1
    for i in range(n,1,-1):
        x = x * i
    return x

def per(n,r):
    return (fact(n)/fact(n-r))

def com(n,r):
    return (per(n,r)/fact(r))

com(10,5)