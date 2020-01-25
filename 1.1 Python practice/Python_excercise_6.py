'''
Created on 22-Jun-2019

@author: Uday
'''
#6 Write a function cubesum() that accepts an integer and returns the sum of the cubes of
#individual digits of that number. Use this function to make functions PrintArmstrong() and
#isArmstrong() to print Armstrong numbers and to find whether is an Armstrong number.

def cubesum(n):
    x = str(n)
    y = 0
    for i in x:
        y += int(i)*int(i)*int(i)
    return y

def isArmstrong(n):
    if n == cubesum(n):
        return True
    return False

def PrintArmstrong():
    for i in range(100,1000):
        if isArmstrong(i):
            print(i)
 
cubesum(371)
print("Armstrong numbers between 100 and 1000 are: ") 
PrintArmstrong()