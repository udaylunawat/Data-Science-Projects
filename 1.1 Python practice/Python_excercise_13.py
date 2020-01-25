'''
Created on 22-Jun-2019

@author: Uday
'''
#13. Write a program which can map() to make a list whose elements are cube of elements in a given list

lst = [1,2,3,4,5]
x = list(map(lambda x:(x*x*x), lst))
print(x)