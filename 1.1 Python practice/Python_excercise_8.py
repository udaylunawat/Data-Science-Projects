'''
Created on 22-Jun-2019

@author: Uday
'''
#8 If all digits of a number n are multiplied by each other repeating with the product, the one
# digit number obtained at last is called the multiplicative digital root of n. The number of
# times digits need to be multiplied to reach one digit is called the multiplicative
# persistance of n.
# Example: 86 -> 48 -> 32 -> 6 (MDR 6, MPersistence 3)
#  341 -> 12->2 (MDR 2, MPersistence 2)
# Using the function prodDigits() of previous exercise write functions MDR() and
# MPersistence() that input a number and return its multiplicative digital root and
# multiplicative persistence respectively


from Python_excercise_7 import prodDigits

def MDR(n):
    z = 1
    while n>=10:
        z = prodDigits(n)
        n = z
    return z      

def MPersistence(n):
    z = 1
    flag = 0
    while n>=10:
        flag += 1
        z = prodDigits(n)
        n = z
    return flag
MDR(86)
MPersistence(86)