'''
Created on 22-Jun-2019

@author: Uday
'''
#7 Write a function prodDigits() that inputs a number and returns the product of digits of that number

def prodDigits(n):
    x = str(n)
    y = 1
    for i in x:
        y *= int(i)
    return y


prodDigits(123)