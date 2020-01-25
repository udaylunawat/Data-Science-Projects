'''
Created on 22-Jun-2019

@author: Uday
'''
#12. Write a program which can filter odd numbers in a list by using filter function


import numpy as np

x = np.arange(100)
x = list(x)
y = list(filter(lambda i:(i%2==1), x))
print(y)
        
        


    