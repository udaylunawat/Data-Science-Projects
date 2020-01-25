'''
Created on 22-Jun-2019

@author: Uday
'''
#1. Write a function that inputs a number and prints the multiplication table of that number

def mtable(n):
#     return  [str(n)+' * '+str(i)+' = '+str(n*i)  for i in range (1, 11)] 
    for i in range(1,11):
        print(str(n)+' * '+str(i)+' = '+str(n*i))
mtable(5)

