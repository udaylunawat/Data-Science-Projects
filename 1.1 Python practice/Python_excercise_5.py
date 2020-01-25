'''
Created on 22-Jun-2019

@author: Uday
'''
#5 Write a function that converts a decimal number to binary number

def decimalToBinary(n):  
    if(n > 1): 
        decimalToBinary(n//2)  
    print(n%2, end='') 
      
      
decimalToBinary(8)

